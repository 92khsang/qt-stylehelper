import argparse
import json
import logging
import sys
from abc import abstractmethod, ABCMeta
from multiprocessing import freeze_support
from pathlib import Path
from typing import TYPE_CHECKING, cast, List, Dict, override

from black.trans import Callable

from qt_stylehelper import (
    QtBindingUtils,
    QtStyleTool,
    ExtraAttribute,
    Theme,
    StaticStyleGenerator,
)

if QtBindingUtils.get_backend() == "PySide6":
    from PySide6.QtWidgets import (
        QApplication,
        QMainWindow,
        QFileDialog,
        QMenu,
        QListWidget,
        QPushButton,
        QToolBar,
        QTableWidget,
        QDockWidget,
        QWidget,
        QCheckBox,
        QColorDialog,
    )
    from PySide6.QtCore import Qt, QCoreApplication
    from PySide6.QtGui import QIcon, QActionGroup, QAction, QColor
    from PySide6.QtUiTools import QUiLoader
else:
    logging.error("must install PySide6")
    sys.exit()


ASSET_PATH: Path = Path(__file__).parent / "assets"


class QMainWindowABCMeta(type(QMainWindow), ABCMeta):
    pass


class AbsMainWindow(QMainWindow, metaclass=QMainWindowABCMeta):
    if TYPE_CHECKING:
        main: QMainWindow
        menu_styles: QMenu
        menu_density: QMenu
        action_toolbar: QAction
        list_widget_2: QListWidget
        file_button: QPushButton
        folder_button: QPushButton
        vertical_toolbar: QToolBar
        table_widget: QTableWidget
        table_widget_2: QTableWidget
        extra: ExtraAttribute
        style_tool: QtStyleTool

    # ----------------------------------------------------------------------
    def __init__(self, style_tool: QtStyleTool):
        """Constructor"""
        super().__init__()

        if QtBindingUtils.get_backend() == "PySide6":
            self.main = cast(
                QMainWindow, QUiLoader().load(ASSET_PATH / "main_window.ui", self)
            )
            wt = "PySide6"
        else:
            logging.error("must install PySide6")
            sys.exit()

        self._init_ui_references()

        self.extra = ExtraAttribute()
        self.style_tool = style_tool

        self.main.setWindowTitle(f"{self.main.windowTitle()} - {wt}")

        self.custom_styles()

        self.add_menu_theme()
        self.add_menu_density()
        self.show_dock_theme()

        self.style_tool.update_resource_prefix(str(ASSET_PATH / "logo"), "logo")
        logo = QIcon("logo:/logo.svg")
        logo_frame = QIcon("logo:/logo.svg")

        self.main.setWindowIcon(logo)
        self.action_toolbar.setIcon(logo)
        [
            self.list_widget_2.item(i).setIcon(logo_frame)
            for i in range(self.list_widget_2.count())  # noqa
        ]

        self.file_button.clicked.connect(  # noqa
            lambda: QFileDialog.getOpenFileName(self.main)
        )
        self.folder_button.clicked.connect(  # noqa
            lambda: QFileDialog.getExistingDirectory(self.main)
        )

    # noinspection PyUnresolvedReferences
    def _init_ui_references(self):
        self.menu_styles = self.main.menuStyles
        self.menu_density = self.main.menuDensity
        self.action_toolbar = self.main.actionToolbar
        self.list_widget_2 = self.main.listWidget_2
        self.file_button = self.main.pushButton_file_dialog
        self.folder_button = self.main.pushButton_folder_dialog
        self.vertical_toolbar = self.main.toolBar_vertical
        self.table_widget = self.main.tableWidget
        self.table_widget_2 = self.main.tableWidget_2

    def custom_styles(self):
        for i in range(self.vertical_toolbar.layout().count()):
            tool_button = self.vertical_toolbar.layout().itemAt(i).widget()
            tool_button.setMaximumWidth(150)
            tool_button.setMinimumWidth(150)

        for r in range(self.table_widget.rowCount()):
            self.table_widget.setRowHeight(r, 36)

        for r in range(self.table_widget_2.rowCount()):
            self.table_widget_2.setRowHeight(r, 36)

    def add_menu_theme(self):
        """Initialize the menu bar and populate it with style options."""
        style_action_group = QActionGroup(self.menu_styles)
        style_action_group.setExclusive(True)

        for theme_name in self.get_theme_name_list():
            action = QAction(theme_name, style_action_group)
            action.triggered.connect(
                lambda checked, theme=theme_name: self.apply_theme(theme)
            )

            self.menu_styles.addAction(action)

    def add_menu_density(self):
        density_action_group = QActionGroup(self.menu_density)
        density_action_group.setExclusive(True)

        for density in range(-2, 3):
            action = QAction(str(density), density_action_group)
            action.triggered.connect(
                lambda checked, density_scale=density: self.apply_density(density_scale)
            )
            self.menu_density.addAction(action)

    def show_dock_theme(self):
        dock_theme = ThemeDockWidget(self.main, self.apply_new_theme)
        dock_theme.setFloating(False)
        self.main.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock_theme)

    @abstractmethod
    def apply_theme(self, theme_name: str):
        pass

    @abstractmethod
    def apply_density(self, density_scale: float):
        pass

    @abstractmethod
    def get_theme_name_list(self) -> List[str]:
        pass

    @abstractmethod
    def apply_new_theme(self, theme_name: str, theme: Theme) -> None:
        pass


