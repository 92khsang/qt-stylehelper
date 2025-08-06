from functools import wraps
from types import FunctionType
from typing import Callable, Type, cast, TypeVar

from qt_stylehelper.core.errors import QtDependencyError
from qt_stylehelper.core.utils import QtBindingUtils

T = TypeVar("T")

# ─────────────────────────────────────────────────────────────
# Individual decorators
# ─────────────────────────────────────────────────────────────


def require_qt(func: Callable) -> Callable:
    """
    Ensures the function is only executed if PySide6 is available.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if QtBindingUtils.is_available():
            return func(*args, **kwargs)
        raise QtDependencyError("A QT module is required. Please install PySide6.")

    return wrapper


# ─────────────────────────────────────────────────────────────
# Class-level decorators
# ─────────────────────────────────────────────────────────────


def require_qt_for_all_methods(cls: Type[T]) -> Type[T]:
    """
    Applies `@require_qt` to all methods (except dunder, static/classmethods).
    """
    return cast(Type[T], _wrap_all_methods(cls, require_qt))


def _wrap_all_methods(
    cls: Type[T], decorator: Callable[[Callable], Callable]
) -> Type[T]:
    """
    Helper that wraps all instance methods of a class with the given decorator.
    """
    for attr_name, attr_value in dict(cls.__dict__).items():
        if attr_name.startswith("__"):
            continue

        if isinstance(attr_value, staticmethod):
            wrapped = staticmethod(decorator(attr_value.__func__))
        elif isinstance(attr_value, classmethod):
            wrapped = classmethod(decorator(attr_value.__func__))
        elif isinstance(attr_value, FunctionType):
            wrapped = decorator(attr_value)
        else:
            continue

        setattr(cls, attr_name, wrapped)

    return cls
