import sys

from PySide6 import QtWidgets

from qt_stylehelper import DynamicQtStyleTools

# create the application and the main window
app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QMainWindow()

dynamic_style_tools = DynamicQtStyleTools(app_name="qt_stylehelper")
# dynamic_style_tools.apply_stylesheet(window, "dark_teal")
dynamic_style_tools.apply_stylesheet(window, "light_cyan_500")

# run
window.show()

if hasattr(app, 'exec'):
	app.exec()
else:
	app.exec_()
