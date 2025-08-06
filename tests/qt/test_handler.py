# test_qt_handler.py

import importlib
import logging
import sys

import pytest

from qt_stylehelper import Theme
from qt_stylehelper.core.utils import QtBindingUtils
from qt_stylehelper.qt import handler
from qt_stylehelper.qt.handler import QtHandler


@pytest.fixture
def theme():
    return Theme(
        primary_color="#FF0000",
        primary_light_color="#FF6666",
        secondary_color="#00FF00",
        secondary_light_color="#66FF66",
        secondary_dark_color="#003300",
        primary_text_color="#000000",
        secondary_text_color="#888888",
    )


@pytest.mark.qt
def test_add_fonts(monkeypatch, tmp_path):
    font_file = tmp_path / "A.ttf"
    font_file.write_text("dummy")

    class DummyFontDB:
        called = []

        @staticmethod
        def addApplicationFont(path):
            DummyFontDB.called.append(path)
            return 1

    monkeypatch.setattr(handler, "QFontDatabase", DummyFontDB)
    QtHandler.add_fonts(str(tmp_path))

    assert len(DummyFontDB.called) == 1
    assert DummyFontDB.called[0] == str(font_file)


@pytest.mark.qt
def test_add_fonts_attribute_error(monkeypatch, tmp_path):
    font_file = tmp_path / "B.ttf"
    font_file.write_text("dummy")

    class DummyFontDB:
        called = []

        @staticmethod
        def addApplicationFont(path):
            raise AttributeError("mocked missing method")

        @staticmethod
        def add_application_font(path):
            DummyFontDB.called.append(path)
            return 1

    monkeypatch.setattr(handler, "QFontDatabase", DummyFontDB)
    QtHandler.add_fonts(str(tmp_path))

    assert DummyFontDB.called[0] == font_file


@pytest.mark.qt
def test_add_fonts_general_exception(monkeypatch, tmp_path, caplog):
    font_file = tmp_path / "C.ttf"
    font_file.write_text("dummy")

    class DummyFontDB:
        @staticmethod
        def addApplicationFont(path):
            raise RuntimeError("intentional fail")

    caplog.set_level(logging.ERROR)
    monkeypatch.setattr(handler, "QFontDatabase", DummyFontDB)
    QtHandler.add_fonts(str(tmp_path))

    assert "Error loading font" in caplog.text


@pytest.mark.qt
def test_add_fonts_failure_result(monkeypatch, tmp_path, caplog):
    font_file = tmp_path / "D.ttf"
    font_file.write_text("dummy")

    class DummyFontDB:
        @staticmethod
        def addApplicationFont(path):
            return -1

    caplog.set_level(logging.DEBUG)
    monkeypatch.setattr(handler, "QFontDatabase", DummyFontDB)
    QtHandler.add_fonts(str(tmp_path))

    assert "Failed to load font" in caplog.text


@pytest.mark.qt
def test_add_fonts_invalid_dir(caplog):
    QtHandler.add_fonts("/non/existing/path")
    assert "does not exist" in caplog.text


@pytest.mark.qt
def test_apply_stylesheet(qtbot):
    from PySide6.QtWidgets import QWidget

    widget = QWidget()
    qtbot.addWidget(widget)

    stylesheet = "QWidget { background-color: red; }"
    QtHandler.apply_stylesheet(widget, stylesheet)

    assert widget.styleSheet() == stylesheet


@pytest.mark.qt
def test_apply_stylesheet_invalid_target(caplog):
    dummy = object()
    QtHandler.apply_stylesheet(dummy, "invalid")
    assert "does not support setStyleSheet" in caplog.text


@pytest.mark.qt
def test_apply_stylesheet_attribute_error(monkeypatch, caplog):
    class DummyApp:
        def setStyleSheet(self, style):
            raise AttributeError("fake attr error")

    app = DummyApp()
    style_sheet = "QWidget { color: red; }"
    caplog.set_level(logging.DEBUG)

    QtHandler.apply_stylesheet(app, style_sheet)

    assert app.styleSheet == "QWidget { color: red; }"


