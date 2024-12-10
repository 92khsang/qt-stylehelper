import logging
import sys
from pathlib import Path

from ._stylesheet import ICON_PREFIX
from ._theme import Theme
from .class_helpers import require_qt, require_qt_for_all_methods

if "PySide6" in sys.modules:
    from PySide6.QtCore import QDir
    from PySide6.QtGui import QFontDatabase, QColor, QGuiApplication, QPalette
else:
    from ._mock_qt import (
        MockQt as QDir,
        MockQt as QFontDatabase,
        MockQt as QColor,
        MockQt as QGuiApplication,
        MockQt as QPalette,
    )


    logging.warning(
        "If you intend to use code related to Qt, the corresponding Qt libraries are required."
    )


# ----------------------------------------------------------------------
# Font Handling
# ----------------------------------------------------------------------


class _QtFontDBHandler:
    """
    Handles font operations like adding application fonts.
    """

    @staticmethod
    @require_qt
    def add_fonts_from_directory(font_dir: str) -> None:
        """
        Adds fonts from the specified directory to the application.

        Args:
                font_dir (str): Path to the directory containing font files.
        """
        if not font_dir:
            logging.error("The font_dir argument is None or empty.")
            return

        path = Path(font_dir)
        if not path.is_dir():
            logging.error(
                f"The directory {font_dir} does not exist or is not accessible."
            )
            return

        result = -1
        for font_path in path.glob("*.ttf"):
            try:
                result = QFontDatabase.addApplicationFont(str(font_path))
            except AttributeError:
                result = QFontDatabase.add_application_font(font_path)
            except Exception as e:
                logging.error(f"Error loading font '{font_path.name}': {e}")
            finally:
                if result == -1:
                    logging.debug(f"Failed to load font: {font_path.name}")


# ----------------------------------------------------------------------
# Stylesheet Handling
# ----------------------------------------------------------------------


class _QtStyleHandler:
    """
    Handles operations related to Qt stylesheets.
    """

    @staticmethod
    @require_qt
    def apply_style(app, style: str) -> None:
        try:
            try:
                app.setStyle(style)
            except AttributeError:
                app.style = style
        except Exception as e:
            logging.error(f"The style '{style}' does not exist.", e)

    @staticmethod
    @require_qt
    def apply_stylesheet(app, stylesheet: str) -> None:
        """
        Applies the provided stylesheet to the application.

        Args:
                app: The Qt application instance.
                stylesheet (str): Stylesheet content.
        """
        if not hasattr(app, "setStyleSheet"):
            logging.error("Provided app does not support setStyleSheet.")
            return

        if not isinstance(stylesheet, str):
            logging.error("Stylesheet must be a string.")
            return

        try:
            app.setStyleSheet(stylesheet)
        except AttributeError:
            app.styleSheet = stylesheet
        except Exception as e:
            logging.error(f"Failed to apply stylesheet", e)

    @staticmethod
    @require_qt
    def add_search_paths(resource_dir: str, icon_prefix: str = ICON_PREFIX) -> None:
        """
        Adds search paths for Qt resources.

        Args:
                resource_dir (str): Path to the directory containing resources.
                icon_prefix (str): Prefix to use for resource paths.
        """
        if not resource_dir:
            logging.error("The resource_dir argument is None or empty.")
            return

        path = Path(resource_dir)
        if not path.is_dir():
            logging.error(
                f"The directory {resource_dir} does not exist or is not accessible."
            )
            return

        success = False
        try:
            QDir.setSearchPaths(icon_prefix, [])
            QDir.addSearchPath(icon_prefix, str(path))
            success = True
        except AttributeError:
            QDir.set_search_paths(icon_prefix, [])
            QDir.add_search_path(icon_prefix, str(path))
            success = True
        except Exception as e:
            logging.error(f"Failed to add search paths for '{resource_dir}': {e}")
        finally:
            if not success:
                logging.debug(f"Failed to add search paths for '{resource_dir}'.")


# ----------------------------------------------------------------------
# Palette Handling
# ----------------------------------------------------------------------


class _QtPaletteHandler:
    """
    Handles operations related to Qt palettes.
    """

    @staticmethod
    @require_qt
    def apply_palette(theme: Theme) -> None:
        """
        Applies a color palette to the Qt application based on the provided theme.

        Args:
                theme (Theme): The theme containing color information.
        """
        if theme is None or not isinstance(theme, Theme):
            logging.error("Invalid theme provided. Expected an instance of Theme.")
            return

        primary_color_key = "primaryColor"
        if primary_color_key not in theme.colors:
            logging.error(f"Theme does not contain the key '{primary_color_key}'.")
            return

        primary_color = _QtPaletteHandler._hex_to_qt_color(
            theme.colors[primary_color_key]
        )
        palette = QGuiApplication.palette()

        try:
            if hasattr(QPalette, "PlaceholderText"):
                palette.setColor(QPalette.PlaceholderText, primary_color)
            else:
                palette.setColor(QPalette.Text, primary_color)

            QGuiApplication.setPalette(palette)
        except AttributeError:
            palette.set_color(QPalette.ColorRole.Text, primary_color)
            QGuiApplication.set_palette(palette)
        except Exception as e:
            logging.error(f"Failed to apply palette: {e}")

    @staticmethod
    def _hex_to_qt_color(hex_color: str, alpha: int = 92) -> QColor:
        """
        Converts a hexadecimal color string to a QColor object with an optional alpha value.

        Args:
                hex_color (str): Hexadecimal color string (e.g., '#RRGGBB').
                alpha (int): Alpha value (0-255) for transparency.

        Returns:
                QColor: QColor object representing the color.
        """
        if not (0 <= alpha <= 255):
            logging.error(f"Invalid alpha value '{alpha}'. Must be between 0 and 255.")
            alpha = 255  # Default to fully opaque

        try:
            rgb = [int(hex_color[i : i + 2], 16) for i in range(1, 7, 2)]
            return QColor(*rgb, alpha)
        except (ValueError, IndexError) as e:
            logging.error(f"Invalid hex color '{hex_color}': {e}")
            return QColor(0, 0, 0, alpha)  # Default to black if parsing fails


# ----------------------------------------------------------------------
# QtHandler: Main Entry Point
# ----------------------------------------------------------------------
@require_qt_for_all_methods
class QtHandler:
    """
    Central handler that delegates operations to other handlers.
    """

    @staticmethod
    def add_fonts(font_dir: str) -> None:
        _QtFontDBHandler.add_fonts_from_directory(font_dir)

    @staticmethod
    def apply_stylesheet(app, stylesheet: str) -> None:
        _QtStyleHandler.apply_stylesheet(app, stylesheet)

    @staticmethod
    def add_search_paths(resource_dir: str, icon_prefix: str = ICON_PREFIX) -> None:
        _QtStyleHandler.add_search_paths(resource_dir, icon_prefix)

    @staticmethod
    def apply_palette(theme: Theme) -> None:
        _QtPaletteHandler.apply_palette(theme)
