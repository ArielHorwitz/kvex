"""Home of `XButton` and `XToggleButton`."""

from .. import kivy as kv
from .. import assets
from ..behaviors import XThemed
from .widget import XWidget


BG_NORMAL = str(assets.get_image("button"))
BG_DOWN = str(assets.get_image("button_down"))


class XButton(XThemed, XWidget, kv.Button):
    """Button."""

    def __init__(self, **kwargs):
        """Initialize the class."""
        kwargs = dict(
            markup=True,
            halign="center",
            valign="center",
            background_normal=BG_NORMAL,
            background_down=BG_DOWN,
            border=(2, 1, 2, 1),
        ) | kwargs
        super().__init__(**kwargs)

    def on_touch_down(self, m):
        """Overrides base class method to only react to left clicks."""
        if m.button != "left":
            return False
        return super().on_touch_down(m)

    def on_subtheme(self, subtheme):
        """Override base method."""
        self.background_color = subtheme.bg.rgba
        self.color = subtheme.fg.rgba


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
