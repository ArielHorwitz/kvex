"""Home of `XCheckBox`."""

from .. import kivy as kv
from .. import util
from ..assets import get_image
from ..behaviors import XThemed, XFocusBehavior
from .widget import XWidget


BG_NORMAL = str(get_image("checkbox"))
BG_DOWN = str(get_image("checkbox_marked"))
BG_NORMAL_DISABLED = str(get_image("checkbox_muted"))
BG_DOWN_DISABLED = str(get_image("checkbox_marked_muted"))


class XCheckBox(XThemed, XFocusBehavior, XWidget, kv.CheckBox):
    """CheckBox with focus."""

    def __init__(self, *args, **kwargs):
        """See class documentation for details."""
        kwargs = dict(
            background_checkbox_disabled_normal=BG_NORMAL_DISABLED,
            background_checkbox_disabled_down=BG_DOWN_DISABLED,
            background_checkbox_normal=BG_NORMAL,
            background_checkbox_down=BG_DOWN,
        ) | kwargs
        super().__init__(*args, **kwargs)
        self.make_bg(source=util.from_atlas("button_disabled"))
        self._kvex_bg_color.a = int(self.focus)
        self.bind(disabled=self._refresh_graphics)

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

    def on_subtheme(self, subtheme):
        """Apply colors."""
        self._refresh_graphics()

    def _refresh_graphics(self, *args):
        color = self.subtheme.fg if not self.disabled else self.subtheme.fg_muted
        self.color = color.rgba


__all__ = (
    "XCheckBox",
)
