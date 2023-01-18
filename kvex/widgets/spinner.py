"""Home of `XSpinner` and `XSpinnerOption`."""

from .. import kivy as kv
from .. import assets
from ..util import DEFAULT_BUTTON_HEIGHT
from .widget import XWidget
from .button import XThemedButton
from .dropdown import XDropDown


BG_NORMAL = str(assets.get_image("spinner"))
BG_DOWN = str(assets.get_image("button_down"))


class XSpinnerOption(XThemedButton, XWidget, kv.SpinnerOption):
    """SpinnerOption."""

    def __init__(self, **kwargs):
        """Initialize the class with defaults."""
        kwargs = dict(
            size_hint_y=None,
            height=DEFAULT_BUTTON_HEIGHT,
            background_normal=BG_NORMAL,
            background_down=BG_DOWN,
            background_disabled_normal=BG_NORMAL,
            background_disabled_down=BG_DOWN,
        ) | kwargs
        super().__init__(**kwargs)


class XSpinner(XThemedButton, XWidget, kv.Spinner):
    """Spinner."""

    def __init__(self, *args, **kwargs):
        """Initialize the class with defaults."""
        kwargs = dict(
            size_hint_y=None,
            height=DEFAULT_BUTTON_HEIGHT,
            dropdown_cls=XDropDown,
            option_cls=XSpinnerOption,
            background_normal=BG_NORMAL,
            background_down=BG_DOWN,
            background_disabled_normal=BG_NORMAL,
            background_disabled_down=BG_DOWN,
        ) | kwargs
        super().__init__(*args, **kwargs)
        self.register_event_type("on_select")

    def on_select(self, index: int, text: str):
        """Called when an item is selected."""
        pass

    def _on_dropdown_select(self, w, text, *largs):
        if self.text_autoupdate:
            self.text = text
        self.is_open = False
        self.dispatch("on_select", self.values.index(text), text)


__all__ = (
    "XSpinner",
    "XSpinnerOption",
)
