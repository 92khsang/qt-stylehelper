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
    A class decorator that applies the `require_init` decorator to all callable
    attributes of a class, including static methods and class methods.

    This decorator walks the MRO of the class and applies the `require_init`
    decorator to all callable attributes that are not special methods (i.e.,
    methods with names that start with double underscore).

    Args:
        cls: The class to be decorated.

    Returns:
        The decorated class.

    """
    for base_cls in cls.__mro__:
        for attr_name, attr_value in base_cls.__dict__.items():
            print(f"Processing {attr_name}: {type(attr_value)}")  # Debugging output

            if attr_name.startswith("__"):
                continue

            if isinstance(attr_value, staticmethod):
                print(f"Wrapping staticmethod: {attr_name}")
                original_func = attr_value.__func__
                setattr(cls, attr_name, staticmethod(require_init(original_func)))
            elif isinstance(attr_value, classmethod):
                print(f"Wrapping classmethod: {attr_name}")
                original_func = attr_value.__func__
                setattr(cls, attr_name, classmethod(require_init(original_func)))
            elif callable(attr_value):
                print(f"Wrapping instance method: {attr_name}")
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
        # Wrap all methods with `require_init`
        for attr_name, attr_value in dct.items():
            if (
                callable(attr_value)  # Only target callable attributes
                and not attr_name.startswith("__")  # Skip special methods
                and not isinstance(
                    attr_value, (staticmethod, classmethod)
                )  # Skip static/class methods
            ):
                dct[attr_name] = require_init(attr_value)
        # Create the class using ABCMeta's logic
        return super().__new__(cls, name, bases, dct)
