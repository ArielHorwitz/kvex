
from typing import Optional
from .. import kivy as kv
from .widget import XWidget
from .layouts import XAnchor


class XModalView(XWidget, kv.ModalView):
    pass


class XModal(XAnchor):
    """A XAnchor with an XInputManager that can de/attach to a container."""

    def __init__(self, container: XAnchor, name: str = "Unnamed", **kwargs):
        super().__init__(**kwargs)
        self.container = container
        self.bind(parent=self._on_parent)

    def toggle(self, *args, set_as: Optional[bool] = None):
        if set_as is None:
            set_as = self.parent is None
        if set_as:
            self.open()
        else:
            self.dismiss()

    def open(self, *args):
        if self.parent is not None:
            return
        self.container.add_widget(self)

    def dismiss(self, *args):
        if self.parent is None:
            return
        self.container.remove_widget(self)

    def _on_parent(self, w, parent):
        self.im.active = parent is not None


__all__ = (
    "XModal",
    "XModalView",
)
