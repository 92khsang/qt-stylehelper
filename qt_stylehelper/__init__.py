import re
import sys
import json
import logging
from pathlib import Path
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

if "PySide6" in sys.modules:
    from ._qt import QtHandler
    from PySide6.QtWidgets import QWidget
else:
    from ._mock_qt import (
        MockQWidget as QWidget,
        MockQtHandler as QtHandler,
    )

from ._theme import ThemeManager
from ._utils import validate_dir_path
from .value_object import Theme, ExtraAttributes
from .icon import BuiltInIconGenerator, BuiltInIconDirValidator
from ._stylesheet import StyleSheetRenderer, StyleSheetExporter, DEFAULT_TEMPLATE_FILE
from .class_helpers import (
    override,
    require_qt_for_all_methods,
    require_init_for_all_methods,
)


# ----------------------------------------------------------------------
# Class to generate static built-in resources
# ----------------------------------------------------------------------
class StaticBuiltInResourceGenerator:

    @staticmethod
    def generate(
        theme_name: str,
        extra: Optional[Dict[str, Union[str, Dict[str, str], None]]] = None,
        destination_dir: Optional[str] = None,
        qss_name: str = "_stylehelper.qss",
        qrc_name: Optional[str] = None,
    ) -> None:
        """
        Generates resources for a specified theme.

        Args:
            theme_name (str): The name of the theme to generate resources for.
            extra (Optional[Dict[str, Union[str, Dict[str, str], None]]]): 
                Additional attributes to customize the theme. Defaults to an empty dictionary.
            destination_dir (Optional[str]): Directory to save the generated resources.
                If None, a default directory will be used.
            qss_name (str): The name of the QSS file to generate. Defaults to "_stylehelper.qss".
            qrc_name (Optional[str]): The name of the QRC file to generate, if needed.

        Raises:
            ValueError: If the specified theme is not found.
        """
        if extra is None:
            extra = {}

        theme_manager = ThemeManager()
        theme_object = theme_manager.load_theme(theme_name)
        if theme_object is None:
            raise ValueError(f"Theme '{theme_name}' not found.")

        StaticBuiltInResourceGenerator.generate_custom_theme(
            theme_name, theme_object, extra, destination_dir, qss_name, qrc_name
        )

    @staticmethod
    def generate_custom_theme(
        theme_name: str,
        theme_object: Theme,
        extra: Optional[Dict[str, Union[str, Dict[str, str], None]]] = None,
        destination_dir: Optional[str] = None,
        qss_name: str = "_stylehelper.qss",
        qrc_name: Optional[str] = None,
    ) -> None:
        """
        Generates resources for a specified theme object.

        Args:
            theme_name (str): The name of the theme to generate resources for.
            theme_object (Theme): The theme object to generate resources for.
            extra (Optional[Dict[str, Union[str, Dict[str, str], None]]]):
                Additional attributes to customize the theme. Defaults to an empty dictionary.
            destination_dir (Optional[str]): Directory to save the generated resources.
                If None, a default directory will be used.
            qss_name (str): The name of the QSS file to generate. Defaults to "_stylehelper.qss".
            qrc_name (Optional[str]): The name of the QRC file to generate, if needed.

        Raises:
            ValueError: If the specified theme is not found.
        """

        if extra is None:
            extra = {}

        destination_dir_path = StaticBuiltInResourceGenerator._build_destination_dir(
            theme_name, destination_dir
        )
        extra_attributes = ExtraAttributes(extra=extra)

        stylesheet_renderer = StyleSheetRenderer()
        stylesheet = stylesheet_renderer.render(
            theme=theme_object, extra=extra_attributes
        )

        BuiltInIconGenerator.generate_statically(
            theme=theme_object, destination_dir=str(destination_dir_path)
        )

        StyleSheetExporter.export(
            stylesheet=stylesheet,
            destination_dir=str(destination_dir_path),
            qss_name=qss_name,
            qrc_name=qrc_name,
        )

        with open(destination_dir_path / f"{theme_name}.json", "w") as file:
            json.dump(theme_object.colors, file, indent=4)

    @staticmethod
    def _build_destination_dir(
        theme_name: str, destination_dir: Optional[str] = None
    ) -> Path:
        """
        Builds a destination directory path for a theme.

        If the destination_dir is specified, it will be used as the base directory.
        Otherwise, the current working directory will be used.

        The theme_name will be added to the destination directory as a subdirectory.

        Returns:
            Path: The fully-qualified destination directory path.
        """

        destination_dir_path = (
            Path(destination_dir)
            if destination_dir
            else Path().cwd().resolve() / "resources"
        )
        return destination_dir_path / theme_name


