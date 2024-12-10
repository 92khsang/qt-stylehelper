import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

from qt_stylehelper import QWidget, StaticQtStyleTools, StaticThemeDirectoryStructure
from qt_stylehelper.value_object import Theme


class TestStaticQtStyleTools(unittest.TestCase):
	def setUp(self):
		"""Set up common resources for the tests."""
		self.style_tools = StaticQtStyleTools()
		self.mock_theme_dir = MagicMock(spec=Path)
		self.mock_theme_dir.is_dir.return_value = True

	@patch("qt_stylehelper.Path")
	@patch("qt_stylehelper.StaticThemeDirectoryStructure")
	def test_auto_init(self, mock_static_theme_directory_structure, mock_path):
		"""Test the auto initialization process."""
		# Mock directory scanning
		# from qt_stylehelper.tools import StaticQtStyleTools
		mock_theme_struct = MagicMock(spec=StaticThemeDirectoryStructure)
		mock_theme_struct.theme_name = "mock_theme"
		self.style_tools.scan_theme_dir = MagicMock(return_value=[mock_theme_struct])
		self.style_tools.manual_init = MagicMock()

		# Call the method
		theme_parent_dir = "/mock/themes"
		self.style_tools.auto_init(theme_parent_dir)

		# Assertions
		self.style_tools.scan_theme_dir.assert_called_with(theme_parent_dir)
		self.style_tools.manual_init.assert_called_with([mock_theme_struct])

	@patch("qt_stylehelper.StaticThemeDirectoryStructure")
	def test_manual_init_with_valid_structures(self, mock_static_theme_directory_structure):
		"""Test manual initialization with valid theme structures."""
		# Mock valid theme structures
		mock_theme_struct = MagicMock(spec=StaticThemeDirectoryStructure)
		mock_theme_struct.theme_name = "mock_theme"
		self.style_tools._verify_unique_theme_names = MagicMock()
		self.style_tools._filter_and_proceed_structures = MagicMock(
			return_value=[mock_theme_struct]
		)
		self.style_tools._convert_to_dict = MagicMock(return_value={"mock_theme": mock_theme_struct})

		# Call the method
		self.style_tools.manual_init([mock_theme_struct])

		# Assertions
		self.style_tools._verify_unique_theme_names.assert_called()
		self.style_tools._filter_and_proceed_structures.assert_called()
		self.style_tools._convert_to_dict.assert_called()

	def test_apply_stylesheet_invalid_theme(self):
		"""Test applying a stylesheet with an invalid theme."""

		with patch("sys.modules", {"PySide6": MagicMock()}):
			self.style_tools._init = True
			self.style_tools.get_theme_list = MagicMock(return_value=["default", "dark"])
			with self.assertRaises(ValueError):
				self.style_tools.apply_stylesheet(None, "nonexistent_theme")


	@patch("qt_stylehelper.QtHandler")
	def test_apply_stylesheet_valid_theme(self, mock_qt_handler):
		"""Test applying a valid stylesheet."""
		with patch("sys.modules", {"PySide6": MagicMock()}):
			self.style_tools._init = True

			self.style_tools._current_theme = "default"

			self.style_tools.get_theme_list = MagicMock(return_value=["default", "dark"])
			self.style_tools._get_theme_object = MagicMock()
			self.style_tools._get_stylesheet = MagicMock(return_value="mock_stylesheet")
			self.style_tools._get_icons_dir = MagicMock(return_value="/mock/icons")

			widget_mock = MagicMock(spec=QWidget)

			# Call with valid theme
			self.style_tools.apply_stylesheet(widget_mock, "dark")

			# Assertions
			self.style_tools._get_stylesheet.assert_called_with("dark")
			mock_qt_handler.apply_stylesheet.assert_called_with(widget_mock, "mock_stylesheet")
			mock_qt_handler.add_search_paths.assert_called_with(resource_dir="/mock/icons")

	def test_is_rendered_from_builtin_template(self):
		"""Test detection of templates rendered from the built-in template."""
		with patch("builtins.open", mock_open(read_data="mock data")):
			result = self.style_tools.is_rendered_from_builtin_template(Path("mock.qss"))
			self.assertFalse(result)  # Adjust the expected result based on your logic.

	def test_generate_regex_for_theme_values(self):
		"""Test regex generation for matching theme values."""
		mock_theme = MagicMock()
		mock_theme.colors = {"activeColor": None, "primary": "#FFFFFF", "secondary": "#000000"}
		regex = StaticQtStyleTools._generate_regex_for_theme_values(mock_theme)
		self.assertTrue(regex.search("#FFFFFF"))
		self.assertTrue(regex.search("#000000"))
		self.assertFalse(regex.search("#123456"))

	def test_require_init_decorator(self):
		"""Test the @require_init decorator."""
		with patch("sys.modules", {"PySide6": MagicMock()}):
			self.style_tools._init = False

			with self.assertRaises(RuntimeError):
				# noinspection PyTypeChecker
				self.style_tools.apply_stylesheet(None, "default")

			self.style_tools._init = True
			with self.assertRaises(ValueError):
				try:
					# noinspection PyTypeChecker
					self.style_tools.apply_stylesheet(None, "default")
				except RuntimeError:
					self.fail("apply_stylesheet() raised RuntimeError unexpectedly when initialized.")

	def test_verify_unique_theme_names(self):
		"""Test the verification of unique theme names."""
		theme1 = MagicMock(spec=StaticThemeDirectoryStructure)
		theme2 = MagicMock(spec=StaticThemeDirectoryStructure)
		theme1.theme_name = "theme1"
		theme2.theme_name = "theme2"

		# Should pass without exception
		self.style_tools._verify_unique_theme_names([theme1, theme2])

		# Add duplicate theme name
		theme3 = MagicMock(spec=StaticThemeDirectoryStructure)
		theme3.theme_name = "theme1"

		with self.assertRaises(ValueError):
			self.style_tools._verify_unique_theme_names([theme1, theme3])

	@patch("qt_stylehelper.Path")
	def test_scan_theme_dir(self, mock_path):
		"""Test scanning a directory for theme structures."""
		self.style_tools._init = True

		mock_theme_parent_dir = mock_path("/mock/themes")
		mock_theme_dir_1 = mock_path("/mock/themes/theme1")
		mock_theme_dir_2 = mock_path("/mock/themes/theme2")
		mock_theme_dir_1.is_dir.return_value = True
		mock_theme_dir_2.is_dir.return_value = True

		mock_theme_parent_dir.iterdir.return_value = [mock_theme_dir_1, mock_theme_dir_2]
		mock_qss_file = mock_path("theme1.qss")
		mock_qss_file.is_file.return_value = True
		mock_theme_dir_1.glob.return_value = [mock_qss_file]

		# Call the method
		result = self.style_tools.scan_theme_dir(mock_theme_parent_dir)

		# Assertions
		self.assertTrue(len(result) == 2)
		self.assertTrue(all(isinstance(struct, StaticThemeDirectoryStructure) for struct in result))

	def test_convert_to_dict_with_duplicates(self):
		"""Test dictionary conversion with duplicate theme names."""
		theme_struct1 = MagicMock(spec=StaticThemeDirectoryStructure)
		theme_struct2 = MagicMock(spec=StaticThemeDirectoryStructure)
		theme_struct1.theme_name = "theme1"
		theme_struct2.theme_name = "theme1"  # Duplicate name

		with self.assertRaises(ValueError):
			self.style_tools._convert_to_dict([theme_struct1, theme_struct2])

	def test_get_stylesheet_multiple_files(self):
		"""Test stylesheet generation from multiple QSS files."""
		mock_qss_file_1 = MagicMock()
		mock_qss_file_1.read_text.return_value = "/* File 1 styles */"

		mock_qss_file_2 = MagicMock()
		mock_qss_file_2.read_text.return_value = "/* File 2 styles */"

		theme_struct = MagicMock(spec=StaticThemeDirectoryStructure)
		theme_struct.qss_files = [mock_qss_file_1, mock_qss_file_2]

		self.style_tools._theme_struct_dict = {"theme1": theme_struct}

		result = self.style_tools._get_stylesheet("theme1")

		self.assertIn("/* File 1 styles */", result)
		self.assertIn("/* File 2 styles */", result)

	def test_verify_unique_theme_names_valid(self):
		"""Test unique theme name verification."""
		theme1 = MagicMock(spec=StaticThemeDirectoryStructure)
		theme2 = MagicMock(spec=StaticThemeDirectoryStructure)
		theme1.theme_name = "theme1"
		theme2.theme_name = "theme2"

		# Should not raise an exception
		try:
			self.style_tools._verify_unique_theme_names([theme1, theme2])
		except ValueError:
			self.fail("_verify_unique_theme_names raised ValueError unexpectedly.")

	@patch("qt_stylehelper.QtHandler")
	def test_apply_stylesheet_same_theme(self, mock_qt_handler):
		"""Test applying the same theme does nothing."""
		with patch("sys.modules", {"PySide6": MagicMock()}):
			self.style_tools._init = True

			self.style_tools._current_theme = "dark"
			self.style_tools.get_theme_list = MagicMock(return_value=["dark", "default"])

			widget_mock = MagicMock(spec=QWidget)
			self.style_tools.apply_stylesheet(widget_mock, "dark")

			# Ensure no operations were performed
			mock_qt_handler.apply_stylesheet.assert_not_called()

	def test_generate_regex_for_theme_values_complex(self):
		"""Test regex generation with complex theme values."""
		mock_theme = MagicMock()
		mock_theme.colors = {"primary": "rgba(255, 255, 255, 0.8)", "secondary": "#ABCDEF"}
		regex = StaticQtStyleTools._generate_regex_for_theme_values(mock_theme)

		self.assertTrue(regex.search("rgba(255, 255, 255, 0.8)"))
		self.assertTrue(regex.search("#ABCDEF"))
		self.assertFalse(regex.search("#123456"))

	@patch("qt_stylehelper.StaticQtStyleTools._advanced_filter_structures")
	@patch("qt_stylehelper.StaticQtStyleTools._proceed_structures")
	@patch("qt_stylehelper.StaticQtStyleTools._is_structure_valid")
	def test_filter_and_proceed_structures(self, mock_is_structure_valid, mock_proceed_structures,
	                                       mock_advanced_filter_structures):
		invalid_struct = MagicMock(spec=StaticThemeDirectoryStructure)
		invalid_struct.qss_files = []
		invalid_struct.theme = None
		invalid_struct.theme_dir = MagicMock(spec=Path)

		valid_struct = MagicMock(spec=StaticThemeDirectoryStructure)
		valid_struct.qss_files = [MagicMock(spec=Path)]
		valid_struct.theme = MagicMock(spec=Path)
		valid_struct.theme_dir = MagicMock(spec=Path)

		mock_is_structure_valid.side_effect = lambda struct: struct == valid_struct
		mock_proceed_structures.return_value = [valid_struct]
		mock_advanced_filter_structures.return_value = [valid_struct]

		result = self.style_tools._filter_and_proceed_structures([invalid_struct, valid_struct])

		self.assertEqual(len(result), 1)
		self.assertEqual(result[0], valid_struct)
		mock_proceed_structures.assert_called_once_with([valid_struct])
		mock_advanced_filter_structures.assert_called_once()
		mock_is_structure_valid.assert_any_call(invalid_struct)
		mock_is_structure_valid.assert_any_call(valid_struct)

	def test_proceed_structures(self):
		"""Test _proceed_structures method with valid and invalid themes."""
		# Mock a valid structure
		valid_struct = MagicMock(spec=StaticThemeDirectoryStructure)
		valid_struct.theme = MagicMock(spec=Path)
		valid_struct.theme.read_text.return_value = """{
            "primaryColor": "#ffd740",
            "primaryLightColor": "#ffff74",
            "secondaryColor": "#232629",
            "secondaryLightColor": "#4f5b62",
            "secondaryDarkColor": "#31363b",
            "primaryTextColor": "#000000",
            "secondaryTextColor": "#ffffff"
        }"""
		valid_struct.replace_theme.return_value = valid_struct

		# Mock an invalid structure
		invalid_struct = MagicMock(spec=StaticThemeDirectoryStructure)
		invalid_struct.theme = MagicMock(spec=Path)
		invalid_struct.theme.read_text.side_effect = Exception("Invalid JSON")

		# Call the method under test
		result = self.style_tools._proceed_structures([valid_struct, invalid_struct])

		# Assertions
		self.assertEqual(len(result), 1)
		self.assertEqual(result[0], valid_struct)
		valid_struct.theme.read_text.assert_called_once()
		valid_struct.replace_theme.assert_called_once()
		invalid_struct.theme.read_text.assert_called_once()

	@patch("qt_stylehelper.StaticQtStyleTools.is_rendered_from_builtin_template")
	@patch("qt_stylehelper.StaticQtStyleTools._generate_regex_for_theme_values")
	def test_advanced_filter_structures(self, mock_generate_regex, mock_is_rendered):
		# Mock QSS files
		valid_qss_file = MagicMock(spec=Path)
		valid_qss_file.open.return_value.__enter__.return_value.read.return_value = "/* Valid QSS #FFFFFF #000000 */"

		invalid_qss_file = MagicMock(spec=Path)
		invalid_qss_file.open.side_effect = Exception("File not found")

		# Mock valid structure
		valid_struct = MagicMock(spec=StaticThemeDirectoryStructure)
		valid_struct.qss_files = [valid_qss_file]
		valid_struct.theme = MagicMock(spec=Theme)
		valid_struct.theme.colors = {"primary": "#FFFFFF", "secondary": "#000000"}
		valid_struct.theme_name = "valid_theme"

		# Mock invalid structure
		invalid_struct = MagicMock(spec=StaticThemeDirectoryStructure)
		invalid_struct.qss_files = [invalid_qss_file]
		invalid_struct.theme = MagicMock(spec=Theme)
		invalid_struct.theme.colors = {"primary": None}
		invalid_struct.theme_name = "invalid_theme"

		# Mock `is_rendered_from_builtin_template`
		mock_is_rendered.side_effect = lambda qss_file: qss_file == valid_qss_file

		# Mock `_generate_regex_for_theme_values` to return a regex for the valid theme
		import re
		mock_generate_regex.side_effect = lambda theme: re.compile(
			"|".join(re.escape(value) for key, value in theme.colors.items() if key != "activeColor" and value)
		)

		# Call the method
		result = self.style_tools._advanced_filter_structures([valid_struct, invalid_struct])

		# Assertions
		self.assertEqual(len(result), 1)
		self.assertEqual(result[0], valid_struct)
		mock_is_rendered.assert_any_call(valid_qss_file)
		mock_is_rendered.assert_any_call(invalid_qss_file)
		mock_generate_regex.assert_any_call(valid_struct.theme)
		valid_qss_file.open.assert_called_once()
		mock_generate_regex.assert_any_call(invalid_struct.theme)
		invalid_qss_file.open.assert_not_called()

	def test_generate_regex_for_theme_values(self):
		mock_theme = MagicMock()
		mock_theme.colors = {
			"primary"    : "#FFFFFF",
			"secondary"  : "#000000",
			"activeColor": None,
		}

		regex = self.style_tools._generate_regex_for_theme_values(mock_theme)

		# Assertions
		self.assertTrue(regex.search("#FFFFFF"))
		self.assertTrue(regex.search("#000000"))
		self.assertFalse(regex.search("#123456"))
