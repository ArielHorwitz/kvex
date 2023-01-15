"""Home of `XSpinner` and `XSpinnerOption`."""

from .. import kivy as kv
from .. import assets
from ..behaviors import XThemed
from .widget import XWidget
from .dropdown import XDropDown


BG_NORMAL = str(assets.get_image("spinner"))
BG_DOWN = str(assets.get_image("button_down"))


class XSpinnerOption(XThemed, XWidget, kv.SpinnerOption):
    """SpinnerOption."""

    def __init__(self, *args, **kwargs):
        """Initialize the class with defaults."""
        kwargs = dict(
            background_normal=BG_NORMAL,
            background_down=BG_DOWN,
        ) | kwargs
        super().__init__(*args, **kwargs)

    def on_subtheme(self, subtheme):
        """Override base method."""
        self.background_color = subtheme.bg.rgba
        self.color = subtheme.fg.rgba


class XSpinner(XThemed, XWidget, kv.Spinner):
    """Spinner."""

    def __init__(self, *args, **kwargs):
        """Initialize the class with defaults."""
        kwargs = dict(
            dropdown_cls=XDropDown,
            option_cls=XSpinnerOption,
            background_normal=BG_NORMAL,
            background_down=BG_DOWN,
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

    def on_subtheme(self, subtheme):
        """Override base method."""
        self.background_color = subtheme.bg.rgba
        self.color = subtheme.fg.rgba


__all__ = (
    "XSpinner",
    "XSpinnerOption",
)