class ThemeDockWidget(QDockWidget):
    if TYPE_CHECKING:
        light_theme_checkbox: QCheckBox

    def __init__(self, parent: QWidget, apply_new_theme: Callable[[str, Theme], None]):
        super().__init__(parent)
        self.apply_new_theme = apply_new_theme

        self.custom_colors: Dict[str, str] = {
            color: "#ffffff" for color in list(Theme.keys(True))
        }

        ui_path = str(ASSET_PATH / "dock_theme.ui")
        self.ui = QUiLoader().load(ui_path, self)

        self._init_ui_references()
        self._setup_connections()

        self.update_buttons()

    # noinspection PyUnresolvedReferences
    def _init_ui_references(self):
        self.light_theme_checkbox = self.ui.checkBox_ligh_theme

    def _setup_connections(self):
        self.light_theme_checkbox.clicked.connect(self.update_theme)
        for color in list(Theme.keys(True)):
            button = getattr(self.ui, f"pushButton_{color}", None)
            if button:
                button.clicked.connect(self._create_color_picker(color))

    def _create_color_picker(self, color_key: str):
        def pick_color():
            initial = QColor(self.custom_colors.get(color_key, "#ffffff"))
            dialog = QColorDialog(self)
            dialog.setCurrentColor(initial)
            if dialog.exec():
                selected_color = dialog.currentColor()
                if selected_color.isValid():
                    hex_color = "#{:02x}{:02x}{:02x}".format(
                        selected_color.red(),
                        selected_color.green(),
                        selected_color.blue(),
                    )
                    self.custom_colors[color_key] = hex_color
                    self.update_theme()

        return pick_color

    def update_buttons(self):
        temp_colors = self.custom_colors.copy()

        if self.light_theme_checkbox.isChecked():
            (
                temp_colors["secondaryColor"],
                temp_colors["secondaryLightColor"],
                temp_colors["secondaryDarkColor"],
            ) = (
                temp_colors["secondaryColor"],
                temp_colors["secondaryDarkColor"],
                temp_colors["secondaryLightColor"],
            )

        for color_key in list(Theme.keys(True)):
            button = getattr(self.ui, f"pushButton_{color_key}", None)
            if not button:
                continue

            color = QColor(temp_colors[color_key])
            text_color = "#ffffff" if color.value() < 128 else "#000000"

            button.setStyleSheet(
                f"""
                * {{
                    background-color: {color.name()};
                    color: {text_color};
                    border: none;
                }}
                """
            )

    def update_theme(self):
        self.apply_new_theme("my_theme", Theme.from_dict(self.custom_colors))
        self.update_buttons()