# ----------------------------------------------------------------------
# Class to
# ----------------------------------------------------------------------
@require_qt_for_all_methods
@require_init_for_all_methods
class QtStyleTools(metaclass=ABCMeta):
    def __init__(self) -> None:
        self._current_theme = "default"
        self._init = False

    def apply_stylesheet(self, widget: QWidget, theme_name: str) -> None:
        """
        Applies a stylesheet to the given widget.

        Args:
            widget (QWidget): The widget to apply the stylesheet to.
            theme_name (str): The name of the theme to apply.

        Raises:
            ValueError: If the widget is not a valid QWidget instance.
            ValueError: If the theme_name is not found.
        """
        if not isinstance(widget, QWidget):
            raise ValueError("Widget must be a valid QWidget instance.")

        if theme_name not in self.get_theme_list():
            raise ValueError(f"Theme '{theme_name}' not found.")

        if self._current_theme == theme_name:
            return

        if theme_name == "default":
            self._apply_default(widget)
        else:
            stylesheet = self._get_stylesheet(theme_name)
            QtHandler.add_search_paths(resource_dir=self._get_icons_dir(theme_name))
            QtHandler.apply_palette(self._get_theme_object(theme_name))
            QtHandler.apply_stylesheet(widget, stylesheet)

        self._current_theme = theme_name

    @staticmethod
    def _apply_default(widget: QWidget) -> None:
        """
        Applies the default stylesheet to the given widget.

        Args:
            widget (QWidget): The widget to apply the default stylesheet to.
        """
        QtHandler.apply_stylesheet(widget, "")

    @abstractmethod
    def get_theme_list(self) -> List[str]:
        """
        Returns a list of theme names available.

        Returns:
            List[str]: The list of theme names.
        """
        pass

    @abstractmethod
    def _get_theme_object(self, theme_name: str) -> Theme:
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
            theme_name (str): The name of the theme for which to retrieve the icons directory.

        Returns:
            str: The path to the directory containing the icons for the specified theme.
        """
        pass


# ----------------------------------------------------------------------
# Class to
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class StaticThemeDirectoryStructure:
    theme: Union[Path, Theme]
    theme_dir: Path
    theme_name: Optional[str] = None
    qss_files: List[Path] = field(default_factory=list)

    def __post_init__(self):
        if self.theme_name is None:
            object.__setattr__(self, "theme_name", self.theme_dir.stem)

    def replace_theme(self, theme: Union[Path, Theme]):
        """
        Replaces the current theme with a new one if it differs in type or value.

        Args:
            theme (Union[Path, Theme]): The new theme to replace the current theme.

        Returns:
            StaticThemeDirectoryStructure: A new instance with the updated theme if
            it differs from the current theme, otherwise returns the same instance.
        """
        if not isinstance(theme, type(self.theme)) or theme != self.theme:
            return StaticThemeDirectoryStructure(
                theme=theme,
                theme_dir=self.theme_dir,
                qss_files=self.qss_files,
                theme_name=self.theme_name,
            )
        else:
            return self

    def replace_qss_files(self, qss_files: List[Path]):
        """
        Replaces the current list of QSS files with a new one if it differs in type or value.

        Args:
            qss_files (List[Path]): The new list of QSS files to replace the current list.

        Returns:
            StaticThemeDirectoryStructure: A new instance with the updated list of QSS files if
            it differs from the current list, otherwise returns the same instance.
        """
        if self.qss_files == qss_files:
            return self

        return StaticThemeDirectoryStructure(
            theme=self.theme,
            theme_dir=self.theme_dir,
            qss_files=qss_files,
            theme_name=self.theme_name,
        )


class StaticQtStyleTools(QtStyleTools):
    def __init__(self):
        super().__init__()

        self._theme_struct_dict = None

    def auto_init(self, theme_parent_dir: str) -> None:
        """
        Automatically initializes the theme structures from a given parent directory.

        Args:
            theme_parent_dir (str): The path to the parent directory containing theme directories.
        """
        theme_structs = self.scan_theme_dir(theme_parent_dir)
        self.manual_init(theme_structs)

    def manual_init(self, theme_structs: List[StaticThemeDirectoryStructure]) -> None:
        """
        Manually initializes the theme structures from a given list.

        Args:
            theme_structs (List[StaticThemeDirectoryStructure]): The list of theme structures to
                initialize with.

        Returns:
            None
        """
        self._verify_unique_theme_names(theme_structs)

        theme_structs = self._filter_and_proceed_structures(theme_structs)
        if theme_structs is None or len(theme_structs) == 0:
            logging.debug("No valid theme directories found.")
            return

        self._theme_struct_dict = self._convert_to_dict(theme_structs)
        self._init = True

    def scan_theme_dir(
        self, theme_parent_dir: str
    ) -> List[StaticThemeDirectoryStructure]:
        """
        Scans a given parent directory for theme directories and returns a list of
        StaticThemeDirectoryStructure objects representing the theme structures.

        Args:
            theme_parent_dir (str): The path to the parent directory containing theme directories.

        Returns:
            List[StaticThemeDirectoryStructure]: A list of theme structures found in the given parent directory.
        """
        theme_parent_dir_path = Path(theme_parent_dir)
        validate_dir_path(theme_parent_dir_path)

        structures: List[StaticThemeDirectoryStructure] = []

        for theme_dir in theme_parent_dir_path.iterdir():
            if theme_dir.is_dir():
                qss_files = sorted(
                    list(theme_dir.glob("*.qss")),
                    key=lambda qss_file: not self.is_rendered_from_builtin_template(
                        qss_file
                    ),
                )
                theme = theme_dir / f"{theme_dir.name}.json"
                structures.append(
                    StaticThemeDirectoryStructure(
                        theme=theme, theme_dir=theme_dir, qss_files=qss_files
                    )
                )
        return structures

    @staticmethod
    def is_rendered_from_builtin_template(qss_file: Path) -> bool:
        """Checks if a given QSS file is rendered from the default Jinja2 template."""
        # The approach here is to compare the top 4 lines of the file to the top 4
        # lines of the default Jinja2 template. These lines are the copy-right
        # comments and should only be changed if the template is modified.
        # If the files are the same, the QSS file is rendered from the default
        # Jinja2 template.

        if qss_file is None or not qss_file.is_file():
            logging.debug(f"File '{qss_file}' does not exist or is not a file.")
            return False
        try:
            with qss_file.open(
                "r", encoding="utf-8"
            ) as qss_file, DEFAULT_TEMPLATE_FILE.open(
                "r", encoding="utf-8"
            ) as jinja_template:
                # Top 4 lines are copy-right comments
                qss_top_4_lines = [
                    line.strip() for line in [next(qss_file, "") for _ in range(4)]
                ]
                jinja_top_4_lines = [
                    line.strip()
                    for line in [next(jinja_template, "") for _ in range(4)]
                ]
                return qss_top_4_lines == jinja_top_4_lines
        except FileNotFoundError as e:
            logging.debug(f"File not found: {e}")
            return False
        except Exception as e:
            logging.debug(f"Error while comparing files: {e}")
            return False

    @override
    def get_theme_list(self) -> List[str]:
        return ["default"] + list(self._theme_struct_dict.keys())

    @override
    def _get_theme_object(self, theme_name: str) -> Theme:
        return self._theme_struct_dict[theme_name].theme

    @override
    def _get_stylesheet(self, theme_name: str) -> str:
        qss_files = self._theme_struct_dict[theme_name].qss_files
        stylesheet = ""
        for qss_file in qss_files:
            stylesheet += qss_file.read_text()
        return stylesheet

    @override
    def _get_icons_dir(self, theme_name: str) -> str:
        return str(self._theme_struct_dict[theme_name].theme_dir)

    @staticmethod
    def _filter_and_proceed_structures(
        theme_structs: List[StaticThemeDirectoryStructure], advanced_filter=True
    ) -> List[StaticThemeDirectoryStructure]:
        filtered_structures = filter(
            StaticQtStyleTools._is_structure_valid, theme_structs
        )
        processed_structures = StaticQtStyleTools._proceed_structures(
            list(filtered_structures)
        )
        if advanced_filter:
            processed_structures = StaticQtStyleTools._advanced_filter_structures(
                processed_structures
            )
        return processed_structures

    @staticmethod
    def _is_structure_valid(theme_struct: StaticThemeDirectoryStructure) -> bool:
        """
        Validates a theme structure by checking for the existence of QSS files, a valid theme file, and a valid theme directory.

        Args:
            theme_struct (StaticThemeDirectoryStructure): The theme structure to validate.

        Returns:
            bool: True if the theme structure is valid, False otherwise.
        """

        if theme_struct.qss_files is None or len(theme_struct.qss_files) == 0:
            logging.debug(
                f"No QSS files found in theme directory '{theme_struct.theme_dir}'"
            )
            return False

        if theme_struct.theme is None or (
            isinstance(theme_struct.theme, Path) and not theme_struct.theme.is_file()
        ):
            logging.debug(f"Invalid theme file '{theme_struct.theme}'")
            return False

        try:
            BuiltInIconDirValidator.validate(str(theme_struct.theme_dir))
        except Exception as e:
            logging.debug(f"Invalid theme directory '{theme_struct.theme_dir}': {e}")
            return False
        return True

    @staticmethod
    def _proceed_structures(
        theme_structs: List[StaticThemeDirectoryStructure],
    ) -> List[StaticThemeDirectoryStructure]:
        """
        Processes a list of theme structures by attempting to replace their themes with
        Theme objects if the theme is a file path.

        Args:
            theme_structs (List[StaticThemeDirectoryStructure]): A list of theme structures to process.

        Returns:
            List[StaticThemeDirectoryStructure]: A list of theme structures with updated themes.
        """
        proceed_structures = []

        for theme_struct in theme_structs:
            try:
                if isinstance(theme_struct.theme, Path):
                    theme_json = json.loads(theme_struct.theme.read_text())
                    theme_object = Theme(theme_json)
                    proceed_structures.append(theme_struct.replace_theme(theme_object))
                else:
                    proceed_structures.append(theme_struct)
            except Exception as e:
                logging.debug(
                    f"Failed to proceed theme structure '{theme_struct}': {e}"
                )
                continue
        return proceed_structures

    @staticmethod
    def _advanced_filter_structures(
        theme_structs: List[StaticThemeDirectoryStructure],
    ) -> List[StaticThemeDirectoryStructure]:
        """
        Filters out theme structures that do not have exactly one template QSS file or whose
        theme values are not found in the template QSS files.

        Args:
            theme_structs (List[StaticThemeDirectoryStructure]): A list of theme structures to filter.

        Returns:
            List[StaticThemeDirectoryStructure]: A list of filtered theme structures.
        """
        filtered_structures = []

        for theme_struct in theme_structs:
            template_qss_files = [
                qss_file
                for qss_file in theme_struct.qss_files
                if StaticQtStyleTools.is_rendered_from_builtin_template(qss_file)
            ]
            if len(template_qss_files) != 1:
                logging.warning(
                    f"Multiple template QSS files found in theme '{theme_struct.theme_name}': {template_qss_files}"
                )

            theme = theme_struct.theme
            regex = StaticQtStyleTools._generate_regex_for_theme_values(theme)
            for template_qss_file in template_qss_files:  # Ensure the file exists
                try:
                    with template_qss_file.open("r", encoding="utf-8") as file:
                        qss_content = file.read()
                except Exception as e:
                    logging.error(f"Failed to read QSS file '{template_qss_file}': {e}")
                    continue

                missing_values = [
                    value
                    for key, value in theme.colors.items()
                    if key != "activeColor" and value and not regex.search(qss_content)
                ]

                if missing_values:
                    logging.warning(
                        f"Theme '{theme_struct.theme_name}' is invalid: Missing values {missing_values} in template '{template_qss_file}'."
                    )
                else:
                    filtered_structures.append(theme_struct)
                    break
        return filtered_structures

    @staticmethod
    def _generate_regex_for_theme_values(theme: Theme) -> re.Pattern:
        # Collect all values except 'activeColor'
        values_to_match = [
            re.escape(value)
            for key, value in theme.colors.items()
            if key != "activeColor" and value
        ]
        # Join the values into a single regex pattern
        pattern = r"|".join(values_to_match)
        return re.compile(pattern)

    @staticmethod
    def _convert_to_dict(
        theme_structs: List[StaticThemeDirectoryStructure],
    ) -> Dict[str, StaticThemeDirectoryStructure]:
        StaticQtStyleTools._verify_unique_theme_names(theme_structs)
        return {theme.theme_name: theme for theme in theme_structs}

    @staticmethod
    def _verify_unique_theme_names(
        theme_structs: List[StaticThemeDirectoryStructure],
    ) -> None:
        seen = set()
        for theme_struct in theme_structs:
            if theme_struct.theme_name in seen:
                raise ValueError(
                    f"Duplicate theme_name found: {theme_struct.theme_name}"
                )
            seen.add(theme_struct.theme_name)


# ----------------------------------------------------------------------
# Class to
# ----------------------------------------------------------------------
class DynamicQtStyleTools(QtStyleTools):

    def __init__(self, app_name: Optional[str] = None):
        super().__init__()

        self._app_name = app_name

        self._icon_generator: BuiltInIconGenerator = BuiltInIconGenerator()
        self._style_renderer: StyleSheetRenderer = StyleSheetRenderer()
        self._theme_manager: ThemeManager = ThemeManager()
        self._extra: ExtraAttributes = ExtraAttributes()
        self._init = True

    def set_extra(
        self, extra: Optional[Dict[str, Union[str, Dict[str, str], None]]] = None
    ) -> None:
        """
        Sets extra attributes for the style tools.

        Args:
            extra (Optional[Dict[str, Union[str, Dict[str, str], None]]]): 
                A dictionary of extra attributes to update. If None, an empty
                dictionary is used.

        Raises:
            TypeError: If the provided 'extra' is not a dictionary.
        """
        if extra is None:
            extra = {}
        if not isinstance(extra, dict):
            raise TypeError("Extra must be an instance of dict.")

        self._extra = self._extra.with_updated_values(extra)

    def set_theme_dir(self, theme_dir: Optional[str] = None) -> None:
        """
        Sets the theme directory.

        Args:
            theme_dir: The directory containing the theme JSON files. If None, the
                default theme directory will be used.

        Raises:
            ValueError: If theme_dir is None and the default theme directory does not
                exist.
        """
        self._theme_manager.set_theme_dir(theme_dir)

    @override
    def get_theme_list(self) -> List[str]:
        return ["default"] + [
            theme.stem for theme in self._theme_manager.get_theme_list()
        ]

    @override
    def _get_theme_object(self, theme_name: str) -> Theme:
        return self._theme_manager.load_theme(theme_name)

    @override
    def _get_stylesheet(self, theme_name: str) -> str:
        theme = self._get_theme_object(theme_name)
        self._icon_generator.generate_dynamically(theme, self._app_name)
        return self._style_renderer.render(theme, self._extra)

    @override
    def _get_icons_dir(self, _: str) -> str:
        return str(self._icon_generator.get_dynamic_icons_dir(self._app_name))
