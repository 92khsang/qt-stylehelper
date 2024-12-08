import sys
from abc import ABCMeta
from functools import wraps

from .errors import QtDependencyError


def require_qt(func):
    """
    Decorator that ensures the decorated function is only executed if a QT module
    is available in the system. Specifically checks for the presence of "PySide6"
    in the loaded modules. If the module is not found, raises a QtDependencyError
    with a message indicating the need to install PySide6.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if any(module in sys.modules for module in ["PySide6"]):
            return func(*args, **kwargs)
        else:
            raise QtDependencyError("A QT module is required. Please install PySide6.")

    return wrapper


def require_qt_for_all_methods(cls):
    """
    Class decorator that applies the `require_qt` decorator to all methods
    of the class, ensuring they are only executed if a QT module is available.
    
    It wraps static methods, class methods, and callable instance methods
    with the `require_qt` decorator. Methods starting with double underscores
    are ignored.

    Args:
        cls: The class whose methods are to be decorated.

    Returns:
        The class with all applicable methods wrapped with the `require_qt` decorator.
    """
    for attr_name, attr_value in list(cls.__dict__.items()):
        if isinstance(attr_value, staticmethod):
            original_func = attr_value.__func__
            wrapped = staticmethod(require_qt(original_func))
            setattr(cls, attr_name, wrapped)
        elif isinstance(attr_value, classmethod):
            original_func = attr_value.__func__
            wrapped = classmethod(require_qt(original_func))
            setattr(cls, attr_name, wrapped)
        elif not attr_name.startswith("__") and hasattr(attr_value, "__call__"):
            wrapped = require_qt(attr_value)
            setattr(cls, attr_name, wrapped)

    return cls


def require_init(func):
    """
    Decorator that ensures the decorated function is only executed if the class
    instance has been initialized, i.e., an attribute "_init" is set to True.

    Args:
        func: The function to be decorated.

    Returns:
        A wrapper function that checks for the presence of the "_init" attribute
        and only calls the original function if the attribute is True.

    Raises:
        RuntimeError: If the decorated function is called without the class
            instance being initialized.

    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, "_init") or not self._init:
            raise RuntimeError(f"{func.__name__} cannot be called unless initialized.")
        return func(self, *args, **kwargs)

    return wrapper


def require_init_for_all_methods(cls):
    """
    A class decorator that applies the @require_init decorator to all callable
    attributes of the class and its base classes.

    The @require_init decorator ensures that the decorated function is only
    executed if the class instance has been initialized, i.e., an attribute
    "_init" is set to True.

    Args:
        cls: The class to be decorated.

    Returns:
        The decorated class.
    """
    for base_cls in cls.__mro__:
        for attr_name, attr_value in base_cls.__dict__.items():
            if attr_name.startswith("__") or isinstance(attr_value, (staticmethod, classmethod)):
                continue

            if callable(attr_value):
                setattr(cls, attr_name, require_init(attr_value))

    return cls


def override(func):
    """
    A decorator that checks if the decorated method overrides a method from one of its base classes.

    Args:
        func: The method to be decorated.

    Returns:
        A wrapper function that raises an AttributeError if the decorated method does not override a base class method.

    Raises:
        AttributeError: If the decorated method does not override a base class method.

    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not any(hasattr(base, func.__name__) for base in self.__class__.__bases__):
            raise AttributeError(
                f"{func.__name__} does not override any method in the base class."
            )
        return func(self, *args, **kwargs)

    return wrapper


class RequireInitMeta(ABCMeta):
    def __new__(cls, name, bases, dct):
        for attr_name, attr_value in dct.items():
            if (
                callable(attr_value)
                and not attr_name.startswith("__")
                and not isinstance(
                    attr_value, (staticmethod, classmethod)
                ) 
            ):
                dct[attr_name] = require_init(attr_value)
        return super().__new__(cls, name, bases, dct)
