import pytest

from qt_stylehelper.tools.static.structs import StaticThemeStruct


@pytest.fixture
def theme_dir(tmp_path):
    return tmp_path / "my_theme"


@pytest.fixture
def theme_file(tmp_path):
    path = tmp_path / "theme.json"
    path.write_text("{}")
    return path


def test_static_theme_struct_default_name(theme_dir, theme_file):
    theme_dir.mkdir()
    struct = StaticThemeStruct(theme=theme_file, theme_dir=theme_dir)
    assert struct.theme_name == "my_theme"


def test_replace_theme_changes_when_different(theme_dir, theme_file):
    new_path = theme_file.parent / "other_theme.json"
    new_path.write_text("{}")
    struct = StaticThemeStruct(theme=theme_file, theme_dir=theme_dir)
    updated = struct.replace_theme(new_path)
    assert updated.theme == new_path
    assert updated != struct


def test_replace_theme_no_change(theme_dir, theme_file):
    struct = StaticThemeStruct(theme=theme_file, theme_dir=theme_dir)
    updated = struct.replace_theme(theme_file)
    assert updated == struct


def test_replace_qss_files_changes_when_different(theme_dir, theme_file):
    qss_path = theme_file.parent / "style.qss"
    qss_path.write_text("body {}")
    struct = StaticThemeStruct(theme=theme_file, theme_dir=theme_dir)
    updated = struct.replace_qss_files([qss_path])
    assert updated.qss_files == [qss_path]
    assert updated != struct


def test_replace_qss_files_no_change(theme_dir, theme_file):
    struct = StaticThemeStruct(theme=theme_file, theme_dir=theme_dir, qss_files=[])
    updated = struct.replace_qss_files([])
    assert updated == struct
