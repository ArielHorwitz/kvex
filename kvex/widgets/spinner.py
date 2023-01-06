
from .. import kivy as kv
from .widget import XWidget
from .dropdown import XDropDown


class XSpinnerOption(kv.SpinnerOption):
    """SpinnerOption."""

    pass


class XSpinner(XWidget, kv.Spinner):
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


__all__ = (
    "XSpinner",
    "XSpinnerOption",
)
