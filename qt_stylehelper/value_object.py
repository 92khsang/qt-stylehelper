from dataclasses import dataclass, field
from typing import Dict, Union

from ._utils import is_valid_6_digit_hex_color


@dataclass(frozen=True)
class Theme:
	# Define the expected keys as a private constant
	__COLOR_KEY = [
		"primaryColor",
		"primaryLightColor",
		"secondaryColor",
		"secondaryLightColor",
		"secondaryDarkColor",
		"primaryTextColor",
		"secondaryTextColor",
		"activeColor",
	]

	# Field to store the validated colors
	colors: Dict[str, str]

	def __init__(self, colors: Dict[str, str]):
		if not isinstance(colors, dict):
			raise TypeError("Colors must be a dictionary.")

		# Set default for "activeColor" if not provided
		colors = {**colors, "activeColor": colors.get("activeColor", "#707070")}

		# Validate the colors dictionary
		self.validate_colors(colors)

		# Use object.__setattr__ to assign immutable values
		object.__setattr__(self, "colors", colors)

	@classmethod
	def validate_colors(cls, colors: Dict[str, str]):
		"""Validates that all required keys exist and all values are valid hex colors."""
		missing_keys = [key for key in cls.__COLOR_KEY if key not in colors]
		if missing_keys:
			raise ValueError(f"Missing key(s): {', '.join(missing_keys)}")

		for key, value in colors.items():
			if not is_valid_6_digit_hex_color(value):
				raise ValueError(f"{key} has an invalid color value: {value}")


@dataclass(frozen=True)
class ExtraAttributes:
	# Private default attributes (used internally for value resolution)
	__DEFAULT_ATTRIBUTES = {
		'icon'         : None,
		'font_family'  : 'Source Sans Pro, Arial, sans-serif',  # Adjusted for Jinja/CSS
		'danger'       : '#dc3545',
		'warning'      : '#ffc107',
		'success'      : '#17a2b8',
		'density_scale': 0.0,
		'button_shape' : 'default',
	}

	# Field to store extra attributes provided during initialization
	extra: Dict[str, Union[str, float, Dict[str, str]]] = field(default_factory=dict)

	def __post_init__(self):
		qmenu_data = self.extra.get('QMenu')
		if qmenu_data is not None and not isinstance(qmenu_data, dict):
			raise ValueError("'QMenu' must be a dictionary if provided in 'extra'.")

	@property
	def values(self) -> Dict[str, Union[str, float, None]]:
		"""
		Combines default attributes with processed extra attributes, returning the final values.
		"""
		return {**self.__DEFAULT_ATTRIBUTES, **self._process_extras(self.extra)}

	@staticmethod
	def _process_extras(extra: Dict[str, Union[str, float, Dict[str, str]]]) -> Dict[str, Union[str, float, None]]:
		"""
		Processes extra attributes, specifically handling 'QMenu' keys.
		If 'QMenu' is a dictionary, prefixes its keys with 'qmenu_'.
		"""
		processed = extra.copy()

		qmenu_data = processed.get('QMenu')
		if isinstance(qmenu_data, dict):
			for key, value in qmenu_data.items():
				processed[f'qmenu_{key}'] = value
			processed['QMenu'] = 'true'
		elif 'QMenu' in processed and not isinstance(qmenu_data, dict):
			raise ValueError("'QMenu' must be a dictionary if provided in 'extra'.")

		density_scale = processed.get('density_scale')
		if density_scale is not None and not isinstance(density_scale, float):
			processed['density_scale'] = float(density_scale)

		return processed

	def with_updated_values(self, new_values: Dict[str, Union[str, float, Dict[str, str]]]) -> 'ExtraAttributes':
		"""
		Returns a new instance with updated values.
		"""
		updated_extra = {**self.extra, **new_values}
		return ExtraAttributes(extra=updated_extra)

	def get_value(self, key: str, default: Union[str, float, None] = None) -> Union[str, float, None]:
		"""
		Safely retrieves a value from `values`, returning the default if the key does not exist.
		"""
		return self.values.get(key, default)
