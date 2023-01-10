
from .. import kivy as kv
from .widget import XWidget, XThemed
from .dropdown import XDropDown


class XSpinnerOption(XThemed, XWidget, kv.SpinnerOption):
    """SpinnerOption."""

    def on_subtheme(self, subtheme):
        self.background_color = subtheme.bg.rgba
        self.color = subtheme.fg.rgba


class XSpinner(XThemed, XWidget, kv.Spinner):
    """Spinner."""

    def __init__(self, *args, **kwargs):
        kwargs = dict(dropdown_cls=XDropDown, option_cls=XSpinnerOption) | kwargs
        super().__init__(*args, **kwargs)
        self.register_event_type("on_select")

    def on_select(self, index: int, text: str):
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
