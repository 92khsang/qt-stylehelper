import json
import logging
from pathlib import Path
from typing import List, Optional, Union

from .value_object import Theme
from ._utils import validate_dir_path


class ThemeManager:
    def __init__(self, theme_dir: Optional[str] = None):
        self.theme_dir_path = self._convert_theme_dir_to_path(theme_dir)

    def set_theme_dir(self, theme_dir: Optional[str] = None) -> None:
        self.theme_dir_path = self._convert_theme_dir_to_path(theme_dir)

    def get_theme_list(self) -> List[Path]:
        color_theme_files = list(self.theme_dir_path.iterdir())
        color_themes = filter(lambda a: a.suffix == ".json", color_theme_files)
        return sorted(list(color_themes))

    def load_theme(self, theme_name: str) -> Union[Theme, None]:
        """
        Loads a color theme from a file in the theme directory.

        Args:
			theme_name (str): Name of the theme without the .json extension.

        Returns:
			Theme: Theme object with the loaded color theme, or None if the theme file does not exist or could not be loaded.
        """

        theme_file_name = (
            theme_name if theme_name.endswith(".json") else f"{theme_name}.json"
        )
        theme_file = Path(self.theme_dir_path) / theme_file_name
        try:
            if not theme_file.exists():
                logging.error(f"Color theme '{theme_name}' not found.")
                return None
            with theme_file.open("r", encoding="utf-8") as file:
                theme_json = json.loads(file.read())
                return Theme(theme_json)
        except Exception as e:
            logging.error(f"Error loading color theme '{theme_name}': {e}")
            return None

    @staticmethod
    def _convert_theme_dir_to_path(theme_dir: Optional[str] = None) -> Path:
        theme_dir_path = (
            Path(theme_dir) if theme_dir else Path(__file__).resolve().parent / "themes"
        )
        validate_dir_path(theme_dir_path)
        return theme_dir_path
