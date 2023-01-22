"""Home of `XContainer` and `XPlaceholder`."""

from typing import Callable, Optional
from .. import kivy as kv
from .layouts import XAnchor, XBox
from .label import XLabel
from .button import XButton


class XPlaceholder(XAnchor):
    """A simple label and button widget for `XContainer`."""

    def __init__(
        self,
        label_text: str = "",
        button_text: str = "Return",
        callback: Optional[Callable] = None,
    ):
        """Initialize the class.

        Args:
            label_text: Label text.
            button_text: Button text.
            callback: Function to call when button is pressed. Required to show button.
        """
        super().__init__()
        box = XBox(orientation="vertical")
        self.add_widget(box)
        if label_text:
            label = XLabel(text=label_text)
            label.set_size(hy=4)
            box.add_widget(label)
        if callback:
            button = XButton(text=button_text, on_release=lambda *a: callback())
            button.set_size(x="300dp", y="70dp")
            box.add_widget(XAnchor.wrap_pad(button, pad=False))


class XContainer(XAnchor):
    """A frame with an optional `content` widget and an XPlaceholder fallback."""

    content = kv.ObjectProperty(None, allownone=True)
    """Content widget. Setting None will show the placeholder fallback."""

    def __init__(self, placeholder: Optional[XPlaceholder] = None):
        """Initialize the class with an `XPlaceholder`."""
        super().__init__()
        self._placeholder = placeholder or XPlaceholder()
        self.bind(content=self._on_content)
        self._on_content(self, self.content)

    def _on_content(self, w, content):
        self.clear_widgets()
        if content:
            self.add_widget(content)
        else:
            self.add_widget(self._placeholder)


__all__ = (
    "XContainer",
    "XPlaceholder",
)
