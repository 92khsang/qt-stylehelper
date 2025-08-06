import pytest

from qt_stylehelper.themes.models import Theme
from qt_stylehelper.tools.static.generator import StaticStyleGenerator


@pytest.fixture
def theme_dir(tmp_path):
    return tmp_path / "my_theme"


@pytest.fixture
def theme_file(tmp_path):
    path = tmp_path / "theme.json"
    path.write_text("{}")
    return path


@pytest.fixture
def theme():
    return Theme(
        primary_color="#123456",
        primary_light_color="#234567",
        secondary_color="#345678",
        secondary_light_color="#456789",
        secondary_dark_color="#56789A",
        primary_text_color="#6789AB",
        secondary_text_color="#789ABC",
    )


def test_resolve_output_path_defaults_to_resources():
    result = StaticStyleGenerator._resolve_output_path("dark", None)
    assert result.name == "dark"
    assert "resources" in str(result)


def test_resolve_output_path_with_custom_dir(tmp_path):
    out = tmp_path / "exported"
    result = StaticStyleGenerator._resolve_output_path("light", out)
    assert result == out / "light"


def test_generate_from_builtin_raises_for_invalid(monkeypatch):
    monkeypatch.setattr(
        "qt_stylehelper.themes.manager.ThemeManager.load_builtin_theme",
        lambda name: None,
    )
    with pytest.raises(ValueError):
        StaticStyleGenerator.generate_from_builtin("missing")


def test_generate_from_custom_creates_json(tmp_path, theme):
    StaticStyleGenerator.generate_from_custom("mytheme", theme, output_dir=tmp_path)
    assert (tmp_path / "mytheme" / "mytheme.json").exists()


def test_generate_from_custom(monkeypatch, tmp_path, theme):
    from qt_stylehelper.themes.stylesheet import StyleSheetExporter, StyleSheetRenderer
    from qt_stylehelper.themes.icon import BuiltInIconGenerator

    monkeypatch.setattr(
        StyleSheetExporter,
        "export",
        lambda *a, **kw: None,
    )
    monkeypatch.setattr(
        BuiltInIconGenerator,
        "generate_statically",
        lambda *a, **kw: None,
    )
    monkeypatch.setattr(
        StyleSheetRenderer,
        "render",
        lambda *a, **kw: "/* qss */",
    )

    path = tmp_path / "style_out"
    json_dir = path / "custom"
    with pytest.raises(FileNotFoundError, match="No such file or directory"):
        StaticStyleGenerator.generate_from_custom("custom", theme, output_dir=path)

    json_dir.mkdir(parents=True, exist_ok=True)
    StaticStyleGenerator.generate_from_custom("custom", theme, output_dir=path)
    json_path = json_dir / "custom.json"
    assert json_path.exists()
