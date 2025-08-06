import logging
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, List, Any, Union

from qt_stylehelper.core.decorators import require_qt_for_all_methods
from qt_stylehelper.core.utils import QtBindingUtils
from qt_stylehelper.qt.handler import QtHandler

if TYPE_CHECKING:
    if "PySide6" == QtBindingUtils.get_backend():
        from PySide6.QtWidgets import QWidget
    else:
        logging.warning(
            "If you intend to use code related to Qt, the corresponding Qt libraries are required."
        )

        QWidget = Any

    from qt_stylehelper.themes.models import Theme


@require_qt_for_all_methods
class QtStyleTool(metaclass=ABCMeta):
    def __init__(self) -> None:
        self._current_theme = "default"

    @property
    def current_theme_name(self) -> str:
        return self._current_theme

    def apply_stylesheet(self, widget: "QWidget", theme_name: str) -> None:
        """
        Applies a stylesheet to the given widget.

        Args:
            widget (QWidget): The widget to apply the stylesheet to.
            theme_name (str): The name of the theme to apply.

        Raises:
            ValueError: If the widget is not a valid QWidget instance.
            ValueError: If the theme_name is not found.
        """
        if theme_name not in self.get_theme_list():
            raise ValueError(f"Theme '{theme_name}' not found.")

        if self._current_theme == theme_name:
            return

        if theme_name == "default":
            self._apply_default(widget)
        else:
            self._apply_theme(widget, theme_name)

        self._current_theme = theme_name

    def refresh_stylesheet(self, widget: "QWidget") -> None:
        """
        Refreshes the stylesheet of the given widget to the current theme.

        Args:
            widget (QWidget): The widget to refresh the stylesheet for.
        """
        if self._current_theme == "default":
            return

        self._apply_theme(widget, self._current_theme)

    def update_resource_prefix(self, resource_dir: str, prefix: str) -> None:
        """
        Adds a resource directory and prefix to the list of directories
        searched for theme resources.

        Args:
            resource_dir (str): The directory to search for resources.
            prefix (str): The prefix to use for the resources.

        Raises:
            ValueError: If the resource directory or prefix is empty.
        """
        QtHandler.add_search_paths(resource_dir, prefix)

    def _apply_theme(self, widget: "QWidget", theme_name: str) -> None:
        stylesheet = self._get_stylesheet(theme_name)
        QtHandler.add_search_paths(resource_dir=self._get_icons_dir(theme_name))
        QtHandler.apply_palette(self._get_theme_object(theme_name))
        QtHandler.apply_stylesheet(widget, stylesheet)

    def _apply_default(self, widget: "QWidget") -> None:
        """
        Applies the default stylesheet to the given widget.

        Args:
            widget (QWidget): The widget to apply the default stylesheet to.
        """
        QtHandler.apply_stylesheet(widget, "")

    @abstractmethod
    def add_theme(self, path: Union[str, Path]) -> None:
        """
        Registers a theme via ThemeManager.

        Args:
            path (Union[str, Path]): The path to a single theme JSON file or a directory
                containing multiple theme JSON files.

        Raises:
            ValueError: If the path is neither a valid file nor a directory.
        """
        pass

    @abstractmethod
    def get_theme_list(self) -> List[str]:
        """
        Returns a list of theme names available.

        Returns:
            List[str]: The list of theme names.
        """
        pass

    @abstractmethod
    def _get_theme_object(self, theme_name: str) -> "Theme":
        """
        Returns the Theme object for the given theme name.

        Args:
            theme_name (str): The name of the theme to get the Theme object for.

        Returns:
            Theme: The Theme object for the given theme name.
        """
        pass

    @abstractmethod
    def _get_stylesheet(self, theme_name: str) -> str:
        """
        Returns the stylesheet for the given theme name.

        Args:
            theme_name (str): The name of the theme to get the stylesheet for.

        Returns:
            str: The stylesheet for the given theme name.
        """
        pass

    @abstractmethod
    def _get_icons_dir(self, theme_name: str) -> str:
        """
        Returns the directory path for the icons associated with the given theme name.

        Args:
            theme_name (str): The name of the theme for which to retrieve the icons' directory.

        Returns:
            str: The path to the directory containing the icons for the specified theme.
        """
        pass
