import unittest
from unittest.mock import patch

from qt_stylehelper.icon import BuiltInIconDirValidator, ICON_CONTEXT


class MockBuiltInIconDirValidatorTests(unittest.TestCase):

	def setUp(self):
		self.mock_built_in_icon_list_patch = patch(
			"qt_stylehelper.icon.BuiltInIconDirValidator._BuiltInIconDirValidator__BUILT_IN_ICON_LIST",
			{"icon1.svg", "icon2.svg"},
		)
		self.mock_built_in_icon_list_patch.start()

	def tearDown(self):
		self.mock_built_in_icon_list_patch.stop()

	def test_validate_success(self):
		with patch(
				"qt_stylehelper.icon._get_icon_name_list",
				return_value=["icon1.svg", "icon2.svg"],
		):
			with patch("qt_stylehelper.icon.validate_dir_path"):

				def mock_exists(self, *, follow_symlinks=True):
					path_str = str(self)
					if (
							"test_dir" in path_str
							and "test_theme" in path_str
							and any(context in path_str for context in ICON_CONTEXT)
					):
						return True
					return False

				with patch(
						"qt_stylehelper.icon.Path.exists", side_effect=mock_exists, autospec=True
				):
					# Perform the validation
					BuiltInIconDirValidator.validate("test_dir", "test_theme")

	def test_validate_missing_context_dirs(self):
		with patch(
				"qt_stylehelper.icon._get_icon_name_list",
				return_value=["icon1.svg", "icon2.svg"],
		):
			with patch("qt_stylehelper.icon.validate_dir_path"):

				def mock_exists(path):
					if any(context in str(path) for context in ["disabled", "primary"]):
						return True
					return False

				with patch(
						"qt_stylehelper.icon.Path.exists", side_effect=mock_exists, autospec=True
				):
					with self.assertRaises(FileNotFoundError) as context:
						BuiltInIconDirValidator.validate("test_dir", "test_theme")
					self.assertIn(
						"Missing context directories: active", str(context.exception)
					)

	def test_validate_icon_list_missing_icons(self):
		with patch(
				"qt_stylehelper.icon._get_icon_name_list", return_value=["icon1.svg"]
		), patch("qt_stylehelper.icon.validate_dir_path"), patch(
			"qt_stylehelper.icon.Path.exists", return_value=True
		):
			with self.assertRaises(ValueError) as context:
				BuiltInIconDirValidator.validate("test_dir", "test_theme")
			self.assertIn(
				"does not contain all the required icons", str(context.exception)
			)

	def test_validate_invalid_theme_dir(self):
		with patch(
				"qt_stylehelper.icon._get_icon_name_list",
				return_value=["icon1.svg", "icon2.svg"],
		), patch(
			"qt_stylehelper.icon.validate_dir_path",
			side_effect=FileNotFoundError(
				"Directory 'test_dir' does not exist or is not a directory."
			),
		):
			with self.assertRaises(FileNotFoundError) as context:
				BuiltInIconDirValidator.validate("test_dir", "test_theme")

			self.assertIn(
				"Directory 'test_dir' does not exist or is not a directory.",
				str(context.exception),
			)
