import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Union

from qt_stylehelper.core.utils import ValidateUtils, ResourcePathUtils
from qt_stylehelper.themes.models import Theme


class ThemeManager:
    def __init__(self, include_builtin=True):
        self._theme_files: Dict[str, Path] = {}
        if include_builtin:
            self.add_themes_from_dir(ResourcePathUtils.themes_dir())

    def add_themes_from_dir(self, directory: Union[str, Path]) -> None:
        """
        Add all .json themes from a directory.

        Args:
            directory (Union[str, Path]): Path to a directory containing .json theme files.
        """
        dir_path = Path(directory)
        ValidateUtils.ensure_directory_exists(dir_path)

        for file_path in dir_path.glob("*.json"):
            self._theme_files[file_path.stem] = file_path

    def add_theme_from_file(self, file_path: Union[str, Path]) -> None:
        """
        Add a single .json theme file from any location.

        Args:
            file_path (Union[str, Path]): Full path to a theme file.
        """
        path = Path(file_path)
        if not path.exists() or path.suffix != ".json":
            raise ValueError(f"Invalid theme file: {path}")
        self._theme_files[path.stem] = path

    def get_theme_list(self) -> List[Path]:
        """
        Get the list of available theme names.
        """
        return sorted(self._theme_files.values())

    def load_theme(self, theme_name: str) -> Optional[Theme]:
        """
        Load the Theme object by its registered name.
        """
        theme_path = self._theme_files.get(theme_name)
        if theme_path and theme_path.exists():
            return self._load_theme_from_file(theme_path)

        # fallback to builtin
        return self.load_builtin_theme(theme_name)

    @staticmethod
    def load_builtin_theme(theme_name: str) -> Optional[Theme]:
        """
        Load a built-in theme by name (fallback method).
        """
        theme_path = ResourcePathUtils.themes_dir() / f"{theme_name}.json"
        if not theme_path.exists():
            logging.error(f"Built-in theme '{theme_name}' not found.")
            return None
        return ThemeManager._load_theme_from_file(theme_path)

    @staticmethod
    def _load_theme_from_file(theme_path: Path) -> Optional[Theme]:
        """
        Load Theme object from a given JSON file path.

        Args:
            theme_path (Path): Full path to the theme JSON file.

        Returns:
            Optional[Theme]: Parsed Theme object or None if failed.
        """
        try:
            with theme_path.open("r", encoding="utf-8") as file:
                theme_data = json.load(file)

            if not isinstance(theme_data, dict):
                raise TypeError(
                    f"Expected JSON object in '{theme_path}', got {type(theme_data).__name__}"
                )

            return Theme.from_dict(theme_data)

        except Exception as e:
            logging.error(f"Failed to load theme from '{theme_path}': {e}")
            return None

    @staticmethod
    def get_builtin_theme_list() -> List[Path]:
        """
        Returns a list of built-in theme files.
        """
        return sorted(ResourcePathUtils.themes_dir().glob("*.json"))
