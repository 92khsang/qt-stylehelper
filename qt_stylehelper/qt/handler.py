from __future__ import annotations as _annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from qt_stylehelper.core.decorators import require_qt, require_qt_for_all_methods
from qt_stylehelper.core.utils import QtBindingUtils
from qt_stylehelper.themes.stylesheet import ICON_PREFIX

if TYPE_CHECKING:
    from qt_stylehelper.themes.models import Theme

    if QtBindingUtils.get_backend() == "PySide6":
        from PySide6.QtWidgets import QWidget
    else:
        QWidget = Any

if QtBindingUtils.is_available():
    if QtBindingUtils.get_backend() == "PySide6":
        from PySide6.QtCore import QDir
        from PySide6.QtGui import QFontDatabase, QColor, QGuiApplication, QPalette

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
                    result = QFontDatabase.add_application_font(font_path)  # noqa
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
        def apply_stylesheet(app: QWidget, stylesheet: str) -> None:
            """
            Applies the provided stylesheet to the application.

            Args:
                    app: The Qt application instance.
                    stylesheet (str): Stylesheet content.
            """
            if not hasattr(app, "setStyleSheet"):
                logging.error("Provided app does not support setStyleSheet.")
                return

            try:
                app.setStyleSheet(stylesheet)
            except AttributeError:
                app.styleSheet = stylesheet
            except Exception as e:
                logging.error(f"Failed to apply stylesheet {e}")

        @staticmethod
        @require_qt
        def add_search_paths(resource_dir: str, icon_prefix: str = ICON_PREFIX) -> None:
            """
            Adds search paths for Qt resources.

            Args:
                    resource_dir (str): Path to the directory containing resources.
                    icon_prefix (str): Prefix to use for resource paths.
            """
            path = Path(resource_dir)
            if not path.is_dir():
                logging.error(
                    f"The directory {resource_dir} does not exist or is not accessible."
                )
                return

            try:
                QDir.setSearchPaths(icon_prefix, [])
                QDir.addSearchPath(icon_prefix, str(path))
            except AttributeError:
                QDir.set_search_paths(icon_prefix, [])  # noqa
                QDir.add_search_path(icon_prefix, str(path))  # noqa
            except Exception as e:
                logging.error(f"Failed to add search paths for '{resource_dir}' {e}")

    # ----------------------------------------------------------------------
    # Palette Handling
    # ----------------------------------------------------------------------

    class _QtPaletteHandler:
        """
        Handles operations related to Qt palettes.
        """

        @staticmethod
        @require_qt
        def apply_palette(theme: "Theme") -> None:
            """
            Applies a color palette to the Qt application based on the provided theme.

            Args:
                    theme (Theme): The theme containing color information.
            """
            primary_color: "QColor" = _QtPaletteHandler._hex_to_color(
                theme.primary_color
            )
            palette: "QPalette" = QGuiApplication.palette()

            try:
                if hasattr(QPalette, "ColorRole"):
                    palette.setColor(QPalette.ColorRole.PlaceholderText, primary_color)
                elif hasattr(QPalette, "PlaceholderText"):
                    palette.setColor(QPalette.PlaceholderText, primary_color)
                else:
                    palette.setColor(QPalette.Text, primary_color)  # noqa

                QGuiApplication.setPalette(palette)
            except AttributeError:
                palette.set_color(QPalette.ColorRole.Text, primary_color)  # noqa
                QGuiApplication.set_palette(palette)  # noqa
            except Exception as e:
                logging.error(f"Failed to apply palette {e}")

        @staticmethod
        def _hex_to_color(hex_color: str, alpha: int = 92) -> "QColor":
            """
            Converts a hexadecimal color string to a QColor object with an optional alpha value.

            Args:
                    hex_color (str): Hexadecimal color string (e.g., '#RRGGBB').
                    alpha (int): Alpha value (0-255) for transparency.

            Returns:
                    QColor: QColor object representing the color.
            """
            if not (0 <= alpha <= 255):
                logging.error(
                    f"Invalid alpha value '{alpha}'. Must be between 0 and 255."
                )
                alpha = 255  # Default to fully opaque

            try:
                r = int(hex_color[1:3], 16)
                g = int(hex_color[3:5], 16)
                b = int(hex_color[5:7], 16)
                return QColor(r, g, b, alpha)
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
        def apply_stylesheet(app: QWidget, stylesheet: str) -> None:
            _QtStyleHandler.apply_stylesheet(app, stylesheet)

        @staticmethod
        def add_search_paths(resource_dir: str, icon_prefix: str = ICON_PREFIX) -> None:
            _QtStyleHandler.add_search_paths(resource_dir, icon_prefix)

        @staticmethod
        def apply_palette(theme: "Theme") -> None:
            _QtPaletteHandler.apply_palette(theme)

else:
    logging.warning("No Qt backend found. Qt features will be disabled.")

    class QtHandler:
        @staticmethod
        def _warn(method: str) -> None:
            logging.warning(
                f"[QtStyleHelper] '{method}()' called but PySide6 is not installed."
            )

        @staticmethod
        def add_fonts(font_dir: str) -> None:
            QtHandler._warn("add_fonts")

        @staticmethod
        def apply_stylesheet(app: QWidget, stylesheet: str) -> None:
            QtHandler._warn("apply_stylesheet")

        @staticmethod
        def add_search_paths(resource_dir: str, icon_prefix: str = ...) -> None:
            QtHandler._warn("add_search_paths")

        @staticmethod
        def apply_palette(theme: "Theme") -> None:
            QtHandler._warn("apply_palette")
