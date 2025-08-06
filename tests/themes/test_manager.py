import json
import tempfile
from pathlib import Path

import pytest

from qt_stylehelper.core.utils import ValidateUtils, ResourcePathUtils
from qt_stylehelper.themes.manager import ThemeManager
from qt_stylehelper.themes.models import Theme


def create_temp_theme_file(directory: Path, name: str, theme_dict: dict) -> Path:
    file_path = directory / f"{name}.json"
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(theme_dict, f)
    return file_path


def create_non_json_file(directory: Path, name: str) -> Path:
    file_path = directory / f"{name}.txt"
    file_path.write_text("not a json")
    return file_path


valid_theme_data = {
    "primary_color": "#000000",
    "primary_light_color": "#111111",
    "secondary_color": "#222222",
    "secondary_light_color": "#333333",
    "secondary_dark_color": "#444444",
    "primary_text_color": "#555555",
    "secondary_text_color": "#666666",
    "active_color": "#777777",
}


# -------------------- ThemeManager Core --------------------
def test_add_themes_from_dir_and_list():
    with tempfile.TemporaryDirectory() as tmpdir:
        dir_path = Path(tmpdir)
        create_temp_theme_file(dir_path, "dark", valid_theme_data)
        create_temp_theme_file(dir_path, "light", valid_theme_data)

        manager = ThemeManager(include_builtin=False)
        manager.add_themes_from_dir(dir_path)
        themes = manager.get_theme_list()
        assert len(themes) == 2
        assert any("dark.json" in str(p) for p in themes)


def test_add_theme_from_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        dir_path = Path(tmpdir)
        file_path = create_temp_theme_file(dir_path, "test", valid_theme_data)

        manager = ThemeManager(include_builtin=False)
        manager.add_theme_from_file(file_path)
        assert len(manager.get_theme_list()) == 1


def test_add_theme_from_file_invalid_type():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = create_non_json_file(Path(tmpdir), "invalid")
        manager = ThemeManager(include_builtin=False)
        with pytest.raises(ValueError):
            manager.add_theme_from_file(path)


def test_load_theme():
    with tempfile.TemporaryDirectory() as tmpdir:
        dir_path = Path(tmpdir)
        file_path = create_temp_theme_file(dir_path, "custom", valid_theme_data)

        manager = ThemeManager(include_builtin=False)
        manager.add_theme_from_file(file_path)
        theme = manager.load_theme("custom")
        assert isinstance(theme, Theme)
        assert theme.primary_color == "#000000"


def test_load_invalid_theme_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "invalid.json"
        path.write_text("not a json")

        manager = ThemeManager(include_builtin=False)
        manager.add_theme_from_file(path)
        assert manager.load_theme("invalid") is None


def test_load_theme_missing_file():
    manager = ThemeManager(include_builtin=False)
    assert manager.load_theme("does_not_exist") is None


def test_load_theme_fallback(monkeypatch):
    # If not found, fallback should attempt built-in (mocked)
    monkeypatch.setattr(
        ResourcePathUtils,
        "themes_dir",
        lambda: Path("/nonexistent"),
    )
    monkeypatch.setattr(
        ValidateUtils,
        "ensure_directory_exists",
        lambda path: None,
    )

    assert ThemeManager().load_theme("nonexistent") is None


def test_load_builtin_theme(monkeypatch):
    theme = ThemeManager.load_builtin_theme("dark_amber").to_dict(camel_case=True)
    del theme["activeColor"]

    dark_amber_json_dict = {
        "primaryColor": "#ffd740",
        "primaryLightColor": "#ffff74",
        "secondaryColor": "#232629",
        "secondaryLightColor": "#4f5b62",
        "secondaryDarkColor": "#31363b",
        "primaryTextColor": "#ffffff",
        "secondaryTextColor": "#ffffff",
    }

    assert theme == dark_amber_json_dict


def test_load_builtin_theme_not_found(monkeypatch):
    monkeypatch.setattr(
        ResourcePathUtils,
        "themes_dir",
        lambda: Path("/nonexistent"),
    )
    assert ThemeManager.load_builtin_theme("nope") is None


def test_get_builtin_theme_list():
    paths = ThemeManager.get_builtin_theme_list()
    assert isinstance(paths, list)
    for p in paths:
        assert p.suffix == ".json"


def test__load_theme_from_file_with_type_error(tmp_path):
    theme_file = tmp_path / "bad.json"
    theme_file.write_text("[]")  # not a dict
    result = ThemeManager._load_theme_from_file(theme_file)
    assert result is None


def test__load_theme_from_file_invalid_json(tmp_path):
    theme_file = tmp_path / "bad.json"
    theme_file.write_text("{ invalid json }")
    result = ThemeManager._load_theme_from_file(theme_file)
    assert result is None
