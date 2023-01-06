"""Home of `ScreenManager` and `XScreen`."""

from .. import kivy as kv
from .widget import XWidget


class XScreen(XWidget, kv.Screen):
    """Screen that can only contain one widget."""

    def __init__(self, **kwargs):
        """Same arguments as Screen."""
        super().__init__(**kwargs)
        self.view = None
        """Widget of the screen."""

    def add_widget(self, w, *args, **kwargs):
        """Overrides base method to set the view."""
        self.view = w
        super().add_widget(w, *args, **kwargs)
        if len(self.children) > 1:
            raise RuntimeError(
                f"Cannot add more than 1 widget to XScreen: {self.children=}"
            )


class XScreenManager(XWidget, kv.ScreenManager):
    """ScreenManager with custom transition behavior."""

    transition_speed = kv.NumericProperty(0.4)
    """Speed of transitions in seconds."""

    def __init__(self, **kwargs):
        """Same arguments as for ScreenManager, minus transition."""
        if "transition" in kwargs:
            del kwargs["transition"]
        super().__init__(**kwargs)
        self.transition = kv.SlideTransition(
            direction="left",
            duration=self.transition_speed,
        )
        """Transition object."""

    def add_screen(self, name: str, widget: kv.Widget) -> XScreen:
        """Create and add a screen from a widget."""
        screen = self.add_widget(XScreen(name=name))
        screen.add_widget(widget)
        return screen

    def switch_name(self, name: str) -> bool:
        """Switch to a screen by name."""
        if name == self.current:
            return True
        if self.mid_transition:
            return False
        if name not in self.screen_names:
            raise ValueError(f'Found no screen by name "{name}" in {self.screen_names}')
        old_index = self.screen_names.index(self.current)
        new_index = self.screen_names.index(name)
        dir = "left" if old_index < new_index else "right"
        self.transition = kv.SlideTransition(
            direction=dir,
            duration=self.transition_speed,
        )
        self.current = name
        return True

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
