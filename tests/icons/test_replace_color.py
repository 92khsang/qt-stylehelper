import unittest

from qt_stylehelper.icon import replace_color


class TestReplaceColor(unittest.TestCase):

	# Test parameters
	test_parameters = [
		('<path fill="#0000ff" />', "#0000ff", "#00bcd4", '<path fill="#00bcd4" />'),
		('<path fill="#00\n00ff" />', "#0000ff", "#00bcd4", '<path fill="#00bcd4" />'),
		('<path fill="#0000ff" />', "#ff0000", "#00bcd4", '<path fill="#0000ff" />'),
		('<path fill="#0000ff" />', "#0000FF", "#00bcd4", '<path fill="#00bcd4" />'),
		('<path fill="#000000" />', "#0000ff", "#00bcd4", '<path fill="#ffffff00" />'),
	]

	def test_replace_color(self):
		for svg_content, origin_color, replacement, expected_output in self.test_parameters:
			with self.subTest(svg_content=svg_content, origin_color=origin_color, replacement=replacement):
				self.assertEqual(replace_color(svg_content, origin_color, replacement), expected_output)
