
from .. import kivy as kv
from ..util import XColor
from .widget import XWidget


class XDropDown(XWidget, kv.DropDown):
    """DropDown."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.make_bg(XColor(v=0, a=0.95))


__all__ = (
    "XDropDown",
)
