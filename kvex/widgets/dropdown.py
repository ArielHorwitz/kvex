
from .. import kivy as kv
from ..colors import XColor
from .widget import XWidget


class XDropDown(XWidget, kv.DropDown):
    """DropDown."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.make_bg(XColor(0, 0, 0, 0.95))


__all__ = (
    "XDropDown",
)
