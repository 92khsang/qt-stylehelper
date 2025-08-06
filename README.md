Sure, here is a clean, organized, and professional English version of the README.md file.

-----

# Qt-stylehelper

`qt-stylehelper` is a Python library that provides tools for managing themes, generating
stylesheets, and dynamically applying styles in PySide6 applications. The library includes modules
for handling static and dynamic resource generation, stylesheet rendering, and managing
theme-specific assets.

## Modules

### `Theme`

An immutable representation of a color theme with strict hex color validation and support for
dual-format serialization.

#### Key Features

* Uses `snake_case` internally for Pythonic consistency.
* Supports JSON serialization and deserialization using `camelCase` for compatibility with existing
  theme files.
* Strict hex color validation is performed in `__post_init__`.
* Includes custom methods for controlled conversions:
    * `from_dict(data: dict)`: Initializes from either `snake_case` or `camelCase` keys.
    * `from_json(json_str: str)`: Parses a JSON string into a `Theme` instance.
    * `to_dict(camel_case=True)`: Serializes to a `dict` with optional `camelCase` keys.
    * `to_json(camel_case=True)`: Serializes to a JSON string with optional `camelCase` keys.
    * `keys(camel_case=False)`: Returns a list of attribute names in the desired case format.

#### Design Note

This class uses a custom `to_dict()` method instead of `dataclasses.asdict()` to support `camelCase`
serialization. This is crucial for compatibility with pre-existing theme files while allowing the
Python implementation to use idiomatic `snake_case`.

#### Example

```python
from qt_stylehelper import Theme

# Theme JSON using camelCase keys (as used in external config files)
json_data = '''
{
  "primaryColor": "#ff0000",
  "primaryLightColor": "#ff6666",
  "secondaryColor": "#00ff00",
  "secondaryLightColor": "#66ff66",
  "secondaryDarkColor": "#009900",
  "primaryTextColor": "#000000",
  "secondaryTextColor": "#333333",
  "activeColor": "#707070"
}
'''

# Deserialize from JSON
theme = Theme.from_json(json_data)

# Access Python-style attributes
print(theme.primary_color)

# Serialize back to JSON (camelCase keys)
print(theme.to_json(camel_case=True))
```

-----

### `ExtraAttribute`

This class provides optional configuration to control additional UI rendering behaviors, primarily
for maintaining compatibility with `qt-material`'s Jinja2-based stylesheet templates.

#### Purpose

`ExtraAttribute` encapsulates settings referenced during dynamic stylesheet rendering. These
settings work in conjunction with a `Theme` and are only meaningful **after a theme has been applied
**.

#### Key Features

* Compatible with `qt-material` template variables (e.g., `danger`, `icon`, `density_scale`).
* Ensures data consistency via `with_updated_values()`, which returns a new validated instance.
* Provides convenient value access through the `.values` property and `.get_value()` method.

#### Field Descriptions

| Field           | Type            | Description                                                                                      |
|:----------------|:----------------|:-------------------------------------------------------------------------------------------------|
| `icon`          | `Optional[str]` | An optional icon path prefix used when `QDir.addSearchPath` is called with `"icon"` as a prefix. |
| `font_family`   | `str`           | The base font family (e.g., `"sans-serif"`, `"Roboto"`).                                         |
| `danger`        | `str`           | The color used for danger-related components (unaffected by theme colors).                       |
| `warning`       | `str`           | The color used for warning-related components (unaffected by theme colors).                      |
| `success`       | `str`           | The color used for success-related components (unaffected by theme colors).                      |
| `density_scale` | `float`         | The UI scaling factor (e.g., `1.0`, `2.0`). Only meaningful after a theme is applied.            |
| `button_shape`  | `str`           | The shape mode for buttons (e.g., `"default"`, `"rounded"`).                                     |

#### API

