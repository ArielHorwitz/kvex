"""Home of `XButton` and `XToggleButton`."""

from .. import kivy as kv
from .. import assets
from ..behaviors import XThemed
from .widget import XWidget


BG_NORMAL = str(assets.get_image("button"))
BG_DOWN = str(assets.get_image("button_down"))


class XThemedButton(XThemed):
    """Mixin for buttons using themes and custom backgrounds (see also: `XButton`)."""

    def __init__(self, **kwargs):
        """Initialize the class."""
        kwargs = dict(
            markup=True,
            halign="center",
            valign="center",
            background_normal=BG_NORMAL,
            background_down=BG_DOWN,
            background_disabled_normal=BG_NORMAL,
            background_disabled_down=BG_DOWN,
            border=(2, 1, 2, 1),
        ) | kwargs
        super().__init__(**kwargs)
        self.bind(disabled=self._refresh_graphics)

    def on_touch_down(self, m):
        """Overrides base class method to only react to left clicks."""
        if m.button != "left":
            return False
        return super().on_touch_down(m)

    def on_subtheme(self, subtheme):
        """Apply colors."""
        self._refresh_graphics()

    def _refresh_graphics(self, *args):
        enabled_alpha = 1 if not self.disabled else 0.5
        self.background_color = self.subtheme.bg.modified_alpha(enabled_alpha).rgba
        fg = self.subtheme.fg
        self.color = fg.rgba
        self.disabled_color = fg.modified_alpha(0.5).rgba


class XButton(XThemedButton, XWidget, kv.Button):
    """Button."""
    pass


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
    "XThemedButton",
)
