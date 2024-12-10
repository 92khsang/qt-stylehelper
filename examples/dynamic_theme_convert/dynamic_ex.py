import sys
from pathlib import Path

if "PySide6" in sys.modules:
	from PySide6.QtCore import QFile, Qt
	from PySide6.QtUiTools import QUiLoader
	from PySide6.QtGui import QAction, QActionGroup
	from PySide6.QtWidgets import QApplication, QMainWindow
else:
	raise Exception(
		"If you intend to use code related to Qt, the corresponding Qt libraries are required."
	)

from qt_stylehelper import DynamicQtStyleTools as QtStyleTools

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.style_tools = QtStyleTools(app_name="qt_stylehelper")
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
			# noinspection PyTypeChecker
			action.triggered.connect(
				lambda checked, style=style_name: self.style_tools.apply_stylesheet(self, style)
			)
			style_menu.addAction(action)
		
		density_menu = menu_bar.addMenu("Densities")
		density_action_group = QActionGroup(density_menu)
		density_action_group.setExclusive(True)

		def update_densities(density_scale):
			self.style_tools.set_extra({"density_scale": density_scale})
			# noinspection PyTypeChecker
			self.style_tools.refresh_stylesheet(self)

		for density in range(-2, 3):
			action = QAction(str(density), density_action_group)
			action.triggered.connect(
				lambda checked, density_scale=density: update_densities(density_scale)
			)
			density_menu.addAction(action)

	def load_ui_file(self, file_path: Path):
		"""Load a .ui file and return the corresponding QWidget."""
		ui_file = QFile(str(file_path))
		ui_file.open(QFile.ReadOnly)
		loader = QUiLoader()
		widget = loader.load(ui_file, self)
		ui_file.close()
		return widget

	# noinspection PyTypeChecker
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
	app = QApplication(sys.argv)
	main_window = MainWindow()
	main_window.show()

	# Use `exec` for PySide6 compatibility
	app_exec = getattr(app, 'exec', app.exec_)
	app_exec()


if __name__ == "__main__":
	main()