* `values`: Returns a flat dictionary of the attribute values.
* `get_value(key: str, default=None)`: Retrieves a value by key, with an optional default.
* `with_updated_values(dict)`: Returns a new validated instance with updated fields, preserving
  immutability and field constraints.

#### Example

```python
from qt_stylehelper import ExtraAttribute

# Create base extra attributes
extra = ExtraAttribute(density_scale=1.0)

# Update one or more values safely
updated = extra.with_updated_values({"danger": "#ff4444", "button_shape": "rounded"})

# Inspect values used in template rendering
print(updated.values)
```

-----

### `QtStyleTool`

An abstract base class that defines a common interface for applying and managing Qt styles and
themes. It integrates theme rendering, palette application, and icon directory handling, providing a
consistent styling mechanism for PySide6 applications.

#### Overview

At its core, `QtStyleTool` is responsible for applying a selected theme to a given `QWidget`. It
separates **theme management** from **theme application**, allowing for flexible rendering
strategies. Subclasses implement how themes, stylesheets, and icon resources are retrieved, whether
dynamically or from pre-generated static resources.

This class is meant to be subclassed by:

* **`DynamicQtStyleTool`**: Uses runtime theme resolution, rendering the stylesheet and icons on the
  fly. This is suitable for maximum flexibility and full compatibility with the `qt-material`
  ecosystem.
* **`StaticQtStyleTool`**: Uses pre-rendered stylesheets and icon resources generated in advance.
  This strategy improves performance and avoids runtime complexity, ensuring fast and reliable theme
  application.

#### Responsibilities

* Maintain and switch between themes by name.
* Apply or refresh a widget's current theme.
* Delegate palette, stylesheet, and resource path updates to a `QtHandler`.
* Leave theme resolution to the subclass implementation.

#### Key Methods

##### `apply_stylesheet(widget, theme_name)`

Applies the selected theme to a widget. This involves:

* Validating the theme name.
* Applying the stylesheet.
* Registering icon directories.
* Applying the theme's color palette.

This method is typically used to **switch to a different theme** entirely.

##### `refresh_stylesheet(widget)`

Re-applies the current theme to the widget. Unlike `apply_stylesheet`, this method is for *
*reapplying the current theme after `ExtraAttribute` changes** (e.g., changing density scale or icon
prefix), without switching the theme itself.

##### `update_resource_prefix(resource_dir, prefix)`

Registers a custom resource directory under a given prefix using `QDir.addSearchPath`. It's
typically used for icon directories within a theme.

##### Abstract Methods (to be implemented by subclasses)

* `add_theme(path)`: Registers one or more themes.
* `get_theme_list()`: Returns a list of available theme names.
* `_get_theme_object(theme_name)`: Retrieves the `Theme` object.
* `_get_stylesheet(theme_name)`: Retrieves the corresponding stylesheet string.
* `_get_icons_dir(theme_name)`: Retrieves the icon directory path.

#### Design Summary

| Method                           | Description                                                                                       |
|:---------------------------------|:--------------------------------------------------------------------------------------------------|
| `apply_stylesheet()`             | Applies a new theme to a widget.                                                                  |
| `refresh_stylesheet()`           | Re-applies the current theme without switching it. Useful when only `ExtraAttribute` has changed. |
| `update_resource_prefix()`       | Adds a custom resource path under a prefix (usually "icon").                                      |
| `add_theme()` (abstract)         | Registers themes via a file or directory.                                                         |
| `get_theme_list()` (abstract)    | Lists available themes.                                                                           |
| `_get_theme_object()` (abstract) | Gets a `Theme` instance for the name.                                                             |
| `_get_stylesheet()` (abstract)   | Gets the rendered stylesheet string.                                                              |
| `_get_icons_dir()` (abstract)    | Gets the icon directory path.                                                                     |

#### Static vs. Dynamic Implementation

`QtStyleTool` serves as the foundation for two distinct rendering strategies:

