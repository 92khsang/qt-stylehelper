import unittest
from pathlib import Path
from unittest.mock import patch

from qt_stylehelper.value_object import Theme
from qt_stylehelper.icon import BuiltInIconGenerator


class TestBuiltInIconGenerator(unittest.TestCase):
    def setUp(self):
        # Example theme for testing
        self.theme = Theme(
            colors={
                "primaryColor": "#123456",
                "primaryLightColor": "#789abc",
                "secondaryColor": "#abcdef",
                "secondaryLightColor": "#fedcba",
                "secondaryDarkColor": "#654321",
                "primaryTextColor": "#112233",
                "secondaryTextColor": "#445566",
                "activeColor": "#778899",
            }
        )
        self.theme_name = "test_theme"
        self.app_name = "test_app"
        self.destination_dir = "/mock/resources/icons/test_theme"

    @patch(
        "qt_stylehelper.icon.BuiltInIconGenerator.get_dynamic_icons_dir",
        return_value=Path("/mock/resources/icons"),
    )
    @patch.object(BuiltInIconGenerator, "_generate_icons")
    def test_generate_dynamically(
        self, mock_generate_icons, mock_get_dynamic_icons_dir
    ):
        # Call the method
        BuiltInIconGenerator.generate_dynamically(self.theme, app_name=self.app_name)

        # Assertions
        mock_get_dynamic_icons_dir.assert_called_once_with(self.app_name)
        mock_generate_icons.assert_called_once_with(
            self.theme, Path("/mock/resources/icons")
        )

    @patch.object(BuiltInIconGenerator, "_create_destination_dir")
    @patch.object(BuiltInIconGenerator, "_generate_icons")
    def test_generate_statically_with_destination_dir(
        self, mock_generate_icons, mock_create_destination_dir
    ):
        # Call the method
        BuiltInIconGenerator.generate_statically(
            self.theme, destination_dir=self.destination_dir
        )

        # Assertions
        mock_create_destination_dir.assert_called_once_with(Path(self.destination_dir))
        mock_generate_icons.assert_called_once_with(
            self.theme, Path("/mock/resources/icons/test_theme")
        )

    def test_generate_statically_without_destination_dir(self):
        with self.assertRaises(TypeError):
            BuiltInIconGenerator.generate_statically(self.theme)

    @patch("qt_stylehelper.icon.Path.exists", return_value=False, autospec=True)
    @patch("qt_stylehelper.icon.Path.mkdir")
    def test_create_destination_dir(self, mock_mkdir, mock_exists):
        # Call the method
        BuiltInIconGenerator._create_destination_dir(
            destination_dir_path=Path(self.destination_dir)
        )

        # Assertions
        mock_exists.assert_called_once_with(Path(self.destination_dir))
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

        mock_exists.reset_mock()
        mock_mkdir.reset_mock()

        mock_exists.return_value = True
        # Call the method
        BuiltInIconGenerator._create_destination_dir(
            destination_dir_path=Path(self.destination_dir)
        )

        # Assertions
        mock_exists.assert_called_once_with(Path(self.destination_dir))
        mock_mkdir.assert_not_called()

    @patch("qt_stylehelper.icon.ContextIconGenerator.generate")
    @patch("qt_stylehelper.icon.__file__", new="/mock/resources/icons/file.py")
    def test_generate_icons(self, mock_generate):
        # Call the method
        BuiltInIconGenerator._generate_icons(self.theme, Path(self.destination_dir))

        # Assertions
        mock_generate.assert_called_once_with(
            theme=self.theme,
            source_dir=str(
                Path("/mock/resources/icons").resolve() / "resources" / "icons"
            ),
            destination_dir=str(Path(self.destination_dir)),
        )
