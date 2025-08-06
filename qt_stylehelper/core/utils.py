import platform
import re
from functools import lru_cache
from importlib.abc import Traversable
from importlib.resources import as_file, files
from pathlib import Path


class PlatformUtils:
    @staticmethod
    def get_app_data_dir(app_name: str) -> Path:
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
        if not ValidateUtils.is_valid_filename(app_name):
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


class ValidateUtils:
    @staticmethod
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

    @staticmethod
    def is_valid_hex_color(value: str) -> bool:
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

    @staticmethod
    def ensure_directory_exists(dir_path: Path) -> None:
        if not dir_path.is_dir():
            raise FileNotFoundError(
                f"Directory '{dir_path}' does not exist or is not a directory."
            )


class QtBindingUtils:
    _initialized = False
    _detected_backend: str | None = None
    _qt_available: bool = False

    @classmethod
    def _detect_backend(cls) -> None:
        if cls._initialized:
            return

        from importlib.util import find_spec

        for backend in ["PySide6"]:
            if find_spec(backend):
                cls._detected_backend = backend
                cls._qt_available = True
                break

        cls._initialized = True

    @classmethod
    def is_available(cls) -> bool:
        cls._detect_backend()
        return cls._qt_available

    @classmethod
    def get_backend(cls) -> str | None:
        cls._detect_backend()
        return cls._detected_backend


class ResourcePathUtils:
    """
    Memory-optimized utility class for accessing resource paths within the qt_stylehelper package.
    Uses caching to minimize repeated resource lookups and memory allocation.
    """

    _BASE_PACKAGE = "qt_stylehelper.resources"

    @classmethod
    @lru_cache(maxsize=1)
    def base_dir(cls) -> Traversable:
        """
        Returns the root resource directory.
        Cached to avoid repeated package lookups.
        """
        return files(cls._BASE_PACKAGE)

    @classmethod
    @lru_cache(maxsize=1)
    def themes_dir(cls) -> Path:
        """
        Returns the theme directory path.
        Cached to avoid repeated path resolution.
        """
        with as_file(cls.base_dir() / "themes") as path:
            return path

    @classmethod
    @lru_cache(maxsize=1)
    def icons_dir(cls) -> Path:
        """
        Returns the icon directory path.
        Cached to avoid repeated path resolution.
        """
        with as_file(cls.base_dir() / "icons") as path:
            return path

    @classmethod
    @lru_cache(maxsize=1)
    def template_file(cls) -> Path:
        """
        Returns the template file path.
        Cached to avoid repeated path resolution.
        """
        with as_file(cls.base_dir() / "template" / "material.css.jinja2") as path:
            return path

    @classmethod
    def clear_cache(cls) -> None:
        """
        Clear all cached paths. Useful for testing or when resources change.
        """
        cls.base_dir.cache_clear()
        cls.themes_dir.cache_clear()
        cls.icons_dir.cache_clear()
        cls.template_file.cache_clear()
