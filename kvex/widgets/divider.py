"""Home of `XDivider`."""

from .. import kivy as kv
from ..util import sp2pixels
from ..colors import XColor
from ..assets import get_image
from ..behaviors import XThemed
from .layouts import XAnchor


class XDivider(XThemed, XAnchor):
    """Themed divider."""

    orientation = kv.OptionProperty("horizontal", options=["horizontal", "vertical"])
    """Orientation of the divider."""
    divider_hint = kv.NumericProperty(0.8)
    """Size hint of the divider."""
    thickness = kv.ObjectProperty("5dp")
    """Thickness of the divider not including padding."""
    color = kv.ColorProperty()
    """Color of the divider."""

    def __init__(self, **kwargs):
        """Initialize the class."""
        kwargs = dict(padding=["3dp", "3dp"]) | kwargs
        super().__init__(**kwargs)
        self.inner = XAnchor()
        self.add_widget(self.inner)
        self._refresh_graphics()
        self.bind(
            orientation=self._refresh_graphics,
            divider_hint=self._refresh_graphics,
            thickness=self._refresh_graphics,
            color=self._refresh_graphics,
        )

    def on_subtheme(self, subtheme):
        """Apply subtheme color."""
        self.color = subtheme.accent.rgba

    def _refresh_graphics(self, *args):
        self.inner.make_bg(
            color=XColor(*self.color),
            source=get_image("xframe_bg"),
        )
        pad = self.padding[1 if self.orientation == "horizontal" else 0]
        thick = sp2pixels(self.thickness) + sp2pixels(pad) * 2
        if self.orientation == "horizontal":
            self.set_size(hx=1, y=thick)
            self.inner.set_size(hx=self.divider_hint, hy=1)
        elif self.orientation == "vertical":
            self.set_size(x=thick, hy=1)
            self.inner.set_size(hx=1, hy=self.divider_hint)


__all__ = (
    "XDivider",
)
