"""Home of `ScreenManager` and `XScreen`."""

from typing import Literal
from .. import kivy as kv
from .widget import XWidget


class XScreen(XWidget, kv.Screen):
    """Screen."""


class XScreenManager(XWidget, kv.ScreenManager):
    """ScreenManager with custom transition behavior."""

    def add_screen(self, name: str, widget: kv.Widget) -> XScreen:
        """Create and add a screen from a widget."""
        screen = XScreen(name=name)
        screen.add_widget(widget)
        self.add_widget(screen)
        return screen

    def screen_direction(self, name: str, /) -> Literal["left", "right"]:
        """Compare index of a screen by name to the current screen.

        Useful for setting transition direction:
        ```python3
        sm = XScreenManager()
        sm.transition.direction = sm.screen_direction("screen_name")
        sm.current = "screen_name"
        ```
        """
        old_index = self.screen_names.index(self.current)
        new_index = self.screen_names.index(name)
        return "left" if old_index < new_index else "right"

    @property
    def mid_transition(self) -> bool:
        """If there is a transition in progress."""
        return 0 < self.current_screen.transition_progress < 1

    @classmethod
    def from_widgets(cls, widgets: dict[str, XWidget], **kwargs) -> "XScreenManager":
        """Create an XScreenManager from a dictionary of screen names and widgets."""
        sm = cls(**kwargs)
        for n, w in widgets.items():
            screen = XScreen(name=n)
            screen.add_widget(w)
            sm.add_widget(screen)
        return sm


__all__ = (
    "XScreenManager",
    "XScreen",
)
