
from .. import kivy as kv
from ..colors import XColor
from .layouts import XBox
from .label import XLabelClick
from .dropdown import XDropDown
from .slider import XSliderText


class XPickColor(XBox):
    """Color picking widget."""

    color = kv.ObjectProperty(XColor(0.5, 0.5, 0.5, 1))

    def __init__(self, **kwargs):
        """Same keyword arguments for Slider."""
        super().__init__(orientation="vertical")
        self.set_size(x=300, y=100)
        update_color = self._update_from_sliders
        self.sliders = []
        for i, c in enumerate("RGBA"):
            slider_kwargs = {
                "range": (0, 1),
                "step": 0.01,
                "value_track": True,
                "value_track_color": XColor(**{c.lower(): 0.75}).rgba,
                "value_track_width": "6dp",
                "cursor_size": (0, 0),
            } | kwargs
            s = XSliderText(**slider_kwargs)
            s.slider.bind(value=update_color)
            self.add_widget(s)
            self.sliders.append(s)
        self.r, self.g, self.b, self.a = self.sliders
        self.set_color(self.color)

    def set_color(self, color: XColor):
        """Set the current color."""
        self.r.slider.value = color.r
        self.g.slider.value = color.g
        self.b.slider.value = color.b
        self.a.slider.value = color.a

    def _update_from_sliders(self, *a):
        color = XColor(
            self.r.slider.value,
            self.g.slider.value,
            self.b.slider.value,
            self.a.slider.value,
        )
        is_bright = sum(color.rgb) > 1.5
        for s in self.sliders:
            s.label.color = (0, 0, 0, 1) if is_bright else (1, 1, 1, 1)
        self.make_bg(color)
        self.color = color


class XSelectColor(XLabelClick):
    """An XPickColor that drops down from an XLabelClick."""

    def __init__(
        self,
        prefix: str = "[u]Color:[/u]\n",
        show_color_values: bool = True,
        **kwargs,
    ):
        """Initialize the class.

        Args:
            prefix: Text to show before the RGB values.
            show_color_values: Show the RGB values of the current color.
            kwargs: Keyword arguments for the XLabelClick.
        """
        self.prefix = prefix
        self.show_color_values = show_color_values
        super().__init__(**kwargs)
        self.picker = XPickColor()
        self.dropdown = XDropDown(auto_width=False, on_dismiss=self._on_color)
        self.dropdown.set_size(*self.picker.size)
        self.dropdown.add_widget(self.picker)
        self.picker.bind(size=lambda w, s: self.dropdown.set_size(*s))
        self.bind(on_release=self.dropdown.open)
        self.on_color()

    def _on_color(self, *args):
        color = self.picker.color
        self.make_bg(color)
        text = self.prefix
        if self.show_color_values:
            text += " , ".join(str(round(c, 2)) for c in color.rgba)
        self.text = text


__all = (
    "XPickColor",
    "XSelectColor",
)
