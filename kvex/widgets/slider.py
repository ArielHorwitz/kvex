
from typing import Optional, Any
from .. import kivy as kv
from .widget import XWidget
from .label import XLabel
from .layouts import XBox


class XSlider(XWidget, kv.Slider):
    """Slider."""

    pass


class XSliderText(XBox):
    """Slider with Label."""

    def __init__(
        self,
        prefix: str = "",
        rounding: int = 3,
        box_kwargs: Optional[dict[str, Any]] = None,
        label_kwargs: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        """Initialize the class.

        Args:
            prefix: Text to prefix the value presented in the label.
            rounding: How many decimal places to show.
            box_kwargs: Keyword arguments for XBox.
            label_kwargs: Keyword arguments for XLabel.
            kwargs: Keyword arguments for XSlider.
        """
        box_kwargs = {} if box_kwargs is None else box_kwargs
        label_kwargs = {} if label_kwargs is None else label_kwargs
        label_kwargs = {"halign": "left"} | label_kwargs
        slider_kwargs = {"cursor_size": (25, 25)} | kwargs
        super().__init__(**box_kwargs)
        self.rounding = rounding
        self.prefix = prefix
        self.label = XLabel(**label_kwargs)
        self.label.set_size(hx=0.2)
        self.slider = XSlider(**slider_kwargs)
        self.add_widgets(self.label, self.slider)
        self.slider.bind(value=self._set_text)
        self._set_text(self, self.slider.value)

    def _set_text(self, w, value):
        if isinstance(value, float):
            value = round(value, self.rounding)
        if value == round(value):
            value = int(value)
        self.label.text = str(f"{self.prefix}{value}")


__all__ = (
    "XSlider",
    "XSliderText",
)
