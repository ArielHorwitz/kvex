"""Home of `get_color`, `XColor`, and `Palette`.

The most common use of this module is `get_color`. It is able to conveniently retrieve
and alter any color from any palette in `PALETTES`. The `PALETTES` dictionary can be
modified to add or change palettes.
"""

import colorsys
import functools


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

    def multiply_saturation(self, multiplier: float, /) -> "XColor":
        """`XColor` that is multiplied in saturation from self."""
        return self.from_hsv(self.h, self.s * multiplier, self.v, self.a)

    def multiply_value(self, multiplier: float, /) -> "XColor":
        """`XColor` that is multiplied in value from self."""
        return self.from_hsv(self.h, self.s, self.v * multiplier, self.a)

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


class Palette:
    """A collection of colors in a palette.

    It is recommended to use `kvex.colors.get_color` instead of using Palettes directly.

    A palette has 3 pairs of colors (as seen in `Palette.COLOR_NAMES`):
    * `main` (and `main_`)
    * `primary` (and `primary_`)
    * `second` (and `second_`)

    These can be accessed via `Palette.get_color`.
    """

    COLOR_NAMES = ("main", "main_", "primary", "primary_", "second", "second_")
    """Names of colors in a palette."""

    def __init__(self, *, main, main_, primary, primary_, second, second_):
        """Initialize the class with 3 colors (in RGB) of a palette."""
        self._color_main = main
        self._color_main_ = main_
        self._color_primary = primary
        self._color_primary_ = primary_
        self._color_second = second
        self._color_second_ = second_
        self.__hash = hash((main, main_, primary, primary_, second, second_))

    def __hash__(self) -> int:
        """Object hash."""
        return self.__hash

    @functools.cache
    def get_color(self, name: str, /) -> XColor:
        """Get a color by name (see: `Palette.COLOR_NAMES`)."""
        return XColor(*getattr(self, f"_color_{name}"))


PALETTES: dict[str, Palette] = dict(
    forest=Palette(
        main=(0.16, 0.22, 0.34),  # dark blue
        main_=(0.47, 0.56, 0.82),  # light blue
        primary=(0.24, 0.32, 0.13),  # dark green
        primary_=(0.72, 0.80, 0.60),  # light green
        second=(0.26, 0.11, 0.20),  # dark purple
        second_=(0.58, 0.25, 0.45),  # dark pink
    ),
)
"""All registered palettes."""
PALETTES["default"] = PALETTES["forest"]


def get_color(
    name: str,
    /,
    palette: str = "default",
    *,
    v: float = 1,
    s: float = 1,
) -> XColor:
    """Get a color from a `Palette` in `PALETTES`.

    See `Palette.COLOR_NAMES` for names. Can also take `v` and `s` for modifying the
    color using `XColor.multiply_value` and `XColor.multiply_saturation`.

    Uses `Palette.get_color`. See also: `PALETTES`, `Palette`.
    """
    return XColor(*_get_color(palette, name, v, s).rgba)


@functools.cache
def _get_color(palette, name, v, s):
    color = PALETTES[palette].get_color(name)
    if v != 1:
        color = color.multiply_value(v)
    if s != 1:
        color = color.multiply_saturation(s)
    return color


__all__ = (
    "get_color",
    "XColor",
    "Palette",
    "PALETTES",
    "RAINBOW",
)
