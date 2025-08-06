import logging
from pathlib import Path

import pytest

from qt_stylehelper.core.utils import ValidateUtils, ResourcePathUtils, PlatformUtils
from qt_stylehelper.themes.icon import (
    _get_icon_name_list,
    BuiltInIconDirValidator,
    ContextIconGenerator,
    BuiltInIconGenerator,
    ICON_CONTEXT,
)
from qt_stylehelper.themes.models import Theme


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


def make_svg(path: Path, content: str = "") -> None:
    path.write_text(content or "<svg></svg>")


def test_validate(tmp_path):
    theme_name = "th"
    theme_dir = tmp_path / theme_name

    icon_set = {"a.svg", "b.svg"}
    validator = BuiltInIconDirValidator
    validator._BuiltInIconDirValidator__BUILT_IN_ICON_LIST = icon_set

    for context in ICON_CONTEXT:
        context_dir = theme_dir / context
        context_dir.mkdir(parents=True, exist_ok=True)
        for icon_name in icon_set:
            icon_path = context_dir / icon_name
            icon_path.touch()

    try:
        BuiltInIconDirValidator.validate(str(theme_dir))
        BuiltInIconDirValidator.validate(str(tmp_path), theme_name)
    except Exception as e:
        pytest.fail(f"Exception should not be raised: {e}")


def test_get_icon_name_list(tmp_path):
    (tmp_path / "a.svg").touch()
    (tmp_path / "b.svg").touch()
    (tmp_path / "c.txt").touch()
    result = _get_icon_name_list(tmp_path)
    assert sorted(result) == ["a.svg", "b.svg"]


def test_validate_icon_context_dirs_missing(tmp_path):
    theme_dir = tmp_path / "my_theme"
    theme_dir.mkdir()
    (theme_dir / "primary").mkdir()
    with pytest.raises(FileNotFoundError):
        BuiltInIconDirValidator._validate_icon_context_dirs(theme_dir)


def test_validate_icon_list_missing_icons(tmp_path, monkeypatch):
    from qt_stylehelper.themes import icon

    monkeypatch.setattr(icon, "_get_icon_name_list", lambda _: ["a.svg"])
    validator = BuiltInIconDirValidator
    validator._BuiltInIconDirValidator__BUILT_IN_ICON_LIST = {"a.svg", "b.svg"}
    with pytest.raises(ValueError):
        validator._validate_icon_list(tmp_path)


def test_context_icon_generator_replace_color():
    input_svg = "#0000ff some #ff0000 and #000000"
    result = ContextIconGenerator._replace_color(input_svg, "#0000ff", "#123456")
    assert "#123456" in result
    assert "#ffffff00" in result


def test_context_icon_generator_process_svg(tmp_path):
    input_svg_path = tmp_path / "icon.svg"
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    make_svg(input_svg_path, "#0000ff and #ff0000")

    generator = ContextIconGenerator("#0000ff", "#ff0000")
    generator._process_svg(input_svg_path, output_dir, "#111111", "#222222")

    output_svg = output_dir / "icon.svg"
    assert output_svg.exists()
    content = output_svg.read_text()
    assert "#111111" in content or "#222222" in content


def test_process_svg_read_error(tmp_path, monkeypatch):
    svg_file = tmp_path / "icon.svg"
    svg_file.write_text("<svg></svg>")
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    generator = ContextIconGenerator("#0000ff", "#ff0000")

    def fake_open_fail_read(*args, **kwargs):
        raise OSError("read failure")

    monkeypatch.setattr(Path, "open", fake_open_fail_read)

    with pytest.raises(RuntimeError) as e:
        generator._process_svg(svg_file, output_dir, "#123456", "#654321")

    assert "Failed to read SVG file" in str(e.value)


def test_process_svg_write_error(tmp_path, monkeypatch):
    svg_file = tmp_path / "icon.svg"
    svg_file.write_text("<svg>#000000#FFFFFF</svg>")
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    generator = ContextIconGenerator("#0000ff", "#ff0000")

    class FakeFile:
        def read(self):
            return "<svg>#000000#FFFFFF</svg>"

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    def fake_open_read_success(self, mode="r", **kwargs):
        if mode == "r":
            return FakeFile()
        raise OSError("write failure")

    monkeypatch.setattr(Path, "open", fake_open_read_success)

    with pytest.raises(RuntimeError) as e:
        generator._process_svg(svg_file, output_dir, "#123456", "#654321")

    assert "Failed to write processed SVG" in str(e.value)


