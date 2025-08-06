from pathlib import Path
from unittest.mock import MagicMock

import pytest

from qt_stylehelper.themes.models import Theme, ExtraAttribute
from qt_stylehelper.tools.dynamic import DynamicQtStyleTool


@pytest.fixture
def sample_theme() -> Theme:
    return Theme(
        primary_color="#111111",
        primary_light_color="#222222",
        secondary_color="#333333",
        secondary_light_color="#444444",
        secondary_dark_color="#555555",
        primary_text_color="#666666",
        secondary_text_color="#777777",
        active_color="#888888",
    )


def test_update_extra_attribute_dict():
    tool = DynamicQtStyleTool()
    tool.update_extra_attribute({"density_scale": 2.0})
    assert tool._extra.values["density_scale"] == 2.0


def test_update_extra_attribute_obj():
    tool = DynamicQtStyleTool()
    original = ExtraAttribute().with_updated_values({"density_scale": 1.5})
    tool.update_extra_attribute(original)
    assert tool._extra.values["density_scale"] == 1.5


def test_update_extra_attribute_none():
    tool = DynamicQtStyleTool()
    prev = tool._extra
    tool.update_extra_attribute(None)
    assert tool._extra == prev


def test_add_theme_file(tmp_path):
    theme_file = tmp_path / "dark.json"
    theme_file.write_text("{}")
    tool = DynamicQtStyleTool()
    tool.add_theme(theme_file)
    assert "dark" in tool.get_theme_list()


def test_add_theme_dir(tmp_path):
    (tmp_path / "light.json").write_text("{}")
    tool = DynamicQtStyleTool()
    tool.add_theme(tmp_path)
    assert "light" in tool.get_theme_list()


def test_add_theme_invalid_path():
    tool = DynamicQtStyleTool()
    with pytest.raises(ValueError):
        tool.add_theme("/invalid/path")


def test_get_theme_object_calls_manager():
    tool = DynamicQtStyleTool()
    tool._theme_manager.load_theme = MagicMock(return_value="fake_theme")
    result = tool._get_theme_object("dark")
    assert result == "fake_theme"


def test_get_stylesheet_calls_generator_renderer(sample_theme):
    tool = DynamicQtStyleTool()
    tool._get_theme_object = MagicMock(return_value=sample_theme)
    tool._icon_generator.generate_dynamically = MagicMock()
    tool._style_renderer.render = MagicMock(return_value="qss-content")

    result = tool._get_stylesheet("dark")
    assert result == "qss-content"
    tool._icon_generator.generate_dynamically.assert_called_once_with(
        sample_theme, tool._app_name
    )
    tool._style_renderer.render.assert_called_once_with(sample_theme, tool._extra)


def test_get_icons_dir_returns_path():
    tool = DynamicQtStyleTool()
    tool._icon_generator.get_dynamic_icons_dir = MagicMock(
        return_value=Path("/mock/icons")
    )
    result = tool._get_icons_dir("any")
    assert result == "/mock/icons"
