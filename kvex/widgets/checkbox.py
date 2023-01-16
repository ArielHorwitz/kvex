"""Home of `XCheckBox`."""

from .. import kivy as kv
from .. import util
from ..behaviors import XFocusBehavior
from .widget import XWidget


class XCheckBox(XFocusBehavior, XWidget, kv.CheckBox):
    """CheckBox with focus."""

    def __init__(self, *args, **kwargs):
        """See class documentation for details."""
        super().__init__(*args, **kwargs)
        self.make_bg(source=util.from_atlas("button_disabled"))
        self._kvex_bg_color.a = int(self.focus)

    def toggle(self, *a):
        """Toggle the active state."""
        self.active = not self.active

    def on_focus(self, w, focus):
        """Set background alpha."""
        self._kvex_bg_color.a = int(focus)

    def keyboard_on_key_down(self, w, key_pair, text, mods):
        """Implement toggling."""
        keycode, key = key_pair
        if key in {"enter", "numpadenter", "spacebar"}:
            self.toggle()
        return super().keyboard_on_key_down(w, key_pair, text, mods)


__all__ = (
    "XCheckBox",
)
