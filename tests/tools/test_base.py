from unittest.mock import Mock, patch

import pytest

from qt_stylehelper.tools.base import QtStyleTool


class DummyStyleTool(QtStyleTool):
    def __init__(self):
        super().__init__()
        self._themes = {"default": "", "dark": "some.qss"}

    def add_theme(self, path):
        self._themes["custom"] = str(path)

    def get_theme_list(self):
        return list(self._themes.keys())

    def _get_theme_object(self, theme_name):
        return Mock(name="Theme")

    def _get_stylesheet(self, theme_name):
        return f"{theme_name}-style"

    def _get_icons_dir(self, theme_name):
        return f"/fake/path/{theme_name}/icons"


def test_current_theme_property():
    tool = DummyStyleTool()
    assert tool.current_theme_name == "default"


def test_apply_stylesheet_changes_theme(monkeypatch):
    tool = DummyStyleTool()
    widget = Mock()

    from qt_stylehelper.tools.base import QtHandler

    with (
        patch.object(QtHandler, "apply_stylesheet") as mock_apply,
        patch.object(QtHandler, "apply_palette") as mock_palette,
        patch.object(QtHandler, "add_search_paths") as mock_add,
    ):

        tool.apply_stylesheet(widget, "dark")

        assert tool.current_theme_name == "dark"
        mock_add.assert_called_once()
        mock_palette.assert_called_once()
        mock_apply.assert_called_once()


def test_apply_stylesheet_with_same_theme_noop():
    tool = DummyStyleTool()
    tool._current_theme = "no-default"
    widget = Mock()

    from qt_stylehelper.tools.base import QtHandler

    with patch.object(QtHandler, "apply_stylesheet") as mock_apply:
        tool.apply_stylesheet(widget, "default")
        mock_apply.assert_called_once_with(widget, "")


def test_apply_stylesheet_invalid_theme():
    tool = DummyStyleTool()
    widget = Mock()

    with pytest.raises(ValueError, match="not found"):
        tool.apply_stylesheet(widget, "not_exist")


def test_refresh_stylesheet_when_not_default(monkeypatch):
    tool = DummyStyleTool()
    widget = Mock()
    tool._current_theme = "dark"
    from qt_stylehelper.tools.base import QtHandler

    with (
        patch.object(QtHandler, "apply_stylesheet") as mock_apply,
        patch.object(QtHandler, "apply_palette") as mock_palette,
        patch.object(QtHandler, "add_search_paths") as mock_add,
    ):

        tool.refresh_stylesheet(widget)

        mock_apply.assert_called_once()
        mock_palette.assert_called_once()
        mock_add.assert_called_once()


def test_refresh_stylesheet_default_noop():
    tool = DummyStyleTool()
    widget = Mock()

    from qt_stylehelper.tools.base import QtHandler

    with patch.object(QtHandler, "apply_stylesheet") as mock_apply:
        tool.refresh_stylesheet(widget)
        mock_apply.assert_not_called()


def test_update_resource_prefix(monkeypatch):
    from qt_stylehelper.tools.base import QtHandler

    with patch.object(QtHandler, "add_search_paths") as mock_add:
        tool = DummyStyleTool()
        tool.update_resource_prefix("/some/path", "prefix")
        mock_add.assert_called_once_with("/some/path", "prefix")
