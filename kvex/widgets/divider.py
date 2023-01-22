"""Home of `XDivider`."""

from .. import kivy as kv
from ..colors import XColor
from ..assets import get_image
from ..behaviors import XThemed
from .layouts import XAnchor, XDynamic


class XDivider(XThemed, XDynamic):
    """Themed divider."""

    orientation = kv.OptionProperty("horizontal", options=["horizontal", "vertical"])
    """Orientation of the divider."""
    hint = kv.NumericProperty(0.8)
    """Size hint of the divider along the orientation axis."""
    thickness = kv.ObjectProperty("5dp")
    """Thickness of the divider on the complementary axis (not including margins)."""
    color = kv.ColorProperty()
    """Color of the divider."""

    def __init__(self, **kwargs):
        """Initialize the class."""
        kwargs = dict(margins="3dp") | kwargs
        super().__init__(**kwargs)
        self.inner = XAnchor()
        self.add_widget(self.inner)
        self._refresh_graphics()
        self.bind(
            orientation=self._refresh_graphics,
            hint=self._refresh_graphics,
            thickness=self._refresh_graphics,
            color=self._refresh_graphics,
        )

    def on_subtheme(self, subtheme):
        """Apply subtheme color."""
        self.color = subtheme.accent.rgba

    def _refresh_graphics(self, *args):
        self.inner.make_bg(XColor(*self.color), get_image("rounded_square"))
        if self.orientation == "horizontal":
            self.inner.set_size(hx=self.hint, y=self.thickness)
            self.set_size(hx=1)
        elif self.orientation == "vertical":
            self.inner.set_size(x=self.thickness, hy=self.hint)
            self.set_size(hy=1)


__all__ = (
    "XDivider",
)
