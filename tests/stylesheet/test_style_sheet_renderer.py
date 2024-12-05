import unittest
from unittest.mock import MagicMock, patch

import jinja2

from qt_stylehelper._stylesheet import ExtraAttributes, StyleSheetRenderer, Theme


class TestStyleSheetRenderer(unittest.TestCase):
	def setUp(self):
		self.theme = Theme(colors={
			"primaryColor"       : "#123456",
			"primaryLightColor"  : "#abcdef",
			"secondaryColor"     : "#654321",
			"secondaryLightColor": "#fedcba",
			"secondaryDarkColor" : "#0f0f0f",
			"primaryTextColor"   : "#f0f0f0",
			"secondaryTextColor" : "#1a1a1a",
		})
		self.extra = ExtraAttributes(extra={"density_scale": "1"})

	@patch("qt_stylehelper._stylesheet.jinja2.Environment.get_template")
	def test_render_valid(self, mock_get_template):
		renderer = StyleSheetRenderer()
		mock_template = MagicMock()
		mock_get_template.return_value = mock_template
		mock_template.render.return_value = "rendered-css"

		result = renderer.render(self.theme, self.extra)
		self.assertEqual(result, "rendered-css")
		mock_template.render.assert_called_once()

	@patch("qt_stylehelper._stylesheet.Path.exists", return_value=False)
	def test_init_invalid_template_path(self, mock_exists):
		with self.assertRaises(FileNotFoundError):
			StyleSheetRenderer(template_file="invalid/path/to/template.css")

	@patch("qt_stylehelper._stylesheet.jinja2.Environment.get_template")
	def test_load_template_error(self, mock_get_template):
		renderer = StyleSheetRenderer()
		mock_get_template.side_effect = jinja2.TemplateError("Load error")
		with self.assertRaises(RuntimeError):
			renderer._load_template()

	@patch("qt_stylehelper._stylesheet.jinja2.Environment.get_template")
	def test_render_invalid_theme(self, mock_get_template):
		renderer = StyleSheetRenderer()
		with self.assertRaises(ValueError):
			renderer.render(None, self.extra)

	@patch("qt_stylehelper._stylesheet.jinja2.Environment.get_template")
	def test_render_invalid_extra(self, mock_get_template):
		renderer = StyleSheetRenderer()
		with self.assertRaises(ValueError):
			renderer.render(self.theme, None)

	@patch("qt_stylehelper._stylesheet.jinja2.Environment.get_template")
	def test_render_template_error(self, mock_get_template):
		renderer = StyleSheetRenderer()

		mock_template = MagicMock()
		mock_get_template.return_value = mock_template
		mock_template.render.side_effect = jinja2.TemplateError("Render error")

		with self.assertRaises(RuntimeError):
			renderer.render(self.theme, self.extra)

	@patch("qt_stylehelper._stylesheet.Path.exists", return_value=True)
	@patch("qt_stylehelper._stylesheet.Path.is_file", return_value=False)
	def test_init_template_not_a_file(self, mock_is_file, mock_exists):
		with self.assertRaises(FileNotFoundError):
			StyleSheetRenderer(template_file="path/to/directory")
