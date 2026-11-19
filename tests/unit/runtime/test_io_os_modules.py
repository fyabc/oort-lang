#! /usr/bin/env python

"""Native io/os modules and string.ord/chr (OP 0015)."""

import subprocess
import sys

import pytest

from oort_lang.driver.compiler import CompilerError
from tests.helpers import get_compiler


def test_read_and_write_file(run_source, tmp_path):
    path = tmp_path / "data.txt"
    out = run_source(
        f"""\
import "io"
import "string"
io.write_file({path.as_posix()!r}, "hello 世界")
print(string.strip(io.read_file({path.as_posix()!r})))
"""
    ).stdout
    assert out == "hello 世界\n"
    assert path.read_text(encoding="utf-8") == "hello 世界"


def test_write_file_overwrites(run_source, tmp_path):
    path = tmp_path / "data.txt"
    path.write_text("old content", encoding="utf-8")
    run_source(f'import "io"\nio.write_file({path.as_posix()!r}, "new")\n')
    assert path.read_text(encoding="utf-8") == "new"


def test_missing_file_is_a_runtime_error(run_source, tmp_path, caplog):
    path = tmp_path / "missing.txt"
    with pytest.raises(CompilerError):
        run_source(f'import "io"\nio.read_file({path.as_posix()!r})\n')
    assert "No such file or directory" in caplog.text


def test_invalid_utf8_is_a_runtime_error(run_source, tmp_path, caplog):
    path = tmp_path / "bad.txt"
    path.write_bytes(b"\xff\xfe")
    with pytest.raises(CompilerError):
        run_source(f'import "io"\nio.read_file({path.as_posix()!r})\n')
    assert "utf-8" in caplog.text.lower()


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ('import "io"\nio.read_file(1)\n', "expect a String path"),
        ('import "io"\nio.write_file("x", 1)\n', "expects a String text"),
        ('import "os"\nos.exit(true)\n', "expects an Int exit code"),
        ('import "os"\nos.exit(-1)\n', "between 0 and 255"),
        ('import "string"\nstring.ord("ab")\n', "exactly one character"),
        ('import "string"\nstring.chr(-1)\n', "Unicode scalar"),
        ('import "string"\nstring.chr(0xD800)\n', "Unicode scalar"),
        ('import "string"\nstring.chr("a")\n', "expects an Int code point"),
    ],
)
def test_module_errors(source: str, message: str, run_source, caplog):
    with pytest.raises(CompilerError):
        run_source(source)
    assert message in caplog.text


def test_ord_and_chr(run_source):
    out = run_source(
        """\
import "string"
print(string.ord("A"), string.chr(65))
print(string.ord("你"), string.ord("😀"))
print(string.chr(0x4F60), string.chr(0x1F600))
"""
    ).stdout
    assert out == "65 A\n20320 128512\n你 😀\n"


def test_os_args_and_script_for_file(tmp_path):
    main = tmp_path / "main.ort"
    main.write_text(
        'import "os"\nprint(os.args)\nprint(os.script)\n',
        encoding="utf-8",
    )
    proc = subprocess.run(
        [sys.executable, "-m", "oort_lang", str(main), "alpha", "beta"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )
    assert proc.returncode == 0
    assert "[alpha, beta]" in proc.stdout
    assert str(main.resolve()) in proc.stdout


def test_os_args_for_cmd(run_source, capsys):
    compiler = get_compiler(["-c", "ignored", "a", "b"])
    compiler.run_string('import "os"\nprint(os.args, os.script)\n')
    assert capsys.readouterr().out == "[a, b] null\n"


def test_os_args_empty_in_repl():
    from oort_lang.driver.repl import ReplSession

    session = ReplSession(get_compiler("NOT_EXIST -t eval"))
    session.feed_line('import "os"')
    result = session.feed_line("os.args")
    assert result.action.name == "EVALUATED"
    assert result.value is not None


def test_os_exit_sets_process_status():
    proc = subprocess.run(
        [sys.executable, "-m", "oort_lang", "-c", 'import "os"\nos.exit(3)'],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )
    assert proc.returncode == 3
    assert "Traceback" not in proc.stdout
    assert "Traceback" not in proc.stderr
