import inspect
import json
import logging
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from qt_stylehelper import ThemeManager
from qt_stylehelper.value_object import Theme


class TestInitializeThemeManager(unittest.TestCase):

	def test_initialize_without_dir(self):
		"""Test ThemeManager initialization without a theme directory."""
		manager = ThemeManager()
		module_path = inspect.getfile(manager.__class__)
		expect_path = Path(module_path).resolve().parent / 'themes'
		self.assertEqual(manager.theme_dir_path, expect_path)

	@patch("qt_stylehelper._theme.Path.is_dir", return_value=True, autospec=True)
	def test_initialize_with_valid_dir(self, mock_is_dir):
		"""Test ThemeManager initialization with a valid theme directory."""
		mock_theme_dir = "/mock/themes"
		manager = ThemeManager(mock_theme_dir)
		self.assertEqual(manager.theme_dir_path, Path(mock_theme_dir))

		mock_is_dir.assert_called_once_with(Path(mock_theme_dir))

	def test_initialize_with_invalid_dir(self):
		"""Test ThemeManager initialization with an invalid theme directory."""
		with self.assertRaises(FileNotFoundError):
			ThemeManager("/invalid/path")


@patch("qt_stylehelper._theme.validate_dir_path")
class TestThemeManager(unittest.TestCase):
	def setUp(self):
		"""Set up a ThemeManager instance with a mock theme directory."""
		self.mock_theme_dir = "/mock/themes"
		self.valid_theme_content = {
			"primaryColor"       : "#ffd740",
			"primaryLightColor"  : "#ffff74",
			"secondaryColor"     : "#232629",
			"secondaryLightColor": "#4f5b62",
			"secondaryDarkColor" : "#31363b",
			"primaryTextColor"   : "#000000",
			"secondaryTextColor" : "#ffffff",
		}

	def test_set_theme_dir(self, _):
		"""Test setting a valid theme directory."""
		theme_manager = ThemeManager(self.mock_theme_dir)

		with patch("qt_stylehelper._theme.Path.is_dir", return_value=True):
			theme_manager.set_theme_dir("/new/theme/dir")
			self.assertEqual(theme_manager.theme_dir_path, Path("/new/theme/dir"))

	@patch("qt_stylehelper._theme.Path.iterdir", return_value=[
		Path("theme1.json"), Path("theme2.json"), Path("not_a_theme.txt")
	])
	def test_get_theme_list(self, mock_iterdir, _):
		"""Test retrieving the list of available themes."""
		theme_manager = ThemeManager(self.mock_theme_dir)
		themes = theme_manager.get_theme_list()
		self.assertEqual(themes, [Path("theme1.json"), Path("theme2.json")])
		mock_iterdir.assert_called_once()

	@patch("qt_stylehelper._theme.Path.iterdir", return_value=[])
	def test_get_theme_list_no_json(self, mock_iterdir, _):
		"""Test retrieving themes when no .json files exist."""
		theme_manager = ThemeManager(self.mock_theme_dir)
		themes = theme_manager.get_theme_list()
		self.assertEqual(themes, [])
		mock_iterdir.assert_called_once()

	@patch("qt_stylehelper._theme.Path.exists", return_value=True)
	@patch("qt_stylehelper._theme.Path.open", new_callable=MagicMock)
	def test_load_theme_valid(self, mock_open, mock_exists, _):
		"""Test loading a valid theme."""
		theme_manager = ThemeManager(self.mock_theme_dir)
		mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(self.valid_theme_content)
		theme = theme_manager.load_theme("valid_theme")
		self.assertIsInstance(theme, Theme)
		self.assertEqual(theme.colors["primaryColor"], "#ffd740")
		mock_exists.assert_called_once()
		mock_open.assert_called_once()

	@patch("qt_stylehelper._theme.Path.exists", return_value=False)
	def test_load_theme_not_found(self, mock_exists, _):
		"""Test loading a theme that does not exist."""
		theme_manager = ThemeManager(self.mock_theme_dir)
		theme = theme_manager.load_theme("missing_theme")
		self.assertIsNone(theme)
		mock_exists.assert_called_once()

	@patch("qt_stylehelper._theme.Path.exists", return_value=True)
	@patch("qt_stylehelper._theme.Path.open", side_effect=Exception("Invalid JSON"))
	def test_load_theme_invalid_json(self, mock_open, mock_exists, _):
		"""Test loading a theme with invalid JSON."""
		theme_manager = ThemeManager(self.mock_theme_dir)
		with self.assertLogs(level=logging.ERROR) as log:
			theme = theme_manager.load_theme("invalid_json_theme")
			self.assertIsNone(theme)
			self.assertIn("Error loading color theme", log.output[0])
		mock_exists.assert_called_once()
		mock_open.assert_called_once()

	def test_convert_theme_dir_to_path(self, _):
		"""Test converting theme directory to a Path."""
		theme_manager = ThemeManager(self.mock_theme_dir)
		with patch("qt_stylehelper._theme.Path.is_dir", return_value=True):
			path = theme_manager._convert_theme_dir_to_path("/custom/path")
			self.assertEqual(path, Path("/custom/path"))
