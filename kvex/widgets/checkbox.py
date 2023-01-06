
from .. import kivy as kv
from ..behaviors import XFocusBehavior
from .widget import XWidget


class XCheckBox(XFocusBehavior, XWidget, kv.CheckBox):
    """CheckBox with focus."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.make_bg(source="atlas://data/images/defaulttheme/button_disabled")
        self._bg_color.a = int(self.focus)

    def toggle(self, *a):
        """Toggle the active state."""
        self.active = not self.active

    def on_focus(self, w, focus):
        self._bg_color.a = int(focus)

    def keyboard_on_key_down(self, w, key_pair, text, mods):
        """Implement toggling."""
        keycode, key = key_pair
        if key in {"enter", "numpadenter", "spacebar"}:
            self.toggle()
        return super().keyboard_on_key_down(w, key_pair, text, mods)


__all__ = (
    "XCheckBox",
)