#! /usr/bin/env python

"""Build lexer / parser / visitor files from grammar."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).absolute().parent.parent
GRAMMAR_FILE_DIR = PROJECT_ROOT / "grammars"
GRAMMAR_FILENAME = GRAMMAR_FILE_DIR / "Oort.g4"
GENERATED_DIR = PROJECT_ROOT / "src" / "oort_lang" / "parser" / "grammar"

_JAVA_EXECUTABLES = ("java.exe", "java")


def _java_bin_dir(java_home: str) -> Path | None:
    bin_dir = Path(java_home) / "bin"
    if any((bin_dir / exe).exists() for exe in _JAVA_EXECUTABLES):
        return bin_dir
    return None


def _build_env() -> dict[str, str]:
    """Build an environment where JAVA_HOME/bin (if valid) comes first."""
    env = os.environ.copy()
    java_home = env.get("JAVA_HOME")
    if java_home and (bin_dir := _java_bin_dir(java_home)):
        env["PATH"] = str(bin_dir) + os.pathsep + env.get("PATH", "")
    return env


def _is_working_java(executable: str, env: dict[str, str]) -> bool:
    """Return True if the executable can actually start and print a version."""
    try:
        subprocess.run([executable, "-version"], check=True, env=env, capture_output=True)
    except (OSError, subprocess.CalledProcessError):
        return False
    return True


def _find_java(env: dict[str, str]) -> str | None:
    """Find a working java executable.

    Resolution order: PATH (which may already include JAVA_HOME/bin), then a
    few common JDK installation directories. Candidates are executed, so a
    broken shim earlier in PATH (e.g. a stale Oracle javapath) is skipped
    instead of aborting the build.
    """
    candidates: list[str] = []
    java = shutil.which("java", path=env.get("PATH", ""))
    if java:
        candidates.append(java)

    search_roots = [
        Path("C:/Program Files/Java"),
        Path("C:/Program Files/Eclipse Adoptium"),
        Path("C:/Program Files/Microsoft"),
    ]
    for root in search_roots:
        if not root.is_dir():
            continue
        for candidate in sorted(root.glob("jdk*"), reverse=True):
            if bin_dir := _java_bin_dir(str(candidate)):
                for exe in _JAVA_EXECUTABLES:
                    if (bin_dir / exe).exists():
                        candidates.append(str(bin_dir / exe))

    for candidate in candidates:
        if _is_working_java(candidate, env):
            return candidate
    return None


def main() -> None:
    env = _build_env()

    java = _find_java(env)
    if java is None:
        sys.exit("Error: no working Java executable found. Install JDK 17+ and set JAVA_HOME.")
    # Make the antlr4 wrapper use the same Java we verified above.
    env["PATH"] = str(Path(java).parent) + os.pathsep + env.get("PATH", "")
    try:
        subprocess.run([java, "-version"], check=True, env=env, capture_output=True)
    except (OSError, subprocess.CalledProcessError) as e:
        sys.exit(f"Error: Java executable {java!r} cannot run: {e}")

    antlr4 = shutil.which("antlr4", path=env.get("PATH", ""))
    if antlr4 is None:
        sys.exit("Error: antlr4 not found. Run `uv sync --extra build-grammar` first.")

    command = [
        antlr4,
        "-encoding",
        "UTF-8",
        "-visitor",
        "-no-listener",
        "-Dlanguage=Python3",
        "-o",
        os.path.relpath(GENERATED_DIR, GRAMMAR_FILE_DIR),
        "-lib",
        ".",
        GRAMMAR_FILENAME.name,
    ]
    # Run from grammars/ with a bare grammar filename so generated headers do
    # not embed the author's absolute filesystem paths.
    subprocess.run(command, check=True, env=env, cwd=GRAMMAR_FILE_DIR)

    # ANTLR leaves trailing spaces on many generated lines; keep the tracked
    # generated sources clean so `git diff --check` stays useful.
    for generated in GENERATED_DIR.glob("*.py"):
        text = generated.read_text(encoding="utf-8")
        cleaned = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
        if cleaned != text:
            generated.write_text(cleaned, encoding="utf-8")


if __name__ == "__main__":
    main()
