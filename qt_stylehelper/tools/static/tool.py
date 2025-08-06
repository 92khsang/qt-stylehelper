import json
import logging
import re
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, override, Union

from qt_stylehelper.core.utils import ValidateUtils, ResourcePathUtils
from qt_stylehelper.themes.icon import BuiltInIconDirValidator
from qt_stylehelper.themes.models import Theme
from qt_stylehelper.tools.base import QtStyleTool
from qt_stylehelper.tools.static.structs import StaticThemeStruct


class StaticQtStyleTool(QtStyleTool):
    def __init__(self):
        super().__init__()
        self._themes: Dict[str, StaticThemeStruct] = {}

    @override
    def add_theme(self, path: Union[str, Path]) -> None:
        """
        Registers a theme from a directory.

        Args:
            path (Union[str, Path]): The path to a directory containing resources.

        Raises:
            ValueError: If the path is neither a directory.
        """
        path = Path(path)
        if not path.is_dir():
            raise ValueError(f"Only directory paths are supported: {path}")

        theme_struct = self._build_theme_struct(path)
        self._themes[theme_struct.theme_name] = theme_struct

    @override
    def get_theme_list(self) -> List[str]:
        """
        Returns a list of available themes.

        Returns:
            List[str]: A list of theme names.
        """
        return list(self._themes.keys())

    @override
    def _get_theme_object(self, theme_name: str) -> Theme:
        return self._themes[theme_name].theme

    @override
    def _get_stylesheet(self, theme_name: str) -> str:
        return "".join(file.read_text() for file in self._themes[theme_name].qss_files)

    @override
    def _get_icons_dir(self, theme_name: str) -> str:
        return str(self._themes[theme_name].theme_dir)

    # ---------- Internal Methods ----------
    def _build_theme_struct(self, theme_dir: Path) -> StaticThemeStruct:
        ValidateUtils.ensure_directory_exists(theme_dir)

        qss_files = self._collect_qss_files(theme_dir)
        theme_json_path = theme_dir / f"{theme_dir.name}.json"

        struct = StaticThemeStruct(
            theme=theme_json_path,
            theme_dir=theme_dir,
            theme_name=theme_dir.name,
            qss_files=qss_files,
        )

        self._validate_theme_dir(struct)
        struct = self._load_theme_object(struct)
        self._validate_theme_contents(struct)

        return struct

    def _collect_qss_files(self, theme_dir: Path) -> List[Path]:
        return sorted(
            theme_dir.glob("*.qss"),
            key=lambda f: not self._is_template_rendered(f),
        )

    def _validate_theme_dir(self, struct: StaticThemeStruct) -> None:
        if not struct.qss_files:
            raise ValueError(f"No QSS files found in: {struct.theme_dir}")

        if isinstance(struct.theme, Path) and not struct.theme.is_file():
            raise ValueError(f"Theme JSON file not found: {struct.theme}")

        BuiltInIconDirValidator.validate(str(struct.theme_dir))

    def _load_theme_object(self, struct: StaticThemeStruct) -> StaticThemeStruct:
        if isinstance(struct.theme, Path):
            try:
                data = json.loads(struct.theme.read_text(encoding="utf-8"))
                theme = Theme.from_dict(data)
                return struct.replace_theme(theme)
            except Exception as e:
                logging.debug(f"Failed to parse theme '{struct.theme_name}': {e}")
        return struct

    def _validate_theme_contents(self, struct: StaticThemeStruct) -> None:
        template_qss = [f for f in struct.qss_files if self._is_template_rendered(f)]

        if len(template_qss) != 1:
            raise ValueError(
                f"Expected one rendered QSS in '{struct.theme_name}', found: {template_qss}"
            )

        regex = self._build_theme_value_regex(struct.theme)
        content = template_qss[0].read_text()

        missing = [
            val
            for key, val in asdict(struct.theme).items()
            if key != "activeColor" and val and not regex.search(content)
        ]

        if missing:
            raise ValueError(
                f"Missing values in QSS for '{struct.theme_name}': {missing}"
            )

    def _is_template_rendered(self, qss_file: Path) -> bool:
        """Checks if a given QSS file is rendered from the default Jinja2 template."""
        # The approach here is to compare the top 4 lines of the file to the top 4
        # lines of the default Jinja2 template. These lines are the copy-right
        # comments and should only be changed if the template is modified.
        # If the files are the same, the QSS file is rendered from the default
        # Jinja2 template.

        if not qss_file or not qss_file.is_file():
            logging.debug(f"Skipping invalid QSS file: {qss_file}")
            return False

        try:
            with (
                qss_file.open("r", encoding="utf-8") as qf,
                ResourcePathUtils.template_file().open("r", encoding="utf-8") as tf,
            ):
                return all(
                    next(qf, "").strip() == next(tf, "").strip() for _ in range(4)
                )
        except Exception as e:
            logging.debug(f"Template comparison failed: {e}")
            return False

    def _build_theme_value_regex(self, theme: "Theme") -> re.Pattern:
        values = [
            re.escape(v) for k, v in theme.to_dict().items() if k != "activeColor" and v
        ]
        return re.compile("|".join(values))
