
from .. import kivy as kv
from ..util import XColor, ColorType
from .widget import XWidget


class XButton(XWidget, kv.Button):
    """Button."""

    def __init__(
        self,
        background_color: ColorType = XColor.from_name("blue", v=0.5).rgba,
        **kwargs,
    ):
        """Initialize the class.

        Args:
            background_color: Background color of the button.
        """
        kwargs = {
            "markup": True,
            "halign": "center",
            "valign": "center",
        } | kwargs
        super().__init__(**kwargs)
        self.background_color = background_color

    def on_touch_down(self, m):
        """Overrides base class method to only react to left clicks."""
        if m.button != "left":
            return False
        return super().on_touch_down(m)


class XToggleButton(kv.ToggleButtonBehavior, XButton):
    """ToggleButton."""

    active = kv.BooleanProperty(False)
    """Behaves like an alias for the `state` property being "down"."""

    def __init__(self, **kwargs):
        """Same arguments as kivy Button."""
        super().__init__(**kwargs)
        self.bind(state=self._set_active)
        self.bind(active=self._set_state)

    def toggle(self, *args):
        """Toggles the active state of the button."""
        self.active = not self.active

    def _set_state(self, *args):
        self.state = "down" if self.active else "normal"

    def _set_active(self, *args):
        self.active = self.state == "down"


__all__ = (
    "XButton",
    "XToggleButton",
)