from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from qt_stylehelper.themes.models import Theme


@dataclass(frozen=True, slots=True)
class StaticThemeStruct:
    theme: Union[Path, Theme]
    theme_dir: Path
    theme_name: Optional[str] = None
    qss_files: List[Path] = field(default_factory=list)

    def __post_init__(self):
        if self.theme_name is None:
            object.__setattr__(self, "theme_name", self.theme_dir.stem)

    def replace_theme(self, new_theme: Union[Path, Theme]) -> "StaticThemeStruct":
        """
        Return a new instance with an updated theme if it differs.
        """
        if type(new_theme) is not type(self.theme) or new_theme != self.theme:
            return replace(self, theme=new_theme)
        return self

    def replace_qss_files(self, new_qss_files: List[Path]) -> "StaticThemeStruct":
        """
        Return a new instance with updated QSS files if they differ.
        """
        if new_qss_files != self.qss_files:
            return replace(self, qss_files=new_qss_files)
        return self
