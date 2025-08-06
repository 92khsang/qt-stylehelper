import json
from dataclasses import dataclass, fields, asdict
from typing import Dict, Union, Optional, List, Literal

from qt_stylehelper.core.utils import ValidateUtils

AttrValue = Union[str, float, None]
AttrDict = Dict[str, AttrValue]


@dataclass(frozen=True, slots=True)
class Theme:
    primary_color: str
    primary_light_color: str
    secondary_color: str
    secondary_light_color: str
    secondary_dark_color: str
    primary_text_color: str
    secondary_text_color: str
    active_color: str = "#707070"

    def __post_init__(self):
        for f in fields(self):
            value = getattr(self, f.name)
            if not ValidateUtils.is_valid_hex_color(value):
                raise ValueError(f"{f.name} has an invalid hex color: {value}")

    @classmethod
    def keys(cls, camel_case: bool = False) -> List[str]:
        return [
            cls._snake_to_camel(f.name) if camel_case else f.name for f in fields(cls)
        ]

    def to_dict(self, camel_case: bool = True) -> Dict[str, str]:
        return {
            self._snake_to_camel(f.name) if camel_case else f.name: getattr(
                self, f.name
            )
            for f in fields(self)
        }

    def to_json(self, camel_case: bool = True, **kwargs) -> str:
        return json.dumps(self.to_dict(camel_case=camel_case), **kwargs)

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Theme":
        snake_case_data = {}
        for f in fields(cls):
            snake_key = f.name
            camel_key = cls._snake_to_camel(snake_key)
            if snake_key in data:
                snake_case_data[snake_key] = data[snake_key]
            elif camel_key in data:
                snake_case_data[snake_key] = data[camel_key]
        return cls(**snake_case_data)

    @classmethod
    def from_json(cls, json_str: str) -> "Theme":
        data = json.loads(json_str)
        return cls.from_dict(data)

    @staticmethod
    def _snake_to_camel(snake: str) -> str:
        parts = snake.split("_")
        return parts[0] + "".join(p.capitalize() for p in parts[1:])


@dataclass(frozen=True, slots=True)
class ExtraAttribute:
    icon: Optional[str] = None
    font_family: str = "sans-serif"
    danger: str = "#dc3545"
    warning: str = "#ffc107"
    success: str = "#17a2b8"
    density_scale: float = 0.0
    button_shape: Literal["default", "rounded"] = "default"

    def __post_init__(self):
        for name in ("danger", "warning", "success"):
            value = getattr(self, name)
            if not ValidateUtils.is_valid_hex_color(value):
                raise ValueError(f"{name} has invalid hex color: {value}")

    @property
    def values(self) -> AttrDict:
        values = asdict(self)
        flat_values = {
            "icon": values["icon"],
            "font_family": values["font_family"],
            "danger": values["danger"],
            "warning": values["warning"],
            "success": values["success"],
            "density_scale": values["density_scale"],
            "button_shape": values["button_shape"],
        }

        return flat_values

    def get_value(self, key: str, default: AttrValue = None) -> AttrValue:
        return self.values.get(key, default)

    def with_updated_values(self, updates: AttrDict) -> "ExtraAttribute":
        """
        Returns a new instance with updated values.
        """
        current = self.values
        merged = {**current, **updates}
        return ExtraAttribute(
            icon=merged.get("icon"),
            font_family=merged.get("font_family", self.font_family),
            danger=merged.get("danger", self.danger),
            warning=merged.get("warning", self.warning),
            success=merged.get("success", self.success),
            density_scale=merged.get("density_scale", self.density_scale),
            button_shape=merged.get("button_shape", self.button_shape),
        )
