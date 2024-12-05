from pathlib import Path

from qt_stylehelper.value_object import Theme

StaticBuiltInResourceGenerator

StaticBuiltInResourceGenerator.generate(
	"dark_amber",
	destination_dir=Path(__file__).parent.resolve() / "resources",
	qrc_name="_stylehelper.qrc",
)

custom_theme = Theme(
	{
		"primaryColor"       : "#00bcd4",
		"primaryLightColor"  : "#62efff",
		"secondaryColor"     : "#f5f5f5",
		"secondaryLightColor": "#e6e6e6",
		"secondaryDarkColor" : "#ffffff",
		"primaryTextColor"   : "#3c3c3c",
		"secondaryTextColor" : "#555555",
	}
)

StaticBuiltInResourceGenerator.generate_custom_theme(
	"custom_theme",
	custom_theme,
	destination_dir=Path(__file__).parent.resolve() / "resources",
	qrc_name="_stylehelper.qrc",
)

# import re
# from pathlib import Path
# from typing import List, Dict

# def extract_color_usage(css_file: Path, property_name: str) -> Dict[str, List[str]]:
#     """
#     Extracts all selectors and their values for a given CSS property.

#     Args:
#         css_file (Path): Path to the CSS file.
#         property_name (str): The CSS property to search for (e.g., 'background-color').

#     Returns:
#         Dict[str, List[str]]: A dictionary where keys are color values, and values are lists of selectors using them.
#     """
#     try:
#         with css_file.open("r", encoding="utf-8") as f:
#             css_content = f.read()

#         # Regular expression to find selectors and property values
#         # Matches blocks like:
#         # .selector { background-color: #123456; ... }
#         pattern = rf"([^\{{]+)\{{[^}}]*{re.escape(property_name)}:\s*([^;]+);"

#         # Find all matches (selector and property value)
#         matches = re.findall(pattern, css_content)

#         # Organize matches into a dictionary: color -> selectors
#         color_usage = {}
#         for selector, value in matches:
#             value = value.strip()  # Clean up the property value
#             selector = selector.strip()  # Clean up the selector

#             # Group selectors by color
#             if value not in color_usage:
#                 color_usage[value] = []
#             color_usage[value].append(selector)

#         return color_usage

#     except FileNotFoundError:
#         print(f"File not found: {css_file}")
#         return {}
#     except Exception as e:
#         print(f"Error reading file: {e}")
#         return {}

# css_file = Path(__file__).parent.resolve() / "resources" / "dark_amber" / "_stylehelper.qss"
# property_name = "background-color"

# color_usage = extract_color_usage(css_file, property_name)

# for color, selectors in color_usage.items():
#     print(f"Color: {color}")
#     print(f"Used by selectors: {', '.join(selectors)}")
