
import re
from .. import kivy as kv
from ..behaviors import XThemed, XFocusBehavior
from .widget import XWidget


class XInput(XThemed, XFocusBehavior, XWidget, kv.TextInput):
    """TextInput with sane defaults."""

    select_on_focus = kv.BooleanProperty(False)
    deselect_on_escape = kv.BooleanProperty(True)

    def __init__(self, **kwargs):
        """Initialize the class.

        Args:
            multiline: If should allow multiple lines.
            background_color: Color of the background.
            foreground_color: Color of the foreground.
            disabled_foreground_color: Color of the foreground when disabled.
            text_validate_unfocus: If focus should be removed after validation
                (pressing enter on a single-line widget).
            write_tab: Allow tabs to be written.
            kwargs: Keyword arguments for TextInput.
        """
        kwargs = dict(
            multiline=False,
            background_color=(0.2, 0.2, 0.2, 1),
            foreground_color=(1, 1, 1, 1),
            disabled_foreground_color=(0.5, 0.5, 0.5, 0.5),
            text_validate_unfocus=False,
            write_tab=False,

        ) | kwargs
        super().__init__(**kwargs)

    def _on_textinput_focused(self, *args, **kwargs):
        """Overrides base method to handle selection on focus."""
        r = super()._on_textinput_focused(*args, **kwargs)
        if self.focus and self.select_on_focus:
            self.select_all()
        return r

    def reset_cursor_selection(self, *a):
        """Resets the cursor position and selection."""
        self.cancel_selection()
        self.cursor = 0, 0
        self.scroll_x = 0
        self.scroll_y = 0

    def keyboard_on_key_down(self, w, key_pair, text, mods):
        """Override base method to deselect on escape."""
        keycode, key = key_pair
        if key == "escape":
            if self.deselect_on_escape:
                self.cancel_selection()
            return True
        return super().keyboard_on_key_down(w, key_pair, text, mods)

    def on_subtheme(self, subtheme):
        """Override base method."""
        self.background_color = subtheme.bg.rgba
        self.foreground_color = subtheme.fg.rgba


class XIntInput(XInput):
    digits_pattern = re.compile('[^0-9]')

    def insert_text(self, substring, *args, **kwargs):
        s = re.sub(self.digits_pattern, '', substring)
        return super().insert_text(s, *args, **kwargs)


class XFloatInput(XInput):
    digits_pattern = re.compile('[^0-9]')

    def insert_text(self, substring, *args, **kwargs):
        if '.' in self.text:
            s = re.sub(self.digits_pattern, '', substring)
        else:
            s = '.'.join(
                re.sub(self.digits_pattern, '', s)
                for s in substring.split('.', 1)
            )
        return super().insert_text(s, *args, **kwargs)


__all__ = (
    "XInput",
    "XIntInput",
    "XFloatInput",
)
