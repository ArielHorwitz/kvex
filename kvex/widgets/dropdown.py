"""Home of `XDropDown`."""

from .. import kivy as kv
from ..behaviors import XThemed
from .widget import XWidget


class XDropDown(XThemed, XWidget, kv.DropDown):
    """DropDown."""

    bg_alpha = kv.NumericProperty(0.95)
    """Alpha component of background color."""

    def __init__(self, **kwargs):
        """Initialize the class."""
        super().__init__(**kwargs)
        self.bind(bg_alpha=self._refresh_graphics)

    def on_subtheme(self, subtheme):
        """Apply background."""
        self._refresh_graphics()

    def _refresh_graphics(self, *args):
        bg = self.subtheme.bg.modified_alpha(self.bg_alpha)
        self.make_bg(bg)


__all__ = (
    "XDropDown",
)
