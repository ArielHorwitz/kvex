
from .. import kivy as kv
from ..colors import XColor
from .widget import XWidget, XThemed


class XDropDown(XThemed, XWidget, kv.DropDown):
    """DropDown."""

    def __init__(self, *args, **kwargs):
        kwargs = dict(subtheme_name="secondary") | kwargs
        super().__init__(*args, **kwargs)
        self.make_bg(XColor(0, 0, 0, 0.95))

    def on_subtheme(self, subtheme):
        """Override base method."""
        self.make_bg(subtheme.bg)


__all__ = (
    "XDropDown",
)