* **`DynamicQtStyleTool`**: A dynamic renderer that mimics the original `qt-material` behavior. It
  re-renders the stylesheet and icons every time a theme is applied. This provides maximum
  flexibility and supports runtime customization but may introduce performance overhead when
  switching themes frequently.

* **`StaticQtStyleTool`**: A custom implementation optimized for performance and stability. Instead
  of generating themes and icons dynamically, it uses a **pre-generated set of stylesheets and
  assets**. This static approach avoids runtime rendering bottlenecks and ensures a consistent
  experience across devices, which is especially helpful in production environments.

-----

### `StaticStyleGenerator`

This class generates static resources—stylesheets, icons, and metadata—for a given theme. These
resources are **required** for `StaticQtStyleTool` to function, enabling fast and reliable theme
application without dynamic rendering.

#### Purpose

Unlike `DynamicQtStyleTool`, which renders stylesheets and icons at runtime, `StaticQtStyleTool`
expects all required assets to be **pre-rendered**. This class fulfills that requirement by
generating:

* A QSS stylesheet (`_stylehelper.qss`).
* Theme metadata (`<theme>.json`).
* Themed SVG icons for multiple color contexts (`primary`, `active`, `disabled`).

#### Output Structure

A typical output directory generated by this class looks like this:

```
<output_dir>/<theme_name>/
├── _stylehelper.qss
├── <theme_name>.json
├── primary/
│   ├── close.svg
│   ├── ...
├── active/
│   ├── close.svg
│   ├── ...
└── disabled/
    ├── close.svg
    ├── ...
```

* `primary/`: Icons rendered with the primary theme color.
* `active/`: Icons for hover/focus state styling.
* `disabled/`: Icons for disabled or low-contrast components.

#### Key Methods

##### `generate_from_builtin(theme_name, extra, output_dir, ...)`

Generates static resources for a **built-in** theme by name.

* Loads the theme using `ThemeManager.load_builtin_theme()`.
* Optionally applies `ExtraAttribute` (e.g., font, density scale).
* Delegates to `generate_from_custom(...)` to produce the files.
* Raises `ValueError` if the theme is not found.

**Use this to statically generate a theme that is included with the library.**

##### `generate_from_custom(theme_name, theme, extra, output_dir, ...)`

Generates static resources from a **custom `Theme` instance**.

Steps performed:

1. Renders QSS using `StyleSheetRenderer`.
2. Generates themed icons in `primary/`, `active/`, `disabled/` via
   `BuiltInIconGenerator.generate_statically(...)`.
3. Exports the stylesheet via `StyleSheetExporter`.
4. Writes the theme's configuration as `<theme_name>.json`.

This method supports advanced customization and external themes.

##### `_resolve_output_path(theme_name, output_dir)`

Returns the base output path as `output_dir/theme_name/` or `./resources/theme_name/` if no output
directory is specified.

#### Integration with `StaticQtStyleTool`

This class should be used **before** using `StaticQtStyleTool`. Without running
`generate_from_builtin()` or `generate_from_custom()`, the static tool will have no QSS or icon
files to load. The static approach ensures faster UI initialization and avoids runtime stylesheet
rendering overhead. It's especially useful in production environments where theme configuration is
fixed and performance is critical.

-----

### `StaticQtStyleTool`

A concrete implementation of `QtStyleTool` designed to apply **pre-generated static themes**. It
reads QSS stylesheets, JSON theme metadata, and icon resources from disk, applying them to Qt
widgets without any runtime rendering.

#### Purpose

Unlike its dynamic counterpart (`DynamicQtStyleTool`), this class does **not** render themes at
runtime. Instead, it loads **pre-rendered stylesheets and icons** generated by
`StaticStyleGenerator`. This static approach offers:

* **Faster theme application**.
* **Reduced runtime overhead**.
* **Deterministic behavior** (no rendering logic is executed during UI load).

It's ideal for production environments or applications that require fast and consistent theming
without the flexibility of dynamic re-theming.

