"""Home of `XColor`, `SubTheme`, and `Theme`.

The most common use of this module is `get_color`. It is able to conveniently retrieve
any color from any palette in `PALETTES`. The `PALETTES` dictionary can be modified to
add or replace palettes.
"""

from typing import NamedTuple
import colorsys
import json
import random
from .assets import ASSETS_DIR


_THEME_DATA_FILE = ASSETS_DIR / "defaultthemes.json"


class XColor:
    """A class to represent a color."""

    def __init__(
        self,
        r: float = 1,
        g: float = 1,
        b: float = 1,
        a: float = 1,
    ):
        """Initialize the class.

        Args:
            r: Red component.
            g: Green component.
            b: Blue component.
            a: Alpha component.
        """
        self.__rgba = r, g, b, a
        self.__hsv = colorsys.rgb_to_hsv(r, g, b)

    @classmethod
    def from_hex(cls, hex_str: str, /) -> "XColor":
        """`XColor` from hex format."""
        rgb = tuple(
            int(hex_str.removeprefix("#")[i:i+2], 16) / 256
            for i in (0, 2, 4)
        )
        return cls(*rgb)

    @classmethod
    def from_hsv(cls, h: float, s: float = 1, v: float = 1, a: float = 1) -> "XColor":
        """`XColor` from hsv values."""
        return cls(*colorsys.hsv_to_rgb(h, s, v), a)

    @classmethod
    def from_name(cls, name: str, /, *, a: float = 1) -> "XColor":
        """`XColor` from color name in `RAINBOW`."""
        return cls(*RAINBOW[name], a)

    def offset_hue(self, offset: float = 0.5, /) -> "XColor":
        """`XColor` that is offset in hue (between 0 and 1) from self."""
        h = (self.h + offset) % 1
        return self.from_hsv(h, self.s, self.v, self.a)

    def modified_hue(self, hue: float, /) -> "XColor":
        """Identical `XColor` with different hue."""
        return self.from_hsv(hue, self.s, self.v, self.a)

    def modified_value(self, value: float, /) -> "XColor":
        """Identical `XColor` with different value."""
        return self.from_hsv(self.h, self.s, value, self.a)

    def modified_saturation(self, saturation: float, /) -> "XColor":
        """Identical `XColor` with different saturation."""
        return self.from_hsv(self.h, saturation, self.v, self.a)

    def modified_alpha(self, alpha: float, /) -> "XColor":
        """Identical `XColor` with different alpha."""
        return self.from_hsv(self.h, self.s, self.v, alpha)

    @classmethod
    def random(cls) -> "XColor":
        """Random `XColor`."""
        return cls.from_hsv(random.random(), 1, 1)

    @classmethod
    def grey(cls, v: float = 0.5, /) -> "XColor":
        """Grey `XColor`."""
        return cls.from_hsv(0, 0, v=v)

    @classmethod
    def white(cls) -> "XColor":
        """White `XColor`."""
        return cls.from_hsv(0, 0, v=1)

    @classmethod
    def black(cls) -> "XColor":
        """Black `XColor`."""
        return cls.from_hsv(0, 0, v=0)

    @property
    def r(self) -> float:
        """The red component."""
        return self.__rgba[0]

    @property
    def g(self) -> float:
        """The green component."""
        return self.__rgba[1]

    @property
    def b(self) -> float:
        """The blue component."""
        return self.__rgba[2]

    @property
    def a(self) -> float:
        """Alpha."""
        return self.__rgba[3]

    @property
    def h(self):
        """Hue."""
        return self.__hsv[0]

    @property
    def s(self):
        """Saturation."""
        return self.__hsv[1]

    @property
    def v(self):
        """Value (from hsv)."""
        return self.__hsv[2]

    @property
    def hsv(self):
        """Hue, saturation, and value."""
        return self.__hsv

    @property
    def rgb(self) -> tuple[float, float, float]:
        """The red, green, and blue components."""
        return self.__rgba[:3]

    @property
    def rgba(self) -> tuple[float, float, float, float]:
        """The red, green, blue, and alpha components."""
        return self.__rgba

    @property
    def hex(self) -> str:
        """Hex representation."""
        return "#" + "".join(hex(round(value * 256))[2:].zfill(2) for value in self.rgb)

    def markup(self, s: str) -> str:
        """Wrap a string in color markup."""
        return f"[color={self.hex}]{s}[/color]"

    def __repr__(self):
        """Object repr."""
        return f"<{self.__class__.__qualname__} {self.hex}>"


RAINBOW = {
    "black": (0.0, 0.0, 0.0),
    "grey": (0.5, 0.5, 0.5),
    "white": (1.0, 1.0, 1.0),
    "red": (0.6, 0.0, 0.1),
    "pink": (0.9, 0.3, 0.4),
    "yellow": (0.8, 0.7, 0.1),
    "orange": (0.7, 0.4, 0.0),
    "lime": (0.1, 0.4, 0.0),
    "green": (0.4, 0.7, 0.1),
    "cyan": (0.1, 0.7, 0.7),
    "blue": (0.1, 0.4, 0.9),
    "navy": (0.0, 0.1, 0.5),
    "violet": (0.7, 0.1, 0.9),
    "purple": (0.4, 0.0, 0.7),
    "magenta": (0.7, 0.0, 0.5),
}
"""Rainbow colors in RGB."""


class SubTheme(NamedTuple):
    """Tuple of XColor for a theme."""

    bg: XColor
    """Background color."""
    fg: XColor
    """Primary foreground (text) color."""
    fg2: XColor
    """Secondary foreground (text) color."""
    accent1: XColor
    """Primary accent color."""
    accent2: XColor
    """Secondary accent color."""

    @classmethod
    def from_hexes(cls, *hexes) -> "SubTheme":
        """`SubTheme` from list of colors in (string) hex format."""
        return cls(*(XColor.from_hex(h) for h in hexes))


SUBTHEME_COLORS = SubTheme._fields
"""Color names in a `SubTheme`."""


class Theme(NamedTuple):
    """Tuple of `SubTheme`s."""

    primary: SubTheme
    """Primary subtheme."""
    secondary: SubTheme
    """Secondary subtheme."""
    accent: SubTheme
    """Accented subtheme."""
    palette: list[XColor]
    """All colors in the palette of this theme."""


SUBTHEME_NAMES = ("primary", "secondary", "accent")
"""`SubTheme` names in a `Theme`."""


def _convert_hexes(*hexes):
    return tuple(XColor.from_hex(h) for h in hexes)


def _import_theme_data() -> dict:
    themes = dict()
    with open(_THEME_DATA_FILE) as f:
        raw_data = json.load(f)
    for theme_name, theme in raw_data.items():
        theme_data = dict()
        theme_data["palette"] = tuple(XColor.from_hex(h) for h in theme["palette"])
        for subtheme_name in SUBTHEME_NAMES:
            theme_data[subtheme_name] = SubTheme(**{
                color_name: XColor.from_hex(color)
                for color_name, color in theme[subtheme_name].items()
            })
        themes[theme_name] = Theme(**theme_data)
    return themes


THEMES = _import_theme_data()
"""Themes data."""

THEME_NAMES = tuple(THEMES.keys())
"""`Theme` names."""


__all__ = (
    "XColor",
    "Theme",
    "SubTheme",
    "SUBTHEME_NAMES",
    "SUBTHEME_COLORS",
    "THEME_NAMES",
    "RAINBOW",
)
