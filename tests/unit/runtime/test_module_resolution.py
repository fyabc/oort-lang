#! /usr/bin/env python

"""Unit tests for module path resolution and default binding names."""

import pytest

from oort_lang.diagnostics.runtime_errors import OortImportError
from oort_lang.runtime.modules import derive_binding_name, resolve_module_path
from oort_lang.source.source_position import SourcePosition


def _pos() -> SourcePosition:
    return SourcePosition.from_location(1, 0, "import", filename="<test>")


def _resolve(tmp_path, spec: str, *, importer_dir=None, search_paths=()):
    entry_dir = tmp_path / "project"
    entry_dir.mkdir(exist_ok=True)
    return resolve_module_path(
        spec,
        importer_dir=entry_dir / "nested" if importer_dir is None else importer_dir,
        entry_dir=entry_dir,
        search_paths=[tmp_path / "extra", *search_paths],
        position=_pos(),
    )


def test_bare_name_uses_entry_dir_and_optional_suffix(tmp_path):
    entry_dir = tmp_path / "project"
    entry_dir.mkdir()
    target = entry_dir / "math.ort"
    target.write_text("var pi = 3\n", encoding="utf-8")

    assert _resolve(tmp_path, "math") == target.resolve()
    assert _resolve(tmp_path, "math.ort") == target.resolve()


def test_bare_name_falls_back_to_search_paths_in_order(tmp_path):
    entry_dir = tmp_path / "project"
    entry_dir.mkdir()
    extra = tmp_path / "extra"
    extra.mkdir()
    (extra / "lib.ort").write_text("var v = 1\n", encoding="utf-8")

    assert _resolve(tmp_path, "lib") == (extra / "lib.ort").resolve()

    (entry_dir / "lib.ort").write_text("var v = 2\n", encoding="utf-8")
    assert _resolve(tmp_path, "lib") == (entry_dir / "lib.ort").resolve()


def test_relative_specs_resolve_against_importer_dir(tmp_path):
    project = tmp_path / "project"
    nested = project / "nested"
    nested.mkdir(parents=True)
    sibling = nested / "sibling.ort"
    sibling.write_text("var v = 1\n", encoding="utf-8")
    parent = project / "parent.ort"
    parent.write_text("var v = 2\n", encoding="utf-8")

    assert _resolve(tmp_path, "./sibling", importer_dir=nested) == sibling.resolve()
    assert _resolve(tmp_path, "../parent.ort", importer_dir=nested) == parent.resolve()


def test_relative_spec_does_not_fall_back_to_search_paths(tmp_path):
    project = tmp_path / "project"
    nested = project / "nested"
    nested.mkdir(parents=True)
    extra = tmp_path / "extra"
    extra.mkdir()
    (extra / "sibling.ort").write_text("var v = 1\n", encoding="utf-8")

    with pytest.raises(OortImportError, match="Cannot find module"):
        _resolve(tmp_path, "./sibling", importer_dir=nested)


def test_subdirectory_bare_name(tmp_path):
    project = tmp_path / "project"
    (project / "lib").mkdir(parents=True)
    target = project / "lib" / "util.ort"
    target.write_text("var v = 1\n", encoding="utf-8")

    assert _resolve(tmp_path, "lib/util") == target.resolve()


def test_directory_module_is_rejected(tmp_path):
    project = tmp_path / "project"
    (project / "pkg.ort").mkdir(parents=True)

    with pytest.raises(OortImportError, match="Directory modules are not supported"):
        _resolve(tmp_path, "pkg")


def test_absolute_module_path_is_rejected(tmp_path):
    target = tmp_path / "math.ort"
    target.write_text("var v = 1\n", encoding="utf-8")

    with pytest.raises(OortImportError, match="Absolute module paths are not supported"):
        _resolve(tmp_path, str(target))


def test_other_extension_is_rejected(tmp_path):
    with pytest.raises(OortImportError, match=r"must use the \.ort extension"):
        _resolve(tmp_path, "math.py")


def test_empty_spec_is_rejected(tmp_path):
    with pytest.raises(OortImportError, match="cannot be empty"):
        _resolve(tmp_path, "")


def test_missing_module_lists_searched_paths(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    extra = tmp_path / "extra"

    with pytest.raises(OortImportError) as exc_info:
        _resolve(tmp_path, "missing")

    message = exc_info.value.msg
    assert "Cannot find module 'missing'" in message
    assert str(project / "missing.ort") in message
    assert str(extra / "missing.ort") in message


@pytest.mark.parametrize(
    "spec, expected",
    [
        ("math", "math"),
        ("math.ort", "math"),
        ("./sub/util.ort", "util"),
        (".\\sub\\util", "util"),
        ("lib/a_b2", "a_b2"),
    ],
)
def test_derive_binding_name(spec: str, expected: str):
    assert derive_binding_name(spec, _pos()) == expected


def test_derive_binding_name_requires_identifier():
    with pytest.raises(OortImportError, match="use 'as <name>'"):
        derive_binding_name("./foo-bar", _pos())