@pytest.mark.qt
def test_apply_stylesheet_general_exception(monkeypatch, caplog):
    class DummyApp:
        def setStyleSheet(self, style):
            raise RuntimeError("boom!")

    app = DummyApp()
    caplog.set_level(logging.ERROR)

    QtHandler.apply_stylesheet(app, "QWidget { color: blue; }")

    assert "Failed to apply stylesheet" in caplog.text


@pytest.mark.qt
def test_add_search_paths(monkeypatch, tmp_path):
    path = tmp_path / "icons"
    path.mkdir()

    set_args = []
    add_args = []

    class DummyDirDB:
        @staticmethod
        def setSearchPaths(*args):
            set_args.append(args)

        @staticmethod
        def addSearchPath(*args):
            add_args.append(args)

    monkeypatch.setattr(handler, "QDir", DummyDirDB)
    QtHandler.add_search_paths(str(path), "prefix")

    assert set_args[0] == ("prefix", [])
    assert add_args[0] == ("prefix", str(path))


@pytest.mark.qt
def test_add_search_paths_attribute_error(monkeypatch, tmp_path):
    path = tmp_path / "icons"
    path.mkdir()

    set_args = []
    add_args = []

    class DummyDirDB:
        @staticmethod
        def setSearchPaths(*args):
            raise AttributeError("fake attr error")

        @staticmethod
        def set_search_paths(*args):
            set_args.append(args)

        @staticmethod
        def add_search_path(*args):
            add_args.append(args)

    monkeypatch.setattr(handler, "QDir", DummyDirDB)
    QtHandler.add_search_paths(str(path), "prefix")

    assert set_args[0] == ("prefix", [])
    assert add_args[0] == ("prefix", str(path))


@pytest.mark.qt
def test_apply_palette(monkeypatch, qtbot, theme):
    from PySide6.QtGui import QGuiApplication, QPalette

    palette = QGuiApplication.palette()
    old_color = palette.color(QPalette.ColorRole.PlaceholderText)

    QtHandler.apply_palette(theme)
    qtbot.wait(50)

    new_color = QGuiApplication.palette().color(QPalette.ColorRole.PlaceholderText)
    assert new_color != old_color


@pytest.mark.qt
def test_apply_palette_generic_exception(monkeypatch, caplog, theme):
    class ExplodingPalette:
        def setColor(self, *args):
            raise RuntimeError("unexpected failure")

    from qt_stylehelper.qt.handler import QGuiApplication

    monkeypatch.setattr(QGuiApplication, "palette", lambda: ExplodingPalette())
    monkeypatch.setattr(QGuiApplication, "setPalette", lambda p: None)

    QtHandler.apply_palette(theme)

    assert "Failed to apply palette" in caplog.text


@pytest.fixture
def reloaded_handler_with_qt_disabled(monkeypatch):
    monkeypatch.setattr(QtBindingUtils, "is_available", lambda: False)

    if "qt_stylehelper.qt.handler" in sys.modules:
        del sys.modules["qt_stylehelper.qt.handler"]

    import qt_stylehelper.qt.handler as fake_handler

    return importlib.reload(fake_handler)


def test_handler_warns_all_methods(caplog, reloaded_handler_with_qt_disabled):
    fake_handler = reloaded_handler_with_qt_disabled.QtHandler

    caplog.clear()
    fake_handler.add_fonts("fake_path")
    assert (
        "[QtStyleHelper] 'add_fonts()' called but PySide6 is not installed."
        in caplog.text
    )

    caplog.clear()
    fake_handler.apply_stylesheet(None, "")
    assert (
        "[QtStyleHelper] 'apply_stylesheet()' called but PySide6 is not installed."
        in caplog.text
    )

    caplog.clear()
    fake_handler.add_search_paths("fake_resource")
    assert (
        "[QtStyleHelper] 'add_search_paths()' called but PySide6 is not installed."
        in caplog.text
    )

    caplog.clear()
    fake_handler.apply_palette(None)
    assert (
        "[QtStyleHelper] 'apply_palette()' called but PySide6 is not installed."
        in caplog.text
    )
