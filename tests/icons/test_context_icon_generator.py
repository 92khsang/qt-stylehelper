import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from qt_stylehelper.icon import ContextIconGenerator


class TestContextIconGenerator(unittest.TestCase):

	def setUp(self):
		"""Setup the ContextIconGenerator instance and test variables."""
		self.generator = ContextIconGenerator("#0000ff", "#ff0000")
		self.theme = MagicMock()
		self.theme.colors = {
			"primaryColor"       : "#00bcd4",
			"secondaryColor"     : "#62efff",
			"secondaryLightColor": "#ffffff",
			"activeColor"        : "#707070",
		}
		self.source_dir = "test_source"
		self.destination_dir = "test_destination"

	@patch("qt_stylehelper.icon.Path.open")
	@patch("qt_stylehelper.icon.replace_color")
	def test_process_svg(self, mock_replace_color, mock_open):
		"""Test the _process_svg method with proper Path.open patching."""
		svg_file = Path("icon.svg")
		output_dir = Path("output")
		replace_main_color = "#00bcd4"
		replace_sub_color = "#62efff"

		# Simulate file read and write behavior
		mock_open.return_value.__enter__.return_value.read.return_value = "svg_content"

		# Mock replace_color to simulate replacing colors
		mock_replace_color.side_effect = lambda content, old_color, new_color: content.replace(old_color, new_color)

		# Call the method
		self.generator._process_svg(
			svg_file=svg_file,
			output_dir=output_dir,
			replace_main_color=replace_main_color,
			replace_sub_color=replace_sub_color,
		)

		# Assert replace_color calls
		mock_replace_color.assert_any_call("svg_content", "#0000ff", "#00bcd4")
		mock_replace_color.assert_any_call("svg_content", "#ff0000", "#62efff")

		# Validate the output file was written with modified content
		mock_open.return_value.__enter__.return_value.write.assert_called_once_with("svg_content")

	@patch("qt_stylehelper.icon.Path.open")
	def test_process_svg_integration(self, mock_open):
		svg_file = Path("icon.svg")
		output_dir = Path("output")
		replace_main_color = "#00bcd4"
		replace_sub_color = "#62efff"

		original_svg_content = """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path fill="#0000ff" d="M12 0L24 12L12 24L0 12z"/>
            <circle fill="#ff0000" cx="12" cy="12" r="10"/>
        </svg>
        """
		expected_svg_content = """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path fill="#00bcd4" d="M12 0L24 12L12 24L0 12z"/>
            <circle fill="#62efff" cx="12" cy="12" r="10"/>
        </svg>
        """

		mock_open.return_value.__enter__.return_value.read.return_value = original_svg_content

		self.generator._process_svg(
			svg_file=svg_file,
			output_dir=output_dir,
			replace_main_color=replace_main_color,
			replace_sub_color=replace_sub_color,
		)

		mock_open.return_value.__enter__.return_value.write.assert_called_once_with(expected_svg_content)

	@patch("qt_stylehelper.icon.Path.is_dir")
	@patch("qt_stylehelper.icon.Path.rglob")
	@patch("qt_stylehelper.icon.Path.mkdir")
	@patch("qt_stylehelper.icon.Path.open")
	def test_generate_valid_dirs(self, mock_open, mock_mkdir, mock_rglob, mock_is_dir):
		mock_is_dir.return_value = True
		mock_rglob.return_value = [Path("icon1.svg"), Path("icon2.svg")]
		mock_open.return_value.__enter__.return_value.read.return_value = "svg_content"

		self.generator.generate(self.theme, self.source_dir, self.destination_dir)

		mock_rglob.assert_called_once_with("*.svg")
		mock_mkdir.assert_any_call(parents=True, exist_ok=True)
		mock_open.assert_called()

	def test_generate_missing_dirs(self):
		"""Test generate method when source or destination directories are missing."""
		with self.assertRaises(ValueError) as context:
			self.generator.generate(self.theme)

		self.assertEqual(
			str(context.exception), "Both source_dir and destination_dir must be provided."
		)

	@patch("qt_stylehelper.icon.Path.rglob")
	def test_get_all_icon_files(self, mock_rglob):
		"""Test the _get_all_icon_files method."""
		mock_rglob.return_value = [Path("icon1.svg"), Path("icon2.svg")]

		icon_files = self.generator._get_all_icon_files(Path(self.source_dir))

		mock_rglob.assert_called_once_with("*.svg")
		self.assertEqual(len(icon_files), 2)
		self.assertIn(Path("icon1.svg"), icon_files)
		self.assertIn(Path("icon2.svg"), icon_files)
