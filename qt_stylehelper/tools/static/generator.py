import json
from pathlib import Path
from typing import Optional, List, Union

from qt_stylehelper.themes.icon import BuiltInIconGenerator
from qt_stylehelper.themes.manager import ThemeManager
from qt_stylehelper.themes.models import Theme, ExtraAttribute
from qt_stylehelper.themes.stylesheet import StyleSheetRenderer, StyleSheetExporter


class StaticStyleGenerator:

    @staticmethod
    def get_builtin_theme_list() -> List[str]:
        return [theme.stem for theme in ThemeManager.get_builtin_theme_list()]

    @staticmethod
    def generate_from_builtin(
        theme_name: str,
        extra: Optional[ExtraAttribute] = None,
        output_dir: Optional[Union[str, Path]] = None,
        qss_filename: str = "_stylehelper.qss",
        qrc_filename: Optional[str] = None,
    ) -> None:
        """
        Generates resources for a specified theme.

        Args:
            theme_name (str): The name of the theme to generate resources for.
            extra (Optional[ExtraAttribute]):
                Additional attributes to customize the theme. Defaults to an empty dictionary.
            output_dir (Optional[str]): Directory to save the generated resources.
                If None, a default directory will be used.
            qss_filename (str): The name of the QSS file to generate. Defaults to "_stylehelper.qss".
            qrc_filename (Optional[str]): The name of the QRC file to generate, if needed.

        Raises:
            ValueError: If the specified theme is not found.
        """
        theme = ThemeManager.load_builtin_theme(theme_name)
        if theme is None:
            raise ValueError(f"Theme '{theme_name}' not found.")

        StaticStyleGenerator.generate_from_custom(
            theme_name=theme_name,
            theme=theme,
            extra=extra,
            output_dir=output_dir,
            qss_filename=qss_filename,
            qrc_filename=qrc_filename,
        )

    @staticmethod
    def generate_from_custom(
        theme_name: str,
        theme: Theme,
        extra: Optional[ExtraAttribute] = None,
        output_dir: Optional[Union[str, Path]] = None,
        qss_filename: str = "_stylehelper.qss",
        qrc_filename: Optional[str] = None,
    ) -> None:
        """
        Generates resources for a specified theme object.

        Args:
            theme_name (str): The name of the theme to generate resources for.
            theme (Theme): The theme object to generate resources for.
            extra (ExtraAttribute):
                Additional attributes to customize the theme. Defaults to an empty dictionary.
            output_dir (Optional[str]): Directory to save the generated resources.
                If None, a default directory will be used.
            qss_filename (str): The name of the QSS file to generate. Defaults to "_stylehelper.qss".
            qrc_filename (Optional[str]): The name of the QRC file to generate, if needed.

        Raises:
            ValueError: If the specified theme is not found.
        """
        extra = extra or ExtraAttribute()
        output_path = StaticStyleGenerator._resolve_output_path(theme_name, output_dir)

        qss = StyleSheetRenderer().render(theme=theme, extra=extra)

        BuiltInIconGenerator.generate_statically(
            theme=theme, destination_dir=str(output_path)
        )

        StyleSheetExporter.export(
            stylesheet=qss,
            destination_dir=str(output_path),
            qss_name=qss_filename,
            qrc_name=qrc_filename,
        )

        with open(output_path / f"{theme_name}.json", "w", encoding="utf-8") as f:
            json.dump(theme.to_dict(), f, indent=4)

    @staticmethod
    def _resolve_output_path(
        theme_name: str, output_dir: Optional[Union[str, Path]]
    ) -> Path:
        """
        Builds a destination directory path for a theme.

        If the destination_dir is specified, it will be used as the base directory.
        Otherwise, the current working directory will be used.

        The theme_name will be added to the destination directory as a subdirectory.

        Returns:
            Path: The fully qualified destination directory path.
        """

        base_dir = Path(output_dir) if output_dir else Path.cwd() / "resources"
        return base_dir / theme_name
