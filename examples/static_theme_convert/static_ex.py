import sys
from typing import List
from pathlib import Path

from PySide6.QtCore import QFile, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import QApplication, QMainWindow

from qt_stylehelper import (
	StaticBuiltInResourceGenerator,
	StaticQtStyleTools as QtStyleTools,
)

_RESOURCES_DIR = Path(__file__).parent.resolve() / "resources"


def generate_static_theme(theme_names: List[str]):
	for theme_name in theme_names:
		StaticBuiltInResourceGenerator.generate(
			theme_name,
			destination_dir=str(_RESOURCES_DIR)
		)


class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.style_tools = QtStyleTools()
		self.style_tools.auto_init(str(_RESOURCES_DIR))

		self.init_ui()
		self.init_menu()
		self.load_widgets()

	def init_menu(self):
		"""Initialize the menu bar and populate it with style options."""
		menu_bar = self.menuBar()
		style_menu = menu_bar.addMenu("Styles")
		style_action_group = QActionGroup(style_menu)
		style_action_group.setExclusive(True)

		for style_name in self.style_tools.get_theme_list():
			action = QAction(style_name, style_action_group)
			action.triggered.connect(
				lambda checked, style_name=style_name: self.style_tools.apply_stylesheet(self, style_name)
			)
			style_menu.addAction(action)

	def load_ui_file(self, file_path: Path):
		"""Load a .ui file and return the corresponding QWidget."""
		ui_file = QFile(str(file_path))
		ui_file.open(QFile.ReadOnly)
		loader = QUiLoader()
		widget = loader.load(ui_file, self)
		ui_file.close()
		return widget

	def load_widgets(self):
		"""Load the central and toolbar widgets."""
		base_path = Path(__file__).parent.parent / "ui"
		self.setCentralWidget(self.load_ui_file(base_path / "full_widget.ui"))
		toolbar_widget = self.load_ui_file(base_path / "toolbar.ui")
		self.addToolBar(toolbar_widget)
		right_dock_widget = self.load_ui_file(base_path / "right_dock_widget.ui")
		self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, right_dock_widget)
		top_dock_widget = self.load_ui_file(base_path / "top_dock_widget.ui")
		self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, top_dock_widget)

	def init_ui(self):
		"""Set up the main window properties."""
		self.setWindowTitle("Qt Application")


def main():
	theme_names = ["dark_amber", "light_cyan_500"]
	generate_static_theme(theme_names)

	app = QApplication(sys.argv)
	main_window = MainWindow()
	main_window.show()

	# Use `exec` for PySide6 compatibility
	app_exec = getattr(app, 'exec', app.exec_)
	app_exec()


if __name__ == "__main__":
	main()
