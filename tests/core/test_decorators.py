import pytest

from qt_stylehelper.core.decorators import (
    require_qt,
    require_qt_for_all_methods,
    _wrap_all_methods,
)
from qt_stylehelper.core.errors import QtDependencyError
from qt_stylehelper.core.utils import QtBindingUtils


# -------------------- require_qt --------------------
def test_require_qt_available(monkeypatch):
    monkeypatch.setattr(QtBindingUtils, "is_available", lambda: True)

    @require_qt
    def example():
        return "Qt OK"

    assert example() == "Qt OK"


def test_require_qt_not_available(monkeypatch):
    monkeypatch.setattr(QtBindingUtils, "is_available", lambda: False)

    @require_qt
    def example():
        return "Qt OK"

    with pytest.raises(QtDependencyError, match="A QT module is required"):
        example()


# -------------------- require_qt_for_all_methods --------------------
def test_require_qt_for_all_methods(monkeypatch):
    monkeypatch.setattr(QtBindingUtils, "is_available", lambda: True)

    @require_qt_for_all_methods
    class Foo:
        def a(self):
            return "ok"

        def __str__(self):  # should remain untouched
            return "Foo"

    f = Foo()
    assert f.a() == "ok"
    assert str(f) == "Foo"


def test_require_qt_for_all_methods_fails(monkeypatch):
    monkeypatch.setattr(QtBindingUtils, "is_available", lambda: False)

    @require_qt_for_all_methods
    class Foo:
        def a(self):
            return "ok"

    f = Foo()
    with pytest.raises(QtDependencyError):
        f.a()


# -------------------- _wrap_all_methods (internal) --------------------
def test_wrap_all_methods_static_and_class(monkeypatch):
    monkeypatch.setattr(QtBindingUtils, "is_available", lambda: False)

    @require_qt
    def marker():
        return "wrapped"

    class Target:
        @staticmethod
        def sm():
            return "static"

        @classmethod
        def cm(cls):
            return "class"

        def normal(self):
            return "instance"

    Wrapped = _wrap_all_methods(Target, require_qt)
    w = Wrapped()

    with pytest.raises(QtDependencyError):
        w.normal()

    with pytest.raises(QtDependencyError):
        Wrapped.cm()

    with pytest.raises(QtDependencyError):
        Wrapped.sm()
