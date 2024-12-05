import sys
import logging
import platform
from pathlib import Path
from typing import Final, List, Optional

import jinja2

from .value_object import ExtraAttributes, Theme

ICON_PREFIX = "icon"
ICON_URL_PREFIX = f"{ICON_PREFIX}:/"

DEFAULT_TEMPLATE_FILE: Final = Path(__file__).resolve().parent / "material.css.jinja2"

# ----------------------------------------------------------------------
# Renderer for Rendering Stylesheets
# ----------------------------------------------------------------------


class StyleSheetRenderer:
    __ENVIRONMENT_INFO = {
        "linux": platform.system() == "Linux",
        "windows": platform.system() == "Windows",
        "darwin": platform.system() == "Darwin",
        "pyqt5": "PyQt5" in sys.modules,
        "pyqt6": "PyQt6" in sys.modules,
        "pyside2": "PySide2" in sys.modules,
        "pyside6": "PySide6" in sys.modules,
    }

    def __init__(self, template_file: str = str(DEFAULT_TEMPLATE_FILE)):
        template_path = Path(template_file)
        if not template_path.exists() or not template_path.is_file():
            raise FileNotFoundError(
                f"Template file '{template_path}' does not exist or is not a valid file."
            )
        self.template_path = template_path

    def render(self, theme: Theme, extra: ExtraAttributes) -> str:
        """
        Renders a stylesheet using the provided theme and extra attributes.

        Args:
            theme (Theme): The theme object containing color information.
            extra (ExtraAttributes): Additional attributes for customizing the style.

        Returns:
            str: The rendered stylesheet as a string.

        Raises:
            ValueError: If the theme or extra is not valid.
            RuntimeError: If an error occurs during template rendering.
        """
        if theme is None or not isinstance(theme, Theme):
            raise ValueError("Invalid theme provided. Expected an instance of Theme.")

        if extra is None or not isinstance(extra, ExtraAttributes):
            raise ValueError(
                "Invalid extra provided. Expected an instance of ExtraStyle."
            )

        template = self._load_template()
        template_inputs = {**theme.colors, **extra.values, **self.__ENVIRONMENT_INFO}

        try:
            return template.render(template_inputs)
        except jinja2.TemplateError as e:
            logging.error(f"Template rendering failed: {e}")
            raise RuntimeError("An error occurred during template rendering.") from e

    def _load_template(self) -> jinja2.Template:
        """
        Loads the Jinja2 template for rendering.

        Returns:
            jinja2.Template: The compiled Jinja2 template.
        """
        loader = jinja2.FileSystemLoader(str(self.template_path.parent))
        env = jinja2.Environment(autoescape=False, loader=loader)

        # Custom filters
        env.filters["opacity"] = opacity
        env.filters["density"] = density

        try:
            return env.get_template(self.template_path.name)
        except jinja2.TemplateError as e:
            logging.error(f"Failed to load template: {e}")
            raise RuntimeError("An error occurred while loading the template.") from e


# ----------------------------------------------------------------------
# Exporter for Stylesheets and Resources
# ----------------------------------------------------------------------


