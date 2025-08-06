from __future__ import annotations as _annotations

from pathlib import Path
from typing import List, Optional, Union, TYPE_CHECKING, override

from qt_stylehelper.themes.icon import BuiltInIconGenerator
from qt_stylehelper.themes.manager import ThemeManager
from qt_stylehelper.themes.models import ExtraAttribute, AttrDict
from qt_stylehelper.themes.stylesheet import StyleSheetRenderer
from .base import QtStyleTool

if TYPE_CHECKING:
    from qt_stylehelper.themes.models import Theme


class DynamicQtStyleTool(QtStyleTool):

    def __init__(self, app_name: Optional[str] = None):
        super().__init__()
        self._app_name = app_name
        self._icon_generator = BuiltInIconGenerator()
        self._style_renderer = StyleSheetRenderer()
        self._theme_manager = ThemeManager()
        self._extra = ExtraAttribute()

    def update_extra_attribute(
        self,
        extra: Optional[Union[ExtraAttribute, AttrDict]] = None,
    ) -> None:
        """
        Sets or updates extra style attributes.

        Args:
            extra (Optional[ExtraAttribute | dict]):
                Additional attributes to update. If None, no update is applied.

        Raises:
            TypeError: If the input is not a dictionary or ExtraAttribute.
        """
        if extra is None:
            return

        if isinstance(extra, dict):
            self._extra = self._extra.with_updated_values(extra)
        elif isinstance(extra, ExtraAttribute):
            self._extra = self._extra.with_updated_values(extra.values)

    @override
    def add_theme(self, path: Union[str, Path]) -> None:
        """
        Registers a theme file or all theme files from a directory via ThemeManager.

        Args:
            path (Union[str, Path]): The path to a single theme JSON file or a directory
                containing multiple theme JSON files.

        Raises:
            ValueError: If the path is neither a valid file nor a directory.
        """
        path = Path(path)

        if path.is_dir():
            self._theme_manager.add_themes_from_dir(path)
        elif path.is_file():
            self._theme_manager.add_theme_from_file(path)
        else:
            raise ValueError(f"Invalid theme path: {path}")

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
