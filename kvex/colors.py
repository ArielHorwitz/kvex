"""Home of `get_color`, `XColor`.

The most common use of this module is `get_color`. It is able to conveniently retrieve
any color from any palette in `PALETTES`. The `PALETTES` dictionary can be modified to
add or replace palettes.
"""

from typing import NamedTuple
import colorsys


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
        """Convert hex string to rgb floats."""
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

    def modify_value(self, value: float, /) -> "XColor":
        """Identical `XColor` with different value."""
        return self.from_hsv(self.h, self.s, value, self.a)

    def modify_saturation(self, saturation: float, /) -> "XColor":
        """Identical `XColor` with different saturation."""
        return self.from_hsv(self.h, saturation, self.v, self.a)

    def modify_alpha(self, alpha: float, /):
        """Identical `XColor` with different alpha."""
        return self.from_hsv(self.h, self.s, self.v, alpha)

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
    def as_hex(self) -> str:
        """Hex representation."""
        return "#" + "".join(hex(round(value * 256))[2:].zfill(2) for value in self.rgb)

    def markup(self, s: str) -> str:
        """Wrap a string in color markup."""
        return f"[color={self.as_hex}]{s}[/color]"

    def __repr__(self):
        """Object repr."""
        cls_name = f"{self.__class__.__qualname__} object"
        idhex = f"at 0x{id(self):x}"
        return f"<{cls_name} {self.rgba} {idhex}>"


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
    fg: XColor
    accent1: XColor
    accent2: XColor

    @classmethod
    def from_hexes(cls, *hexes):
        return cls(*(XColor.from_hex(h) for h in hexes))


class Theme(NamedTuple):
    """Tuple of SubThemes."""
    primary: SubTheme
    secondary: SubTheme
    accent: SubTheme
    palette: list[XColor]


def _convert_hexes(*hexes):
    return tuple(XColor.from_hex(h) for h in hexes)


