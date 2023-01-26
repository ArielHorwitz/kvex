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


class XInputNumber(XInput):
    """XInput for numbers.

    Can compare value to minimum and maximum, automatically setting the `valid` property
    and optionally disabling invalid inputs.

    .. note::
        Using `disable_invalid` may be tricky. Some user input with some `min_value`,
        `max_value`, and `default_valid` values can become frustrating. In particular,
        typing the negative sign or any number starting with digits below the
        `min_value`.
    """

    _number_value = kv.NumericProperty(None)

    def _get_number_value(self) -> int | float:
        return self._number_value

    def _set_number_value(self, value: int | float):
        self._number_value = value

    number_value = kv.AliasProperty(
        _get_number_value,
        _set_number_value,
        bind=["_number_value"],
    )
    """Last valid value as a number type."""
    max_value = kv.NumericProperty(None, allownone=True)
    """Maximum valid value."""
    min_value = kv.NumericProperty(None, allownone=True)
    """Minimum valid value."""
    max_inclusive = kv.BooleanProperty(True)
    """If `max_value` is inclusive. Defaults to True."""
    min_inclusive = kv.BooleanProperty(True)
    """If `min_value` is inclusive. Defaults to True."""
    disable_invalid = kv.BooleanProperty(False)
    """If invalid inputs should be blocked. Defaults to False."""
    cap_invalid = kv.BooleanProperty(True)
    """If input should be capped (only if `disabled_invalid`). Defaults to True."""
    default_valid = kv.NumericProperty(0)
    """Value if text cannot be parsed as a number. See class documentation."""

    def __init__(self, *args, input_filter: str = "float", **kwargs):
        """Initialize the class and bind events."""
        super().__init__(*args, input_filter=input_filter, **kwargs)
        self._assert_properties()
        self.number_value = self.default_valid
        self.text = self._last_valid_text = str(self.default_valid)
        _check_valid = self._check_valid
        self.bind(
            input_filter=self._assert_properties,
            default_valid=self._assert_properties,
            text=_check_valid,
            max_value=_check_valid,
            min_value=_check_valid,
            max_inclusive=_check_valid,
            min_inclusive=_check_valid,
            disable_invalid=_check_valid,
        )
        _check_valid()

    def _get_number(self) -> int | float:
        try:
            return int(self.text) if self.input_filter == "int" else float(self.text)
        except ValueError:
            return self.default_valid

    def _check_valid(self, *args):
        value = self._get_number()
        self.valid = self._max_valid(value) and self._min_valid(value)
        if self.valid:
            self._last_valid_text = self.text
            self._number_value = value
        elif self.disable_invalid:
            if self.cap_invalid:
                self.text = str(self._capped_number_value(value))
            else:
                self.text = self._last_valid_text

    def _max_valid(self, value):
        max_value = self.max_value
        if max_value is None:
            return True
        return value <= max_value if self.max_inclusive else value < max_value

    def _min_valid(self, value):
        min_value = self.min_value
        if min_value is None:
            return True
        return value >= min_value if self.min_inclusive else value > min_value

    def _cap_invalid_text(self):
        value = self._get_number()
        if self.min_value is not None and not self._min_valid(value):
            self.text = str(self.min_value)
        elif self.max_value is not None and not self._max_valid(value):
            self.text = str(self.max_value)

    def _capped_number_value(self, value):
        if self.min_value is not None and not self._min_valid(value):
            return self.min_value
        elif self.max_value is not None and not self._max_valid(value):
            return self.max_value
        return value

    def _assert_properties(self, *args):
        assert self.input_filter in {"float", "int"}
        self.default_valid = self._capped_number_value(self.default_valid)
        assert self._max_valid(self.default_valid)
        assert self._min_valid(self.default_valid)


__all__ = (
    "XInput",
    "XInputNumber",
)
