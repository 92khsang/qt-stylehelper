import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

from qt_stylehelper import ICON_URL_PREFIX, StyleSheetExporter


class TestStyleSheetExporter(unittest.TestCase):
	@patch("qt_stylehelper._stylesheet.Path.mkdir")
	@patch("qt_stylehelper._stylesheet.StyleSheetExporter._save_qss_file")
	@patch("qt_stylehelper._stylesheet.StyleSheetExporter._generate_qrc_file")
	def test_export_valid(self, mock_generate_qrc, mock_save_qss, mock_mkdir):
		StyleSheetExporter.export(
			stylesheet="body { background: red; }",
			destination_dir="destination",
			qss_name="test.qss",
			qrc_name="test.qrc",
		)
		mock_mkdir.assert_called_once()
		mock_save_qss.assert_called_once()
		mock_generate_qrc.assert_called_once()

	@patch("qt_stylehelper._stylesheet.Path.mkdir", side_effect=Exception("Mkdir error"))
	def test_export_mkdir_error(self, mock_mkdir):
		with self.assertRaises(Exception):
			StyleSheetExporter.export(stylesheet="body {}", destination_dir="destination")

	@patch("builtins.open", new_callable=mock_open)
	def test_save_qss_file(self, mock_file):
		StyleSheetExporter._save_qss_file(
			Path("destination"), "body {}", "_stylesheet:/", "stylesheet.qss"
		)
		mock_file.assert_called_once_with(Path("destination") / "stylesheet.qss", "w")

	@patch("builtins.open", new_callable=mock_open)
	def test_generate_qrc_file(self, mock_file):
		sub_folders = ["primary"]
		StyleSheetExporter._generate_qrc_file(
			Path("destination"),
			Path("destination") / "test.qrc",
			"_stylesheet:/",
			"stylesheet.qss",
			sub_folders=sub_folders,
		)
		mock_file.assert_called_once_with(Path("destination") / "test.qrc", "w")

	@patch("qt_stylehelper._stylesheet.Path.mkdir")
	def test_export_invalid__stylesheet_url_prefix(self, mock_mkdir):
		with self.assertRaises(TypeError):
			StyleSheetExporter.export(
				stylesheet="body {}",
				destination_dir="destination",
				_stylesheet_url_prefix="invalid_url_prefix",
				qss_name="test.qss",
			)

	@patch("builtins.open", new_callable=mock_open)
	def test_save_qss_file_replacement(self, mock_file):
		stylesheet = f"background: url('{ICON_URL_PREFIX}some-_stylesheet');"
		replacement_prefix = "custom:/"

		StyleSheetExporter._save_qss_file(
			Path("destination"), stylesheet, replacement_prefix, "stylesheet.qss"
		)
		mock_file().writelines.assert_called_once_with(
			"background: url('custom:/some-_stylesheet');"
		)

	@patch("builtins.open", new_callable=mock_open)
	def test_generate_qrc_file_with_files(self, mock_file):
		with patch.object(Path, "iterdir", return_value=[Path("file1.svg"), Path("file2.svg")]) as mock_iterdir, \
				patch.object(Path, "is_dir", return_value=True) as mock_is_dir, \
				patch.object(Path, "is_file", return_value=True) as mock_is_file, \
				patch.object(Path, "exists", return_value=True) as mock_exists:
			output_dir_name = "output"

			# Call the code under test
			sub_folders = ["primary"]
			StyleSheetExporter._generate_qrc_file(
				Path(output_dir_name),
				Path(output_dir_name) / "test.qrc",
				"_stylesheet:/",
				"stylesheet.qss",
				sub_folders=sub_folders,
			)

		mock_file().write.assert_called_once_with(
			"<RCC>\n"
			'  <qresource prefix="_stylesheet">\n'
			f"    <file>{output_dir_name}/{sub_folders[0]}/file1.svg</file>\n"
			f"    <file>{output_dir_name}/{sub_folders[0]}/file2.svg</file>\n"
			"  </qresource>\n"
			'  <qresource prefix="file">\n'
			"    <file>stylesheet.qss</file>\n"
			"  </qresource>\n"
			"</RCC>"
		)
