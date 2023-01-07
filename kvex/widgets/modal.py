"""Home of `XModalView` and `XModal`."""

from .. import kivy as kv
from .widget import XWidget


class XModalView(XWidget, kv.ModalView):
    """ModalView."""

    pass


__all__ = (
    "XModalView",
)