#### Key Features

* Loads a theme directory containing rendered QSS files, a theme metadata JSON file, and icon
  directories (`primary/`, `active/`, `disabled/`).
* Validates the directory contents, QSS integrity, and color usage.
* Maintains an in-memory map of available themes.

#### Core Methods

##### `add_theme(path)`

Registers a theme by reading the specified directory. This method:

1. Validates the directory's existence and format.
2. Parses the QSS and JSON files.
3. Validates that:
    * The QSS file rendering matches a known template.
    * Theme color values (excluding `activeColor`) are present in the stylesheet.
    * All required icon directories are present.

The result is stored as a `StaticThemeStruct` mapped by theme name.

##### `get_theme_list()`

Returns a list of successfully registered theme names.

##### `_get_stylesheet(theme_name)`

Concatenates all `.qss` files from the theme directory into a single stylesheet string.

##### `_get_theme_object(theme_name)`

Returns the `Theme` instance loaded from the corresponding JSON file.

##### `_get_icons_dir(theme_name)`

Returns the root directory where the icon folders are located.

#### Internal Validation Flow

When you call `add_theme()`, the following validations are enforced:

* `theme_dir` must exist and contain:
    * At least one valid `.qss` file.
    * A JSON file that matches the directory name (e.g., `dark_red/dark_red.json`).
    * Valid icon directories.
* The QSS must contain rendered values, not just placeholders.
* Theme values (excluding `activeColor`) must appear in the QSS.
* The QSS must be rendered from the known default Jinja2 template.

These checks ensure full consistency between the `Theme`, `ExtraAttribute`, and rendered assets.

#### Example

```python
from qt_stylehelper import StaticQtStyleTool, StaticStyleGenerator
from pathlib import Path

_RESOURCES_DIR = Path(__file__).parent / "resources"

# 1. Pre-generate static assets (only needed once)
StaticStyleGenerator.generate_from_builtin(
        theme_name="dark_amber",
        output_dir=_RESOURCES_DIR
)

# 2. Load and apply theme
tool = StaticQtStyleTool()
tool.add_theme(_RESOURCES_DIR / "dark_amber")
tool.apply_stylesheet(main_window, "dark_amber")
```

#### Static Theme Directory Structure

```
resources/
└── dark_amber/
    ├── _stylehelper.qss         ← Pre-rendered stylesheet
    ├── dark_amber.json          ← Theme metadata
    ├── primary/                 ← Main icon color set
    ├── active/                  ← Icons for hover/focus states
    └── disabled/                ← Icons for disabled states
```

> All files must be generated beforehand using `StaticStyleGenerator`. Otherwise,
`StaticQtStyleTool` will raise validation errors when loading the theme.

-----

### `DynamicQtStyleTool`

A dynamic implementation of `QtStyleTool` that renders stylesheets and icons **at runtime** using
Jinja2 templating and in-memory theme management.

#### Purpose

`DynamicQtStyleTool` enables **on-the-fly theme rendering** without the need to pre-generate QSS or
icon assets. It's ideal for development, theming previews, or applications that require runtime
customization (e.g., switching fonts, colors, or density).

Compared to `StaticQtStyleTool`, this class provides **maximum flexibility** at the cost of
additional runtime processing.

#### Key Features

* Loads and manages theme files dynamically from disk.
* Renders QSS stylesheets using Jinja2 templates on each call.
* Generates icon resources in a temporary cache directory.
* Allows dynamic updates to `ExtraAttribute` (e.g., font, density).
* Requires no prior invocation of `StaticStyleGenerator`.

#### Internal Components

* `ThemeManager`: Handles loading of theme JSON files.
* `StyleSheetRenderer`: Converts `Theme` and `ExtraAttribute` into QSS using Jinja2.
* `BuiltInIconGenerator`: Dynamically generates themed icons to a temporary path.
* `ExtraAttribute`: User-defined enhancements like density scaling or font overrides.

