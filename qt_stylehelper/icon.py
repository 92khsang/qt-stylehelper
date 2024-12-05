import re
import logging
from pathlib import Path
from typing import Final, List, Optional

from .value_object import Theme
from ._utils import get_platform_resource_dir_path, is_valid_filename, validate_dir_path

ICON_CONTEXT: Final[List[str]] = ["disabled", "primary", "active"]


# ----------------------------------------------------------------------
# Utility Functions
# ----------------------------------------------------------------------
def replace_color(svg_content: str, origin_color: str, replacement: str) -> str:
    """
    Efficiently replaces the given color (with optional \n between characters)
    in the SVG content. Also replaces black (#000000) with transparency (#ffffff00).

    :param svg_content: The SVG content string.
    :param replacement: The color to replace the target color with (e.g., "#FF0000").
    :param origin_color: The target color to replace (e.g., "#0000ff").
    :return: Updated SVG content.
    """

    # Helper to create a regex pattern for a color
    def color_pattern(hex_color: str) -> str:
        """
        Returns a regex pattern to match the given hex color, allowing optional \n between characters.

        Example:
                For "#0000FF", the regex would be "\#(0\n?)(0\n?)(0\n?)(F\n?)(F\n?)(F\n?)".
        """
        return r"\#" + "".join(f"({char}\n?)" for char in hex_color[1:])

    # Replace the primary color
    primary_pattern = re.compile(color_pattern(origin_color), re.IGNORECASE)
    svg_content = primary_pattern.sub(replacement, svg_content)

    # Replace black (#000000) with transparency
    black_pattern = re.compile(color_pattern("#000000"))
    svg_content = black_pattern.sub("#ffffff00", svg_content)

    return svg_content


# ----------------------------------------------------------------------
# Internal Utility Functions
# ----------------------------------------------------------------------
def _get_icon_name_list(dir_path: Path) -> List[str]:
    return [f.name for f in dir_path.glob("*.svg")]


# ----------------------------------------------------------------------
# Built-in Icon Directory Validator
# ----------------------------------------------------------------------
class BuiltInIconDirValidator:
    __BUILT_IN_ICON_LIST: Final = set(
        _get_icon_name_list(Path(__file__).resolve().parent / "resources" / "icons")
    )

    @staticmethod
    def validate(icon_dir: str, theme_name: Optional[str] = None) -> None:
        """
        Validates that the given icon directory contains all the required built-in icons.

        Args:
            icon_dir (str): The path to the directory containing the icon themes.
            theme_name (Optional[str]): The name of the theme to validate, if not provided, the
                validate function will validate the root of the icon directory.
        """
        theme_dir = Path(icon_dir) / theme_name if theme_name else Path(icon_dir)

        validate_dir_path(theme_dir)
        BuiltInIconDirValidator._validate_icon_context_dirs(theme_dir)

        for context in ICON_CONTEXT:
            context_dir = theme_dir / context
            BuiltInIconDirValidator._validate_icon_list(context_dir)

    @staticmethod
    def _validate_icon_context_dirs(theme_dir: Path) -> None:
        missing_context_dirs = [
            context for context in ICON_CONTEXT if not (theme_dir / context).exists()
        ]
        if missing_context_dirs:
            raise FileNotFoundError(
                f"Missing context directories: {', '.join(missing_context_dirs)} in theme directory '{theme_dir}'."
            )

    @staticmethod
    def _validate_icon_list(context_dir: Path) -> None:
        context_icon_list = set(_get_icon_name_list(context_dir))
        if not BuiltInIconDirValidator.__BUILT_IN_ICON_LIST.issubset(context_icon_list):
            raise ValueError(
                f"The icon list of '{context_dir.name}' does not contain all the required icons."
            )


