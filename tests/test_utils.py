import unittest
from pathlib import Path
from unittest.mock import patch

from qt_stylehelper._utils import (
	get_platform_resource_dir_path, is_valid_6_digit_hex_color, is_valid_filename, validate_dir_path,
)


class TestGetPlatformResourceDirPath(unittest.TestCase):
	@patch("qt_stylehelper._utils.platform.system")
	def test_windows_path(self, mock_platform):
		mock_platform.return_value = "Windows"
		app_name = "TestApp"
		expected_path = Path.home() / "AppData" / "Local" / app_name
		self.assertEqual(get_platform_resource_dir_path(app_name), expected_path)

	@patch("qt_stylehelper._utils.platform.system")
	def test_darwin_path(self, mock_platform):
		mock_platform.return_value = "Darwin"
		app_name = "TestApp"
		expected_path = Path.home() / "Library" / "Application Support" / app_name
		self.assertEqual(get_platform_resource_dir_path(app_name), expected_path)

	@patch("qt_stylehelper._utils.platform.system")
	def test_linux_path(self, mock_platform):
		mock_platform.return_value = "Linux"
		app_name = "TestApp"
		expected_path = Path.home() / ".local" / "share" / app_name
		self.assertEqual(get_platform_resource_dir_path(app_name), expected_path)

	def test_invalid_app_name(self):
		with self.assertRaises(ValueError):
			get_platform_resource_dir_path("Invalid/Name")

	@patch("qt_stylehelper._utils.platform.system")
	def test_unsupported_platform(self, mock_platform):
		mock_platform.return_value = "UnsupportedOS"
		with self.assertRaises(NotImplementedError):
			get_platform_resource_dir_path("TestApp")


class TestIsValidFilename(unittest.TestCase):

	def test_valid_filename(self):
		self.assertTrue(is_valid_filename("valid_filename"))

	def test_invalid_filename_with_colon(self):
		self.assertFalse(is_valid_filename("invalid:filename"))

	def test_invalid_filename_with_slash(self):
		self.assertFalse(is_valid_filename("invalid/filename"))

	def test_invalid_filename_with_backslash(self):
		self.assertFalse(is_valid_filename("invalid\\filename"))

	def test_empty_filename(self):
		self.assertFalse(is_valid_filename(""))


class TestIsValid6DigitHexColor(unittest.TestCase):

	def test_valid_hex_color(self):
		self.assertTrue(is_valid_6_digit_hex_color("#1a2b3c"))

	def test_uppercase_hex_color(self):
		self.assertTrue(is_valid_6_digit_hex_color("#A1B2C3"))

	def test_invalid_hex_color_short(self):
		self.assertFalse(is_valid_6_digit_hex_color("#abc"))

	def test_invalid_hex_color_wrong_chars(self):
		self.assertFalse(is_valid_6_digit_hex_color("#1g2h3i"))

	def test_invalid_hex_color_no_hash(self):
		self.assertFalse(is_valid_6_digit_hex_color("123456"))


class TestValidateDirPath(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.temp_dir = Path("temp_test_dir")
		cls.temp_dir.mkdir(exist_ok=True)

	@classmethod
	def tearDownClass(cls):
		cls.temp_dir.rmdir()

	def test_existing_dir(self):
		try:
			validate_dir_path(self.temp_dir)
		except FileNotFoundError:
			self.fail("validate_dir_path raised FileNotFoundError unexpectedly!")

	def test_nonexistent_dir(self):
		with self.assertRaises(FileNotFoundError):
			validate_dir_path(self.temp_dir / "nonexistent_subdir")
