import platform
import tempfile
from pathlib import Path

import pytest

from qt_stylehelper.core.utils import (
    PlatformUtils,
    ValidateUtils,
    QtBindingUtils,
    ResourcePathUtils,
)


# -------------------- ValidateUtils --------------------
def test_is_valid_filename():
    assert ValidateUtils.is_valid_filename("valid_name")
    assert not ValidateUtils.is_valid_filename("in:valid")
    assert not ValidateUtils.is_valid_filename("name*")
    assert not ValidateUtils.is_valid_filename("<bad>")


def test_is_valid_hex_color():
    assert ValidateUtils.is_valid_hex_color("#FFFFFF")
    assert ValidateUtils.is_valid_hex_color("#abcdef")
    assert not ValidateUtils.is_valid_hex_color("123456")
    assert not ValidateUtils.is_valid_hex_color("#12345G")


def test_ensure_directory_exists():
    with tempfile.TemporaryDirectory() as tmp:
        ValidateUtils.ensure_directory_exists(Path(tmp))
    with pytest.raises(FileNotFoundError):
        ValidateUtils.ensure_directory_exists(Path("/nonexistent/dir"))


# -------------------- PlatformUtils --------------------
def test_get_app_data_dir_valid():
    name = "MyApp"
    path = PlatformUtils.get_app_data_dir(name)
    assert name in str(path)
    assert isinstance(path, Path)


def test_get_app_data_dir_invalid():
    with pytest.raises(ValueError):
        PlatformUtils.get_app_data_dir("bad:name")


def test_get_app_data_dir_platform_behavior(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    assert ".local/share" in str(PlatformUtils.get_app_data_dir("App"))

    monkeypatch.setattr(platform, "system", lambda: "Darwin")
    assert "Application Support" in str(PlatformUtils.get_app_data_dir("App"))

    monkeypatch.setattr(platform, "system", lambda: "Windows")
    assert "AppData" in str(PlatformUtils.get_app_data_dir("App"))

    monkeypatch.setattr(platform, "system", lambda: "Unknown")
    with pytest.raises(NotImplementedError):
        PlatformUtils.get_app_data_dir("App")


# -------------------- QtBindingUtils --------------------
def test_qt_binding_detection():
    assert isinstance(QtBindingUtils.is_available(), bool)
    assert QtBindingUtils.get_backend() in ("PySide6", None)


# -------------------- ResourcePathUtils --------------------
def test_resource_path_utils():
    path = ResourcePathUtils.themes_dir()
    assert path.exists()
    assert path.is_dir()

    path = ResourcePathUtils.icons_dir()
    assert path.exists()
    assert path.is_dir()

    path = ResourcePathUtils.template_file()
    assert path.exists()
    assert path.is_file()

    ResourcePathUtils.clear_cache()  # Just to make sure it doesn't raise
    assert callable(ResourcePathUtils.base_dir)


# Optional: Mark slow if accessing large resources
@pytest.mark.slow
def test_clear_cache_effect():
    ResourcePathUtils.clear_cache()
    _ = ResourcePathUtils.themes_dir()
