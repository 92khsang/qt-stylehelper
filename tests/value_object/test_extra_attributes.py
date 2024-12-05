import unittest

from qt_stylehelper.value_object import ExtraAttributes


class TestExtraAttributes(unittest.TestCase):
	def setUp(self):
		"""Set up common test data."""
		self.default_extra = {
			'icon'         : None,
			'font_family'  : 'Source Sans Pro, Arial, sans-serif',
			'danger'       : '#dc3545',
			'warning'      : '#ffc107',
			'success'      : '#17a2b8',
			'density_scale': 0,
			'button_shape' : 'default',
		}

	def test_default_values(self):
		"""Test default values with no extra attributes."""
		extra = ExtraAttributes()
		self.assertDictEqual(extra.values, self.default_extra)

	def test_merge_extra_with_defaults(self):
		"""Test merging extra attributes with defaults."""
		extra = ExtraAttributes(extra={"icon": "custom_icon"})
		merged = {**self.default_extra, "icon": "custom_icon"}
		self.assertDictEqual(extra.values, merged)

	def test_qmenu_processing(self):
		"""Test proper processing of QMenu attributes."""
		qmenu_extra = {"QMenu": {"option1": "value1", "option2": "value2"}}
		extra = ExtraAttributes(extra=qmenu_extra)
		expected_values = {
			**self.default_extra,
			"qmenu_option1": "value1",
			"qmenu_option2": "value2",
			"QMenu"        : "true",
		}
		self.assertDictEqual(extra.values, expected_values)

	def test_invalid_qmenu(self):
		"""Test invalid QMenu input."""
		with self.assertRaises(ValueError) as context:
			ExtraAttributes(extra={"QMenu": "invalid_value"})
		self.assertIn("'QMenu' must be a dictionary", str(context.exception))

	def test_with_updated_values(self):
		"""Test updating values with with_updated_values."""
		extra = ExtraAttributes(extra={"icon": "custom_icon"})
		updated = extra.with_updated_values({"density_scale": "1"})
		self.assertEqual(updated.values["density_scale"], 1)
		self.assertEqual(updated.values["icon"], "custom_icon")

	def test_get_value(self):
		"""Test retrieving values with get_value."""
		extra = ExtraAttributes(extra={"icon": "custom_icon"})
		self.assertEqual(extra.get_value("icon"), "custom_icon")
		self.assertEqual(extra.get_value("density_scale"), 0)
		self.assertEqual(extra.get_value("nonexistent_key", "default_value"), "default_value")
