"""Home of `XDropDown`."""

from .. import kivy as kv
from .widget import XWidget, XThemed


class XDropDown(XThemed, XWidget, kv.DropDown):
    """DropDown."""

    def __init__(self, *args, **kwargs):
        """Initialize the class."""
        kwargs = dict(subtheme_name="secondary") | kwargs
        super().__init__(*args, **kwargs)

    def on_subtheme(self, subtheme):
        """Override base method."""
        self.make_bg(subtheme.bg.modified_alpha(0.5))


__all__ = (
    "XDropDown",
)