# ----------------------------------------------------------------------
# Built-in Icon Generator
# ----------------------------------------------------------------------
class BuiltInIconGenerator:
    __MAIN_COLOR: Final[str] = "#0000ff"
    __SUB_COLOR: Final[str] = "#ff0000"

    @staticmethod
    def generate_dynamically(theme: Theme, app_name: str = ".pyqtapp") -> None:
        """
        Generates icons dynamically for a specified theme.

        Args:
            theme (Theme): The theme object to generate icons for.
            app_name (str): The name of the application to generate icons for, if not
                provided, the default value ".pyqtapp" will be used.

        Raises:
            ValueError: If the specified theme is not found.
        """
        destination_dir_path = BuiltInIconGenerator.get_dynamic_icons_dir(app_name)
        BuiltInIconGenerator._generate_icons(theme, destination_dir_path)

    @staticmethod
    def get_dynamic_icons_dir(app_name: str = ".pyqtapp") -> Path:
        """
        Gets the path to a directory suitable for storing dynamically generated icons for a given
        application name on the current platform.

        Args:
            app_name (str): The name of the application. If not provided, the default value ".pyqtapp"
                will be used.

        Returns:
            Path: The path to the directory on the current platform.

        Raises:
            ValueError: If the app name contains prohibited characters.
        """

        app_name = app_name if is_valid_filename(app_name) else ".pyqtapp"
        destination_dir_path = get_platform_resource_dir_path(app_name)
        BuiltInIconGenerator._create_destination_dir(destination_dir_path)
        return destination_dir_path

    @staticmethod
    def generate_statically(
        theme: Theme,
        destination_dir: str,
    ) -> None:

        """
        Generates icons statically for a specified theme.

        Args:
            theme (Theme): The theme object to generate icons for.
            destination_dir (str): Directory to save the generated icons.

        Raises:
            ValueError: If the specified theme is not found.
        """
        destination_dir_path = Path(destination_dir)

        # Create the destination directory
        BuiltInIconGenerator._create_destination_dir(destination_dir_path)
        BuiltInIconGenerator._generate_icons(theme, destination_dir_path)

    @staticmethod
    def _create_destination_dir(destination_dir_path: Path) -> None:
        try:
            if not destination_dir_path.exists():
                destination_dir_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logging.error(f"Failed to create icon destination directory: {e}")
            raise e

    @staticmethod
    def _generate_icons(theme: Theme, destination_dir_path: Path) -> None:
        source_dir_path = Path(__file__).resolve().parent / "resources" / "icons"
        context_icon_generator = ContextIconGenerator(
            original_main_color=BuiltInIconGenerator.__MAIN_COLOR,
            original_sub_color=BuiltInIconGenerator.__SUB_COLOR,
        )
        context_icon_generator.generate(
            theme=theme,
            source_dir=str(source_dir_path),
            destination_dir=str(destination_dir_path),
        )


# ----------------------------------------------------------------------
# Context Icon Generator
# ----------------------------------------------------------------------
class ContextIconGenerator:

    def __init__(self, original_main_color: str, original_sub_color: str):

        self.original_main_color = original_main_color
        self.original_sub_color = original_sub_color

    def generate(
        self,
        theme: Theme,
        source_dir: str = None,
        destination_dir: str = None,
    ) -> None:
        """
        Generates icons statically for a specified theme.

        Args:
            theme (Theme): The theme object to generate icons for.
            source_dir (str, optional): Directory containing the original icons.
            destination_dir (str, optional): Directory to save the generated icons.

        Raises:
            ValueError: If the specified theme is not found.
        """
        
        if source_dir is None or destination_dir is None:
            raise ValueError("Both source_dir and destination_dir must be provided.")

        source_dir_path = Path(source_dir)
        validate_dir_path(source_dir_path)

        destination_dir_path = Path(destination_dir)
        validate_dir_path(destination_dir_path)

        icon_paths = self._get_all_icon_files(source_dir_path)

        for context in ICON_CONTEXT:
            context_dir = destination_dir_path / context
            context_dir.mkdir(parents=True, exist_ok=True)

            main_color = theme.colors.get(
                {
                    "primary": "primaryColor",
                    "disabled": "secondaryLightColor",
                    "active": "activeColor",
                }[context],
                "#000000",
            )

            sub_color = theme.colors.get(
                {
                    "primary": "secondaryColor",
                    "disabled": "secondaryColor",
                    "active": "secondaryColor",
                }[context],
                "#000000",
            )

            for icon_path in icon_paths:
                self._process_svg(
                    svg_file=icon_path,
                    output_dir=context_dir,
                    replace_main_color=main_color,
                    replace_sub_color=sub_color,
                )

    def _process_svg(
        self,
        svg_file: Path,
        output_dir: Path,
        replace_main_color: str,
        replace_sub_color: str,
    ) -> None:
        """
        Reads an SVG file, applies the specified color, and writes it to the output directory.
        """
        try:
            with svg_file.open("r") as file_input:
                content = file_input.read()
        except Exception as e:
            raise RuntimeError(f"Failed to read SVG file {svg_file}: {e}")

        updated_content = replace_color(
            content, self.original_main_color, replace_main_color
        )
        updated_content = replace_color(
            updated_content, self.original_sub_color, replace_sub_color
        )

        output_file = output_dir / svg_file.name

        try:
            with output_file.open("w") as file_output:
                file_output.write(updated_content)
        except Exception as e:
            raise RuntimeError(f"Failed to write processed SVG {output_file}: {e}")

    @staticmethod
    def _get_all_icon_files(directory: Path) -> List[Path]:
        return list(directory.rglob("*.svg"))
