import unittest
from unittest.mock import patch

from qt_stylehelper.value_object import Theme


class TestTheme(unittest.TestCase):
	def setUp(self):
		"""Set up common test data."""
		self.valid_colors = {
			"primaryColor"       : "#123456",
			"primaryLightColor"  : "#abcdef",
			"secondaryColor"     : "#654321",
			"secondaryLightColor": "#fedcba",
			"secondaryDarkColor" : "#0f0f0f",
			"primaryTextColor"   : "#f0f0f0",
			"secondaryTextColor" : "#1a1a1a",
		}

	@patch("qt_stylehelper.value_object.is_valid_6_digit_hex_color", return_value=True)
	def test_theme_with_all_keys(self, mock_is_valid_hex):
		"""Test Theme initialization with all required keys."""
		theme = Theme(colors={**self.valid_colors, "activeColor": "#707070"})
		self.assertEqual(theme.colors["activeColor"], "#707070")
		self.assertDictEqual(theme.colors, {**self.valid_colors, "activeColor": "#707070"})

	@patch("qt_stylehelper.value_object.is_valid_6_digit_hex_color", return_value=True)
	def test_theme_missing_keys(self, mock_is_valid_hex):
		"""Test Theme initialization with missing keys."""
		with self.assertRaises(ValueError) as context:
			self.valid_colors.pop("primaryColor")
			Theme(colors=self.valid_colors)  # Missing "primaryColor"
		self.assertIn("Missing key(s):", str(context.exception))

	@patch("qt_stylehelper.value_object.is_valid_6_digit_hex_color")
	def test_theme_invalid_hex_color(self, mock_is_valid_hex):
		"""Test Theme initialization with invalid hex color values."""
		mock_is_valid_hex.side_effect = lambda color: color != "#invalid"
		invalid_colors = {**self.valid_colors, "activeColor": "#invalid"}
		with self.assertRaises(ValueError) as context:
			Theme(colors=invalid_colors)
		self.assertIn("has an invalid color value", str(context.exception))

	def test_theme_default_active_color(self):
		"""Test Theme sets default activeColor if not provided."""
		theme = Theme(colors=self.valid_colors)
		self.assertEqual(theme.colors["activeColor"], "#707070")
