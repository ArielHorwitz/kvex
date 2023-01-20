"""Home of `XInput`."""

from .. import kivy as kv
from ..behaviors import XThemed, XFocusBehavior
from .widget import XWidget


class XInput(XThemed, XFocusBehavior, XWidget, kv.TextInput):
    """TextInput."""

    select_on_focus = kv.BooleanProperty(False)
    """If all text is selected when entering focus. Defaults to False."""
    deselect_on_escape = kv.BooleanProperty(True)
    """If text is deselected when escape is pressed. Defaults to True."""
    valid = kv.BooleanProperty(True)
    """If current text is valid."""

    def __init__(self, **kwargs):
        """Initialize the class."""
        kwargs = dict(
            multiline=False,
            text_validate_unfocus=False,
            write_tab=False,
        ) | kwargs
        super().__init__(**kwargs)
        self.bind(valid=self._refresh_graphics)

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
        """Apply colors."""
        self._refresh_graphics()

    def _refresh_graphics(self, *args):
        st = self.subtheme
        self.background_color = st.bg.rgba
        self.foreground_color = st.fg.rgba if self.valid else st.fg_warn.rgba
        self.cursor_color = st.fg.rgba
        self.disabled_foreground_color = st.fg_muted.rgba
        self.selection_color = st.accent.modified_alpha(0.5).rgba
        self.hint_text_color = st.fg_muted.rgba
        self._trigger_update_graphics()


__all__ = (
    "XInput",
)