class StyleSheetExporter:
    @staticmethod
    def export(
        stylesheet: str,
        destination_dir: str,
        icon_url_prefix: str = ICON_URL_PREFIX,
        qss_name: str = "_stylehelper.qss",
        qrc_name: Optional[str] = None,
    ) -> None:
        """
        Exports the rendered stylesheet and generates QRC files if needed.

        Args:
            stylesheet (str): The rendered stylesheet content.
            destination_dir (str): Directory to save the exported files.
            icon_url_prefix (str): URL prefix for icons.
            qss_name (str): Name of the QSS file to save.
            qrc_name (str, optional): Name of the QRC file to generate.
        """
        if not icon_url_prefix.endswith(":/"):
            raise ValueError("Icon URL prefix must end with ':/'.")
        destination_dir_path = Path(destination_dir)

        StyleSheetExporter._create_destination_dir(destination_dir_path)

        StyleSheetExporter._save_qss_file(
            destination_dir_path, stylesheet, icon_url_prefix, qss_name
        )

        if qrc_name:
            StyleSheetExporter._generate_qrc_file(
                destination_dir_path,
                destination_dir_path / qrc_name,
                icon_url_prefix,
                qss_name,
            )

    @staticmethod
    def _create_destination_dir(destination_dir_path: Path) -> None:
        try:
            if not destination_dir_path.exists():
                destination_dir_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logging.error(f"Failed to create stylesheet destination directory: {e}")
            raise e

    @staticmethod
    def _save_qss_file(
        output_path: Path, stylesheet: str, icon_url_prefix: str, qss_name: str
    ) -> None:
        try:
            with open(output_path / qss_name, "w") as file:
                file.writelines(
                    stylesheet
                    if icon_url_prefix == ICON_URL_PREFIX
                    else stylesheet.replace(ICON_URL_PREFIX, icon_url_prefix)
                )
        except IOError as e:
            logging.error(f"Failed to write QSS file: {e}")
            raise

    @staticmethod
    def _generate_qrc_file(
        output_path: Path,
        qrc_path: Path,
        icon_url_prefix: str,
        qss_name: str,
        sub_folders: Optional[List[str]] = None,
    ) -> None:
        """
        Generates a QRC file from the stylesheet and resources.

        Args:
            output_path (Path): The directory containing resources.
            qrc_path (Path): Path to save the QRC file.
            icon_url_prefix (str): URL prefix for icons.
            qss_name (str): Name of the QSS file to include in QRC.
            sub_folders (list, optional): Sub folders to scan for resources.
        """
        if sub_folders is None:
            sub_folders = [
                folder.name
                for folder in output_path.iterdir()
                if folder.is_dir()
                and any(file.suffix == ".svg" for file in folder.iterdir())
            ]

        qrc_content = [
            "<RCC>",
            f'  <qresource prefix="{icon_url_prefix[:-2]}">',
        ]

        for subfolder in sub_folders:
            resource_dir = output_path / subfolder
            if not resource_dir.exists() or not resource_dir.is_dir():
                logging.warning(f"Resource directory '{resource_dir}' does not exist.")
                continue

            files = [
                f for f in resource_dir.iterdir() if f.is_file() and f.suffix == ".svg"
            ]
            for file in files:
                qrc_content.append(
                    f"    <file>{output_path.name}/{subfolder}/{file.name}</file>"
                )

        qrc_content.append("  </qresource>")

        if qss_name:
            qss_path = output_path / qss_name
            qrc_content.append('  <qresource prefix="file">')
            qrc_content.append(f"    <file>{qss_path.name}</file>")
            qrc_content.append("  </qresource>")

        qrc_content.append("</RCC>")

        try:
            with open(qrc_path, "w") as file:
                file.write("\n".join(qrc_content))
        except IOError as e:
            logging.error(f"Failed to write QRC file: {e}")
            raise


# ----------------------------------------------------------------------
# Utility Functions
# ----------------------------------------------------------------------


def opacity(hex_color: str, opacity_value: float = 0.5) -> str:
    """
    Converts a hex color to an RGBA string with the specified opacity.

    Args:
        hex_color (str): Hexadecimal color string (e.g., '#RRGGBB').
        opacity_value (float): Opacity value (0.0 to 1.0).

    Returns:
        str: RGBA color string (e.g., 'rgba(255, 0, 0, 0.5)').
    """
    if not (hex_color.startswith("#") and len(hex_color) == 7):
        raise ValueError("Invalid hex color format. Expected format: '#RRGGBB'.")
    if not (0.0 <= opacity_value <= 1.0):
        raise ValueError("Opacity value must be between 0.0 and 1.0.")

    r, g, b = (int(hex_color[i : i + 2], 16) for i in range(1, 7, 2))
    return f"rgba({r}, {g}, {b}, {opacity_value})"


def density(
    value,
    density_scale: int,
    border: int = 0,
    scale: float = 1,
    density_interval: int = 4,
    min_: int = 4,
):
    """
    Adjusts a value based on density scaling rules.

    Args:
        value (str|float): The base value. Strings are treated as pixel values (e.g., '16px').
        density_scale (int): Density scale multiplier.
        border (int): Border size to subtract.
        scale (float): Additional scaling factor.
        density_interval (int): Increment for density adjustments.
        min_ (int): Minimum value to return.

    Returns:
        float|str: The adjusted value or 'unset'.
    """
    if isinstance(value, str):
        if value.startswith("@"):
            return float(value[1:]) * scale
        if value == "unset":
            return "unset"
        try:
            value = float(value.replace("px", ""))
        except ValueError:
            raise ValueError(
                "Invalid value format. Expected a numeric value or 'unset'."
            )

    adjusted_density = (
        value + (density_interval * density_scale) - (border * 2)
    ) * scale
    return max(adjusted_density, min_)
