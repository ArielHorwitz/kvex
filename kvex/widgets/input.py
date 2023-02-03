"""Home of `XInput`."""

from .. import kivy as kv
from ..behaviors import XThemed, XFocusBehavior
from .widget import XWidget


class XInput(XThemed, XFocusBehavior, XWidget, kv.TextInput):
    """TextInput."""

    select_on_focus = kv.BooleanProperty(True)
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
        self._fix_textinput_modifiers()
        r = super()._on_textinput_focused(*args, **kwargs)
        if self.focus and self.select_on_focus:
            self.select_all()
        return r

    def _fix_textinput_modifiers(self):
        self._ctrl_l = False
        self._ctrl_r = False
        self._alt_l = False
        self._alt_r = False

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
            self._fix_textinput_modifiers()
            if self.deselect_on_escape:
                self.cancel_selection()
            return True
        return super().keyboard_on_key_down(w, key_pair, text, mods)

    def on_subtheme(self, subtheme):
        """Apply colors."""
        self._refresh_graphics()

    def _refresh_graphics(self, *args):
        st = self.subtheme
        fg = st.fg.rgba if self.valid else st.fg_warn.rgba
        self.background_color = st.bg.rgba
        self.foreground_color = fg
        self.cursor_color = fg
        self.disabled_foreground_color = st.fg_muted.rgba
        self.selection_color = st.accent.modified_alpha(0.5).rgba
        self.hint_text_color = st.fg_muted.rgba
        self._trigger_update_graphics()

    def on_touch_down(self, touch):
        """Override base method to disable consuming scroll touch if not scrolled."""
        if not touch.button.startswith("scroll"):
            return super().on_touch_down(touch)
        x, y = self.scroll_x, self.scroll_y
        ret = super().on_touch_down(touch)
        if (x, y) == (self.scroll_x, self.scroll_y):
            return False
        return ret


class XInputNumber(XInput):
    """XInput for numbers.

    Can compare value to minimum and maximum, automatically setting the `valid` property
    and optionally capping invalid inputs.

    .. note::
        Using `cap_invalid` may be tricky. Some user input with some `min_value` can
        become frustrating for the user. In particular, typing the negative sign or any
        number starting with digits below the `min_value`.
    """

    _number = kv.NumericProperty(None, allownone=True)

    def _get_number(self):
        return self._number

    number = kv.AliasProperty(_get_number, None, bind=["_number"])
    """Text as a number type (int or float). Returns None if text value is invalid."""
    max_value = kv.NumericProperty(None, allownone=True)
    """Maximum valid value."""
    min_value = kv.NumericProperty(None, allownone=True)
    """Minimum valid value."""

    def __init__(self, *args, input_filter: str = "float", **kwargs):
        """Initialize the class and bind events."""
        super().__init__(*args, input_filter=input_filter, **kwargs)
        self.bind(
            input_filter=self._update_properties,
            text=self._update_properties,
            max_value=self._update_properties,
            min_value=self._update_properties,
        )

    def _update_properties(self, *args):
        assert self.input_filter in {"float", "int"}
        text = self.text
        number = None
        if text in {"", "-", ".", "-."}:
            number = 0
        elif self.input_filter == "float":
            number = float(text)
        else:
            number = int(text)
        self._number = number
        self.valid = number is not None and number == self._capped_number(number)

    def _capped_number(self, value):
        if self.min_value is not None:
            value = max(self.min_value, value)
        if self.max_value is not None:
            value = min(self.max_value, value)
        return value


__all__ = (
    "XInput",
    "XInputNumber",
)
