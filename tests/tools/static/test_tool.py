import json

import pytest

from qt_stylehelper.themes.icon import ICON_CONTEXT
from qt_stylehelper.tools.static.tool import StaticQtStyleTool


@pytest.fixture
def theme_dir(tmp_path):
    theme_path = tmp_path / "my_theme"
    theme_path.mkdir()

    for context in ICON_CONTEXT:
        context_dir = theme_path / context
        context_dir.mkdir(exist_ok=True, parents=True)

    # Write QSS file
    qss_file = theme_path / "style.qss"
    qss_file.write_text(
        """/* Copyright */\n/* Line 2 */\n/* Line 3 */\n/* Line 4 */\nbody { background-color: #123456; color: #654321; }"""
    )

    # Write theme JSON
    theme_json = theme_path / "my_theme.json"
    theme_json.write_text(
        json.dumps(
            {
                "primaryColor": "#123456",
                "primaryLightColor": "#123456",
                "secondaryColor": "#123456",
                "secondaryLightColor": "#123456",
                "secondaryDarkColor": "#123456",
                "primaryTextColor": "#654321",
                "secondaryTextColor": "#654321",
                "activeColor": "#abcdef",
            }
        )
    )

    return theme_path


@pytest.fixture
def resource_path_utils(monkeypatch, theme_dir):
    from qt_stylehelper.core.utils import ResourcePathUtils

    monkeypatch.setattr(
        ResourcePathUtils,
        "template_file",
        staticmethod(lambda: theme_dir / "style.qss"),
    )

    return ResourcePathUtils


def test_add_theme_registers_theme(monkeypatch, theme_dir, resource_path_utils):
    from qt_stylehelper.themes.icon import BuiltInIconDirValidator

    monkeypatch.setattr(BuiltInIconDirValidator, "validate", lambda _: None)

    tool = StaticQtStyleTool()

    tool.add_theme(theme_dir)

    assert tool.get_theme_list() == ["my_theme"]
    assert tool._get_theme_object("my_theme").primary_color == "#123456"
    assert tool._get_icons_dir("my_theme") == str(theme_dir)
    assert "background-color" in tool._get_stylesheet("my_theme")


def test_add_theme_invalid_dir():
    tool = StaticQtStyleTool()
    with pytest.raises(ValueError):
        tool.add_theme("not_a_dir")


def test_missing_qss_file(tmp_path):
    theme_dir = tmp_path / "empty_theme"
    theme_dir.mkdir()
    json_path = theme_dir / "empty_theme.json"
    json_path.write_text("{}")

    tool = StaticQtStyleTool()
    with pytest.raises(ValueError, match="No QSS files found"):
        tool.add_theme(theme_dir)


def test_missing_theme_json(tmp_path):
    theme_dir = tmp_path / "broken_theme"
    theme_dir.mkdir()
    (theme_dir / "style.qss").write_text("/* dummy */")

    tool = StaticQtStyleTool()
    with pytest.raises(ValueError, match="Theme JSON file not found"):
        tool.add_theme(theme_dir)
