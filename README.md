# Qt-stylehelper

`qt-stylehelper` is a Python library that provides tools for managing themes, generating stylesheets, and dynamically applying styles in PySide6 applications. The library includes modules for handling static and dynamic resource generation, stylesheet rendering, and managing theme-specific assets.

Modules
-------

### `StaticBuiltInResourceGenerator`

This class handles the generation of static resources, including QSS stylesheets and QRC resource files, for a given theme.

#### Key Methods:

*   `generate`: Generates static resources for a theme.
*   `generate_custom_theme`: Customizes resource generation with extra attributes.
*   `_build_destination_dir`: Constructs the output directory path for theme resources.

#### Example:

```python
from qt_stylehelper import StaticBuiltInResourceGenerator

StaticBuiltInResourceGenerator.generate(
    theme_name="dark_theme",
    extra={"font_family": "Arial, sans-serif"},
    destination_dir="./output",
)
```

* * *

### `QtStyleTools`

An abstract base class providing the foundation for applying styles and themes to PyQt widgets.

#### Key Features:

*   `apply_stylesheet`: Applies a stylesheet to a given widget.
*   Abstract methods for retrieving themes, stylesheets, and icon directories.

* * *

### `StaticQtStyleTools`

A concrete implementation of `QtStyleTools` for managing and applying static themes.

#### Key Features:

*   `auto_init`: Automatically initializes themes from a directory.
*   `manual_init`: Manually initializes themes using provided theme structures.
*   `get_theme_list`: Retrieves the list of available themes.

#### Example:

```python
from qt_stylehelper import (
	StaticBuiltInResourceGenerator,
	StaticQtStyleTools,
)

_RESOURCES_DIR = Path(__file__).parent.resolve() / "resources"

def generate_static_theme(theme_names: List[str]):
	for theme_name in theme_names:
		StaticBuiltInResourceGenerator.generate(
			theme_name,
			destination_dir=str(_RESOURCES_DIR)
		)

theme_names = ["dark_amber", "light_cyan_500"]
generate_static_theme(theme_names)

# main window
main_window = #

static_tools = StaticQtStyleTools()
static_tools.auto_init(str(_RESOURCES_DIR))
static_tools.apply_stylesheet(main_window, "dark_amber")
```

- See the examples folder for more details

* * *

### `DynamicQtStyleTools`

An extension of `QtStyleTools` that generates resources dynamically during runtime.

#### Key Features:

*   Dynamically generates icons and stylesheets.
*   Supports extra attributes for customizing styles.
*   Simplifies the integration of themes with PyQt applications.

#### Example:

```python
from qt_stylehelper import DynamicQtStyleTools

dynamic_tools = DynamicQtStyleTools(app_name="my_app")
dynamic_tools.apply_stylesheet(widget=my_widget, theme_name="dark_amber")
```

- See the examples folder for more details

* * *

## License
This project is licensed under the BSD 2-Clause License. See the LICENSE file for details.

## Acknowledgments and Attribution

This project, **qt-stylehelper**, has been deeply inspired by the outstanding work of the [qt\-material](https://github.com/UN-GCPDS/qt-material) project. We wish to extend our sincere gratitude to the authors and contributors of qt-material for their exceptional efforts in creating and maintaining such a valuable resource for the community.

Several components of the **qt-stylehelper** codebase have been directly derived from or adapted from the qt-material project. These contributions have significantly influenced the design and functionality of this project. Without the foundational work of qt-material, the development of qt-stylehelper would not have been possible in its current form.

The qt-material project is made available under the **BSD 2-Clause "Simplified" License**, which permits reuse and adaptation with appropriate acknowledgment. We fully comply with the terms of this license and are committed to ensuring proper recognition of their intellectual contributions.

We encourage anyone interested in the original qt-material project to visit its [GitHub repository](https://github.com/UN-GCPDS/qt-material) to learn more about their work and access their full licensing details. The license itself can be reviewed at the following link: BSD 2\-Clause License.

We are grateful to be part of a community that thrives on open collaboration and shared knowledge. Projects like qt-material embody the spirit of open source, and we are honored to contribute to this ecosystem by building upon their efforts.