def test_context_icon_generator_generate(theme, tmp_path):
    input_dir = tmp_path / "src"
    input_dir.mkdir()
    for context in ICON_CONTEXT:
        (input_dir / f"{context}.svg").write_text("#0000ff")

    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()
    generator = ContextIconGenerator("#0000ff", "#ff0000")
    generator.generate(theme, input_dir, dest_dir)

    for context in ICON_CONTEXT:
        assert (dest_dir / context).exists()


def test_context_icon_generator_generate_invalid_dir(theme):
    generator = ContextIconGenerator("#0000ff", "#ff0000")
    with pytest.raises(
        ValueError, match="Both source_dir and destination_dir must be directory."
    ):
        generator.generate(theme, Path("/nonexistent"), Path("/nonexistent"))


def test_get_dynamic_icons_dir_valid(monkeypatch, tmp_path):
    dummy_app_dir = tmp_path / ".pyqtapp"
    monkeypatch.setattr(ValidateUtils, "is_valid_filename", lambda x: True)
    monkeypatch.setattr(
        PlatformUtils,
        "get_app_data_dir",
        lambda name: dummy_app_dir,
    )

    called = {}

    def fake_mkdir(self, parents=False, exist_ok=False):
        called["mkdir"] = True

    monkeypatch.setattr(Path, "mkdir", fake_mkdir)

    path = BuiltInIconGenerator.get_dynamic_icons_dir("valid_app")
    assert path == dummy_app_dir
    assert called.get("mkdir") is True


def test_get_dynamic_icons_dir_invalid(monkeypatch, tmp_path):
    dummy_app_dir = tmp_path / ".pyqtapp"
    monkeypatch.setattr(ValidateUtils, "is_valid_filename", lambda x: False)
    monkeypatch.setattr(
        PlatformUtils,
        "get_app_data_dir",
        lambda name: dummy_app_dir,
    )
    monkeypatch.setattr(Path, "mkdir", lambda self, parents=False, exist_ok=False: None)

    path = BuiltInIconGenerator.get_dynamic_icons_dir("??invalid")
    assert path.name == ".pyqtapp"


def test_generate_dynamically_calls_internal(theme, monkeypatch, tmp_path):
    called = {"generate_icons": False}

    monkeypatch.setattr(
        BuiltInIconGenerator,
        "get_dynamic_icons_dir",
        lambda app_name: tmp_path,
    )

    def fake_generate_icons(input_theme, destination_dir_path):
        assert input_theme == theme
        assert destination_dir_path == tmp_path
        called["generate_icons"] = True

    monkeypatch.setattr(
        BuiltInIconGenerator,
        "_generate_icons",
        fake_generate_icons,
    )

    BuiltInIconGenerator.generate_dynamically(theme, app_name="myapp")
    assert called["generate_icons"] is True


def test_built_in_icon_generator_create_destination_dir(tmp_path):
    path = tmp_path / "icons"
    assert not path.exists()
    BuiltInIconGenerator._create_destination_dir(path)
    assert path.exists() and path.is_dir()


def test_create_destination_dir_raises_and_logs(monkeypatch, caplog):
    class BogusPath:
        def exists(self):
            return False

        def mkdir(self, *args, **kwargs):
            raise PermissionError("no permission")

    bogus_path = BogusPath()

    with caplog.at_level(logging.ERROR):
        with pytest.raises(PermissionError, match="no permission"):
            BuiltInIconGenerator._create_destination_dir(bogus_path)

    assert "Failed to create icon destination directory" in caplog.text


def test_built_in_icon_generator_generate_statically(theme, tmp_path):
    icon_src = tmp_path / "icons"
    icon_src.mkdir()
    for context in ["primary", "disabled", "active"]:
        (icon_src / f"{context}.svg").write_text("#0000ff")

    monkeypatch_dir = tmp_path / "builtin"
    monkeypatch_dir.mkdir()
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(ResourcePathUtils, "icons_dir", lambda: icon_src)

    dest = tmp_path / "out"
    BuiltInIconGenerator.generate_statically(theme, str(dest))

    for context in ["primary", "disabled", "active"]:
        assert (dest / context).exists()

    monkeypatch.undo()