class DynamicMainWindow(AbsMainWindow):

    def __init__(self):
        from qt_stylehelper import DynamicQtStyleTool

        super().__init__(DynamicQtStyleTool())

    def apply_theme(self, theme_name: str):
        self.style_tool.apply_stylesheet(self.main, theme_name)

    def apply_density(self, density_scale: float):
        self.style_tool.update_extra_attribute({"density_scale": density_scale})  # noqa
        self.style_tool.refresh_stylesheet(self.main)

    def get_theme_name_list(self) -> List[str]:
        return self.style_tool.get_theme_list()

    def apply_new_theme(self, theme_name: str, theme: Theme) -> None:
        theme_json = Path(theme_name + ".json")
        theme_json.write_text(json.dumps(theme.to_dict(), indent=2))

        self.style_tool.add_theme(theme_json)
        self.style_tool.apply_stylesheet(self.parent, theme_name)


class StaticMainWindow(AbsMainWindow):

    def __init__(self):
        from qt_stylehelper import StaticQtStyleTool

        super().__init__(StaticQtStyleTool())

    @override
    def apply_theme(self, theme_name: str):
        output_dir: Path = Path().cwd() / "resources"
        StaticStyleGenerator.generate_from_builtin(theme_name, self.extra, output_dir)
        self.style_tool.add_theme(output_dir / theme_name)
        self.style_tool.apply_stylesheet(self.main, theme_name)

    @override
    def apply_density(self, density_scale: float):
        self.extra = self.extra.with_updated_values({"density_scale": density_scale})
        output_dir: Path = Path().cwd() / "resources"
        StaticStyleGenerator.generate_from_builtin(
            self.style_tool.current_theme_name, self.extra, output_dir
        )
        self.style_tool.refresh_stylesheet(self.main)

    @override
    def get_theme_name_list(self) -> List[str]:
        return StaticStyleGenerator.get_builtin_theme_list()

    @override
    def apply_new_theme(self, theme_name: str, theme: Theme) -> None:
        output_dir: Path = Path().cwd() / "resources"
        StaticStyleGenerator.generate_from_custom(
            theme_name, theme, self.extra, output_dir
        )
        self.style_tool.add_theme(output_dir / theme_name)
        self.style_tool.apply_stylesheet(self.parent, theme_name)


def prepare_qt_app() -> QApplication:
    if hasattr(Qt, "AA_ShareOpenGLContexts"):
        QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    else:
        print("'Qt' object has no attribute 'AA_ShareOpenGLContexts'")

    app = QApplication([])
    freeze_support()
    app.processEvents()
    app.setQuitOnLastWindowClosed(False)
    app.lastWindowClosed.connect(app.quit)
    return app


def main():
    parser = argparse.ArgumentParser(
        description="Run with either 'static' or 'dynamic' mode."
    )

    parser.add_argument(
        "mode",
        choices=["static", "dynamic"],
        help="Execution mode: 'static' or 'dynamic' (required)",
    )

    args = parser.parse_args()

    if args.mode == "static":
        print("Running in STATIC mode...")
        window_cls = StaticMainWindow
    elif args.mode == "dynamic":
        print("Running in DYNAMIC mode...")
        window_cls = DynamicMainWindow
    else:
        raise ValueError("'mode' must be either 'static' or 'dynamic'")

    app = prepare_qt_app()
    window = window_cls()
    window.main.showMaximized()

    if hasattr(app, "exec"):
        app.exec()
    else:
        app.exec_()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Error: Missing required argument 'mode' (static | dynamic)",
            file=sys.stderr,
        )
        sys.exit(1)

    main()