#### Core Methods

##### `apply_stylesheet(widget, theme_name)`

Inherited from `QtStyleTool`. Applies the dynamically rendered stylesheet and icon paths to the
target widget.

##### `update_extra_attribute(extra)`

Updates the internal `ExtraAttribute` instance. It accepts either a full `ExtraAttribute` object or
a partial `dict`. This allows for on-the-fly UI density or color adjustments without changing the
current theme.

* Example:
  ```python
  dynamic_tool.update_extra_attribute({"font_family": "Inter", "density_scale": 1.25})
  ```

##### `add_theme(path)`

Registers a single theme JSON file or scans a directory for multiple theme files. It's used for
loading user-defined or external themes at runtime.

##### `get_theme_list()`

Returns a list of all available theme names, including the built-in `"default"`.

##### `_get_stylesheet(theme_name)`

* Loads the theme from `ThemeManager`.
* Generates dynamic icons to a temporary cache directory.
* Renders the stylesheet using the active `ExtraAttribute`.

##### `_get_icons_dir(theme_name)`

Returns the temporary directory where dynamic icons are generated.

#### Example

```python
from qt_stylehelper import DynamicQtStyleTool

tool = DynamicQtStyleTool(app_name="my_app")
tool.update_extra_attribute({"density_scale": 1.2})  # Optional customization
tool.apply_stylesheet(widget=my_widget, theme_name="dark_cyan")
```

This will:

1. Load the `dark_cyan.json` theme from the specified directory.
2. Render the QSS using Jinja2 with the `ExtraAttribute` values.
3. Dynamically generate themed icons (e.g., `primary/`, `active/`, `disabled/`).
4. Apply the stylesheet and resource path to `my_widget`.

#### Use Cases

* **Live theme previews** in design tools.
* Applications that allow **user-driven theme customization**.
* Dynamically loaded third-party themes (e.g., plugins, extensions).

#### Comparison with `StaticQtStyleTool`

| Feature                  | DynamicQtStyleTool           | StaticQtStyleTool         |
|:-------------------------|:-----------------------------|:--------------------------|
| Theme loading            | At runtime                   | Pre-generated on disk     |
| QSS rendering            | Jinja2 (in-memory)           | From a static `.qss` file |
| Icon generation          | Dynamic (temp dir)           | Pre-rendered (on disk)    |
| `ExtraAttribute` updates | Applied live                 | Applied during generation |
| Performance              | Slower (flexible)            | Faster (fixed)            |
| Best for                 | Development, previews, tools | Production, packaged apps |

-----

## License

This project is licensed under the BSD 2-Clause License. See the LICENSE file for details.

## Acknowledgments and Attribution

This project, **qt-stylehelper**, was deeply inspired by the outstanding work of
the [qt-material](https://github.com/UN-GCPDS/qt-material) project. We extend our sincere gratitude
to the authors and contributors of `qt-material` for their exceptional efforts in creating and
maintaining such a valuable resource for the community.

Several components of the `qt-stylehelper` codebase are directly derived from or adapted from the
`qt-material` project. These contributions have significantly influenced the design and
functionality of this project. Without the foundational work of `qt-material`, the development of
`qt-stylehelper` would not have been possible in its current form.

The `qt-material` project is available under the **BSD 2-Clause "Simplified" License**, which
permits reuse and adaptation with appropriate acknowledgment. We fully comply with the terms of this
license and are committed to ensuring proper recognition of their intellectual contributions.

We encourage anyone interested in the original `qt-material` project to visit
its [GitHub repository](https://github.com/UN-GCPDS/qt-material) to learn more about their work and
access their full licensing details. The license itself can be reviewed at the following link: BSD
2-Clause License.

We are grateful to be part of a community that thrives on open collaboration and shared knowledge.
Projects like `qt-material` embody the spirit of open source, and we are honored to contribute to
this ecosystem by building upon their efforts.