THEMES: dict[str, Theme] = dict(
    midnight=Theme(
        palette=_convert_hexes("#161722", "#25273C", "#CACDE8", "#E4E5F1", "#777A92"),
        primary=SubTheme.from_hexes("#161722", "#E4E5F1", "#25273C", "#777A92"),
        secondary=SubTheme.from_hexes("#25273C", "#E4E5F1", "#161722", "#777A92"),
        accent=SubTheme.from_hexes("#CACDE8", "#161722", "#777A92", "#25273C"),
    ),
    darkpop=Theme(
        palette=_convert_hexes("#082032", "#2C394B", "#334756", "#FF4C29"),
        primary=SubTheme.from_hexes("#082032", "#FF4C29", "#334756", "#2C394B"),
        secondary=SubTheme.from_hexes("#2C394B", "#FF4C29", "#082032", "#334756"),
        accent=SubTheme.from_hexes("#334756", "#FF4C29", "#082032", "#2C394B"),
    ),
    deepbrown=Theme(
        palette=_convert_hexes("#1A120B", "#3C2A21", "#D5CEA3", "#E5E5CB"),
        primary=SubTheme.from_hexes("#1A120B", "#E5E5CB", "#3C2A21", "#D5CEA3"),
        secondary=SubTheme.from_hexes("#3C2A21", "#E5E5CB", "#1A120B", "#D5CEA3"),
        accent=SubTheme.from_hexes("#D5CEA3", "#1A120B", "#3C2A21", "#E5E5CB"),
    ),
    market=Theme(
        palette=_convert_hexes("#342628", "#F7F4EF", "#FEAA00", "#788402"),
        primary=SubTheme.from_hexes("#342628", "#F7F4EF", "#FEAA00", "#788402"),
        secondary=SubTheme.from_hexes("#F7F4EF", "#342628", "#788402", "#FEAA00"),
        accent=SubTheme.from_hexes("#FEAA00", "#342628", "#F7F4EF", "#788402"),
    ),
    muted=Theme(
        palette=_convert_hexes("#F7F1F0", "#A15C38", "#C3A6A0", "#262220"),
        primary=SubTheme.from_hexes("#F7F1F0", "#262220", "#A15C38", "#C3A6A0"),
        secondary=SubTheme.from_hexes("#A15C38", "#F7F1F0", "#C3A6A0", "#262220"),
        accent=SubTheme.from_hexes("#C3A6A0", "#262220", "#A15C38", "#F7F1F0"),
    ),
    ocean=Theme(
        palette=_convert_hexes("#18B7BE", "#F9F7F0", "#178CA4", "#072A40"),
        primary=SubTheme.from_hexes("#18B7BE", "#F9F7F0", "#178CA4", "#072A40"),
        secondary=SubTheme.from_hexes("#F9F7F0", "#072A40", "#178CA4", "#18B7BE"),
        accent=SubTheme.from_hexes("#178CA4", "#F9F7F0", "#18B7BE", "#072A40"),
    ),
    subtle=Theme(
        palette=_convert_hexes("#013328", "#CC8B65", "#E3DCD2", "#100C0D"),
        primary=SubTheme.from_hexes("#013328", "#CC8B65", "#E3DCD2", "#100C0D"),
        secondary=SubTheme.from_hexes("#CC8B65", "#013328", "#E3DCD2", "#100C0D"),
        accent=SubTheme.from_hexes("#E3DCD2", "#013328", "#CC8B65", "#100C0D"),
    ),
    eve=Theme(
        palette=_convert_hexes("#00003C", "#3B185F", "#C060A1", "#F0CAA3"),
        primary=SubTheme.from_hexes("#00003C", "#F0CAA3", "#3B185F", "#C060A1"),
        secondary=SubTheme.from_hexes("#3B185F", "#F0CAA3", "#00003C", "#C060A1"),
        accent=SubTheme.from_hexes("#C060A1", "#00003C", "#3B185F", "#F0CAA3"),
    ),
    vineyard=Theme(
        palette=_convert_hexes("#431D32", "#2A3759", "#778FD2", "#B7CB99", "#3D5220"),
        primary=SubTheme.from_hexes("#2A3759", "#B7CB99", "#431D32", "#3D5220"),
        secondary=SubTheme.from_hexes("#431D32", "#B7CB99", "#2A3759", "#3D5220"),
        accent=SubTheme.from_hexes("#3D5220", "#778FD2", "#431D32", "#B7CB99"),
    ),
    travel=Theme(
        palette=_convert_hexes("#285185", "#6F4849", "#D67940", "#CCD9E2"),
        primary=SubTheme.from_hexes("#285185", "#CCD9E2", "#6F4849", "#D67940"),
        secondary=SubTheme.from_hexes("#6F4849", "#CCD9E2", "#D67940", "#285185"),
        accent=SubTheme.from_hexes("#D67940", "#285185", "#6F4849", "#CCD9E2"),
    ),
    toucan=Theme(
        palette=_convert_hexes("#5A8100", "#FFF9E9", "#FFB400", "#FF6C02"),
        primary=SubTheme.from_hexes("#5A8100", "#FFF9E9", "#FFB400", "#FF6C02"),
        secondary=SubTheme.from_hexes("#FFB400", "#5A8100", "#FFF9E9", "#FF6C02"),
        accent=SubTheme.from_hexes("#FF6C02", "#FFF9E9", "#FFB400", "#5A8100"),
    ),
    coral=Theme(
        palette=_convert_hexes("#D96846", "#CDCBD6", "#596235", "#2F3020"),
        primary=SubTheme.from_hexes("#D96846", "#CDCBD6", "#596235", "#2F3020"),
        secondary=SubTheme.from_hexes("#CDCBD6", "#2F3020", "#D96846", "#596235"),
        accent=SubTheme.from_hexes("#596235", "#CDCBD6", "#D96846", "#2F3020"),
    ),
)
SUBTHEMES = ("primary", "secondary", "accent")


__all__ = (
    "XColor",
    "THEMES",
    "SUBTHEMES",
    "Theme",
    "RAINBOW",
)
