import jinja2
import pytest

from qt_stylehelper.themes.models import Theme, ExtraAttribute
from qt_stylehelper.themes.stylesheet import (
    StyleSheetRenderer,
    StyleSheetExporter,
    opacity,
    density,
)


@pytest.fixture
def theme():
    return Theme(
        primary_color="#000000",
        primary_light_color="#111111",
        secondary_color="#222222",
        secondary_light_color="#333333",
        secondary_dark_color="#444444",
        primary_text_color="#555555",
        secondary_text_color="#666666",
        active_color="#777777",
    )


@pytest.fixture
def extra():
    return ExtraAttribute()


def test_opacity():
    assert opacity("#FF0000", 0.5) == "rgba(255, 0, 0, 0.5)"
    with pytest.raises(ValueError):
        opacity("#GG0000", 0.5)
    with pytest.raises(ValueError, match="Opacity value must be between 0.0 and 1.0."):
        opacity("#FF0000", 1.5)
    with pytest.raises(
        ValueError, match="Invalid hex color format. Expected format: '#RRGGBB'."
    ):
        opacity("FF0000", 0.5)


def test_density_numeric():
    assert density(16, density_scale=1) >= 4


def test_density_string():
    assert density("16px", density_scale=1) >= 4
    assert density("unset", density_scale=1) == "unset"
    assert density("@2.0", density_scale=1) == 2.0
    with pytest.raises(ValueError):
        density("invalid", density_scale=1)


def test_renderer_with_valid_template(theme, tmp_path):
    template_path = tmp_path / "material.css.jinja2"
    template_path.write_text(".example { color: {{ primaryColor }}; }")

    extra = ExtraAttribute()
    renderer = StyleSheetRenderer(template_file=str(template_path))
    output = renderer.render(theme, extra)
    assert ".example" in output
    assert "#000000" in output


def test_renderer_with_missing_template():
    with pytest.raises(FileNotFoundError):
        StyleSheetRenderer(template_file="/nonexistent/template.j2")


def test_render_raises_runtime_error(tmp_path, theme, extra, monkeypatch):
    template_path = tmp_path / "material.qss"
    template_path.write_text("dummy")

    class MockTemplate:
        def render(self, _):
            raise jinja2.TemplateError("fail")

    def mock_load_template(self):
        return MockTemplate()

    monkeypatch.setattr(StyleSheetRenderer, "_load_template", mock_load_template)

    renderer = StyleSheetRenderer(template_file=str(template_path))
    with pytest.raises(
        RuntimeError, match="An error occurred during template rendering."
    ):
        renderer.render(theme, extra)


def test_load_template_raises_runtime_error(tmp_path, monkeypatch):
    template_path = tmp_path / "material.qss"
    template_path.write_text("dummy")

    class MockEnvironment:
        @property
        def filters(self):
            return {}

        def get_template(self, name):
            raise jinja2.TemplateError("fail")

    def mock_env(*args, **kwargs):
        return MockEnvironment()

    monkeypatch.setattr(jinja2, "Environment", mock_env)

    renderer = StyleSheetRenderer(template_file=str(template_path))
    with pytest.raises(
        RuntimeError, match="An error occurred while loading the template."
    ):
        renderer._load_template()


def test_stylesheet_export(tmp_path):
    qss_content = ".my-class { color: red; }"
    export_dir = tmp_path / "export"
    StyleSheetExporter.export(
        stylesheet=qss_content, destination_dir=str(export_dir), qrc_name="style.qrc"
    )

    assert (export_dir / "_stylehelper.qss").exists()
    assert (export_dir / "style.qrc").exists()


def test_stylesheet_export_invalid_prefix():
    with pytest.raises(ValueError):
        StyleSheetExporter.export(
            stylesheet="test", destination_dir="/tmp", icon_url_prefix="invalid"
        )


def test_generate_qrc_file(tmp_path):
    icon_dir = tmp_path / "primary"
    icon_dir.mkdir()
    (icon_dir / "icon.svg").write_text("<svg></svg>")

    qss_file = tmp_path / "_stylehelper.qss"
    qss_file.write_text(".style {}")

    qrc_path = tmp_path / "style.qrc"

    StyleSheetExporter._generate_qrc_file(
        output_path=tmp_path,
        qrc_path=qrc_path,
        icon_url_prefix="icon:/",
        qss_name="_stylehelper.qss",
    )

    content = qrc_path.read_text()
    assert '<qresource prefix="icon">' in content
    assert f"<file>{tmp_path.name}/primary/icon.svg</file>" in content
    assert "<file>_stylehelper.qss</file>" in content
