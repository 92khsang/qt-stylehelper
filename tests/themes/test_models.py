import json

import pytest

from qt_stylehelper.themes.models import Theme, ExtraAttribute


# -------------------- Theme --------------------
def test_theme_valid():
    theme = Theme(
        primary_color="#ffffff",
        primary_light_color="#f0f0f0",
        secondary_color="#111111",
        secondary_light_color="#222222",
        secondary_dark_color="#333333",
        primary_text_color="#444444",
        secondary_text_color="#555555",
    )
    assert theme.primary_color == "#ffffff"
    assert theme.active_color == "#707070"  # default


def test_theme_invalid_color():
    with pytest.raises(ValueError, match="invalid hex color"):
        Theme(
            primary_color="notacolor",
            primary_light_color="#f0f0f0",
            secondary_color="#111111",
            secondary_light_color="#222222",
            secondary_dark_color="#333333",
            primary_text_color="#444444",
            secondary_text_color="#555555",
        )


def test_theme_to_dict_and_json():
    theme = Theme(
        primary_color="#000000",
        primary_light_color="#111111",
        secondary_color="#222222",
        secondary_light_color="#333333",
        secondary_dark_color="#444444",
        primary_text_color="#555555",
        secondary_text_color="#666666",
    )

    d = theme.to_dict(camel_case=False)
    assert d["primary_color"] == "#000000"

    d_camel = theme.to_dict(camel_case=True)
    assert d_camel["primaryColor"] == "#000000"

    j = theme.to_json()
    assert json.loads(j)["primaryColor"] == "#000000"


def test_theme_serialization_roundtrip():
    original = Theme(
        primary_color="#010101",
        primary_light_color="#020202",
        secondary_color="#030303",
        secondary_light_color="#040404",
        secondary_dark_color="#050505",
        primary_text_color="#060606",
        secondary_text_color="#070707",
    )
    json_str = original.to_json()
    restored = Theme.from_json(json_str)
    assert restored == original


def test_theme_keys():
    keys_snake = Theme.keys()
    keys_camel = Theme.keys(camel_case=True)
    assert "primary_color" in keys_snake
    assert "primaryColor" in keys_camel


# -------------------- ExtraAttribute --------------------
def test_extra_attr_valid():
    attr = ExtraAttribute()
    assert attr.font_family.startswith("sans-serif")
    assert attr.danger == "#dc3545"


def test_extra_attr_invalid():
    with pytest.raises(ValueError):
        ExtraAttribute(danger="badhex")


def test_extra_attr_values():
    attr = ExtraAttribute(icon="x.svg")
    values = attr.values
    assert values["icon"] == "x.svg"
    assert values["font_family"] == attr.font_family


def test_extra_attr_get_value():
    attr = ExtraAttribute()
    assert attr.get_value("danger") == attr.danger
    assert attr.get_value("nonexistent", "fallback") == "fallback"


def test_extra_attr_with_updated():
    attr = ExtraAttribute()
    updated = attr.with_updated_values({"density_scale": 1.5, "icon": "ok.svg"})
    assert updated.density_scale == 1.5
    assert updated.icon == "ok.svg"
    assert updated.danger == attr.danger  # unchanged
