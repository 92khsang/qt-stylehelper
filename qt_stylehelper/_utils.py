import re
import platform
from pathlib import Path


def get_platform_resource_dir_path(app_name: str) -> Path:
	"""
	Gets the path to a directory suitable for storing resources for a given
	application name on the current platform.

	Args:
		app_name (str): The name of the application.

	Returns:
		Path: The path to the directory on the current platform.

	Raises:
		ValueError: If the app name contains prohibited characters.
		NotImplementedError: If the platform is not supported.
	"""
	if not is_valid_filename(app_name):
		raise ValueError(
			f"Invalid app name: {app_name}. Contains prohibited characters."
		)

	os_name = platform.system()
	if os_name == "Windows":
		return Path.home() / "AppData" / "Local" / app_name
	elif os_name == "Darwin":
		return Path.home() / "Library" / "Application Support" / app_name
	elif os_name == "Linux":
		return Path.home() / ".local" / "share" / app_name
	else:
		raise NotImplementedError("Unsupported platform.")


def is_valid_filename(filename: str) -> bool:
	"""
	Checks if a given string is a valid filename.

	A valid filename is one that does not contain any of the following characters:
		<>:"/\\|?*

	Args:
		filename (str): The string to check.

	Returns:
		bool: True if the string is a valid filename, False otherwise.
	"""
	invalid_chars = '<>:"/\\|?*'
	return filename and not any(char in filename for char in invalid_chars)


def is_valid_6_digit_hex_color(value: str) -> bool:
	"""
	Checks if a given string is a valid 6-digit hexadecimal color code.

	A valid 6-digit hexadecimal color code is one that matches the following pattern:
		^#[0-9A-Fa-f]{6}$

	Args:
		value (str): The string to check.

	Returns:
		bool: True if the string is a valid 6-digit hexadecimal color code, False otherwise.
	"""
	pattern = r"^#[0-9A-Fa-f]{6}$"
	return bool(re.match(pattern, value))


def validate_dir_path(dir_path: Path) -> None:
	if not dir_path.is_dir():
		raise FileNotFoundError(
			f"Directory '{dir_path}' does not exist or is not a directory."
		)
