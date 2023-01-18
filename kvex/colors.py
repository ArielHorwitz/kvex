"""Home of `XColor`, `SubTheme`, and `Theme`."""

import colorsys
import functools
import random
import tomli
from .assets import ASSETS_DIR


_THEME_DATA_FILE = ASSETS_DIR / "defaultthemes.toml"


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
        self.__hash = hash(self.__rgba)

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

    def __hash__(self) -> int:
        """Object hash."""
        return self.__hash

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


class SubTheme:
    """Collection of `XColor`s meant to be used in widgets.

    SubThemes are designed for a particular `Theme`, using its color palette. At least
    "bg" and "fg" are required to create a SubTheme (see:  `COLOR_NAMES`).

    Colors can be accessed via name:
    ```python3
    subtheme.bg
    subtheme.fg
    subtheme.accent
    ```

    Or via mapping:
    ```python3
    for name, color in dict(subtheme).items():
        ...
    ```
    """

    COLOR_NAMES = (
        "bg",
        "fg",
        "fg_accent",
        "fg_muted",
        "fg_warn",
        "accent",
    )
    """Names of colors in a SubTheme."""

    def __init__(self, **kwargs):
        """Initialize the class with colors from `COLOR_NAMES`.

        See class documentation.
        """
        assert "bg" in kwargs
        assert "fg" in kwargs
        extra_colors = set(kwargs.keys()) - set(self.COLOR_NAMES)
        if extra_colors:
            raise KeyError(f"Unknown color names: {extra_colors}")
        # Set defaults
        fg = kwargs["fg"]
        kwargs["fg_accent"] = kwargs.get("fg_accent", fg)
        kwargs["fg_warn"] = kwargs.get("fg_warn", fg)
        kwargs["fg_muted"] = fg_muted = kwargs.get("fg_muted", fg)
        kwargs["accent"] = kwargs.get("accent", fg_muted)
        self._colors = tuple(kwargs[color] for color in self.COLOR_NAMES)
        self._hash = hash(self._colors)

    def __getattr__(self, name):
        """Get color by name."""
        return self[name]

    @functools.cache
    def __getitem__(self, key) -> XColor:
        """Get SubTheme by name."""
        if key in self.COLOR_NAMES:
            index = self.COLOR_NAMES.index(key)
            return self._colors[index]
        raise KeyError(f"No such color name {key!r}")

    def keys(self) -> tuple[str, ...]:
        """Tuple of color names."""
        return self.COLOR_NAMES

    def __hash__(self) -> int:
        """Object hash."""
        return self._hash

    def __repr__(self):
        """Object repr."""
        cls_name = f"{self.__class__.__qualname__} object"
        idhex = f"at 0x{id(self):x}"
        return f"<{cls_name} {self.bg.hex} {self.fg.hex} {idhex}>"


class Theme:
    """A collection of `SubTheme`s designed using a single color palette.

    SubThemes can be accessed via name:
    ```python3
    theme.primary
    theme.secondary
    theme.accent
    ```

    Or via mapping:
    ```python3
    for name, subtheme in dict(theme).items():
        ...
    ```
    """

    SUBTHEME_NAMES = ("primary", "secondary", "accent")
    """Names of SubThemes in a Theme."""

    def __init__(
        self,
        *,
        palette: tuple[XColor, ...],
        primary: SubTheme,
        secondary: SubTheme,
        accent: SubTheme,
    ):
        """Initialize the class with palette and `SubTheme`s.

        Args:
            palette: Tuple of `XColor`s used in this theme.
            primary: Primary SubTheme (used most)
            secondary: Secondary SubTheme
            accent: Accent SubTheme (used least)
        """
        self.palette = tuple(palette)
        self._subthemes = (primary, secondary, accent)
        self._hash = hash((self.palette, self._subthemes))

    def __getattr__(self, name):
        """Get subtheme by name."""
        return self[name]

    @functools.cache
    def __getitem__(self, key) -> SubTheme:
        """Get SubTheme by name."""
        if key in self.SUBTHEME_NAMES:
            index = self.SUBTHEME_NAMES.index(key)
            return self._subthemes[index]
        raise KeyError(f"No such subtheme name {key!r}")

    def keys(self) -> tuple[str, ...]:
        """Tuple of subtheme names."""
        return self.SUBTHEME_NAMES

    def __hash__(self) -> int:
        """Object hash."""
        return self._hash

    def __repr__(self) -> str:
        """Object repr."""
        return f"<{self.__class__.__qualname__} object {self.palette}>"


def _import_theme_data() -> dict:
    themes = dict()
    with open(_THEME_DATA_FILE, "rb") as f:
        raw_data = tomli.load(f)
    for theme_name, theme in raw_data.items():
        theme_data = dict()
        theme_data["palette"] = tuple(XColor.from_hex(h) for h in theme["palette"])
        for subtheme_name in Theme.SUBTHEME_NAMES:
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
    "THEME_NAMES",
    "RAINBOW",
)
