"""App and associated widgets.

To use the GUI, initialize and then run an `XApp`:
```python
app = XApp()
app.hook(func_to_call_every_frame, fps=20)
app.run()
```
"""
from typing import Callable, Optional
from contextlib import contextmanager
from functools import partial
from . import kivy as kv
from .colors import XColor, THEMES, Theme, reload_themes
from .util import (
    queue_around_frame,
    restart_script,
    consume_args,
    schedule_interval,
)
from .behaviors import XFocusBehavior
from .win_focus_patch import XWindowFocusPatch
from .widgets.layouts import XAnchor, XAnchorDelayed, fpwrap
from .widgets.label import XLabel


DEFAULT_THEME_NAME = "midnight"


class XOverlay(XFocusBehavior, XAnchor):
    """Overlay to be displayed on top of other widgets."""

    def __init__(self, **kwargs):
        """Initialize like an XAnchor."""
        super().__init__()
        self.make_bg(XColor(*self.app.theme.secondary.bg.rgb, 0.75))
        with self.app.subtheme_context("primary"):
            self.label = XLabel(**kwargs)
            frame = fpwrap(self.label)
            frame.set_size(x="500sp", y="150sp")
            self.add_widget(frame)


class XApp(kv.App):
    """See module documentation for details."""

    current_focus = kv.ObjectProperty(None, allownone=True)
    """Widget that currently has focus."""
    block_input = kv.BooleanProperty(False)
    """If all user input should be blocked."""

    _theme_name: str = DEFAULT_THEME_NAME
    _theme: Theme = THEMES[DEFAULT_THEME_NAME]
    _subtheme_contexts: list[str] = []
    """List of subthemes for nested context. See `XApp.subtheme`."""

    window = kv.Window
    """Kivy `Window`."""

    def __init__(self, escape_exits: bool = False, **kwargs):
        """Initialize the class."""
        self.__window_focus_path = XWindowFocusPatch()
        self.disable_multitouch()
        self.enable_escape_exit(escape_exits)
        super().__init__(**kwargs)
        self.register_event_type("on_theme")
        self.root = XAnchorDelayed()
        self.keyboard = kv.Window.request_keyboard(consume_args, None)
        self.__restart_flag = False
        self.__overlay = None
        self._overlay_container = None
        schedule_interval(self._check_focus, 0)
        kv.Window.bind(
            on_touch_down=self._filter_touch,
            on_touch_up=self._filter_touch,
            on_touch_move=self._filter_touch,
        )

    @property
    def theme_name(self) -> str:
        """Current theme name."""
        return self._theme_name

    @property
    def theme(self) -> Theme:
        """Current `kvex.colors.Theme` object."""
        return self._theme

    def set_theme(self, theme_name: str, /):
        """Set the theme by name."""
        self._theme_name = theme_name
        self._theme = THEMES[theme_name]
        self.dispatch("on_theme", self._theme)

    def on_theme(self, theme: Theme):
        """Called when the theme has been set."""
        pass

    def reload_themes(self, *args):
        """Reload themes from disk.

        Some widgets may require manual refreshing to take effect.
        """
        reload_themes()
        self.set_theme(self.theme_name)

    @property
    def subtheme_name(self) -> str:
        """Current subtheme name, based on context from `XApp.subtheme_context`."""
        if not self._subtheme_contexts:
            return "primary"
        return self._subtheme_contexts[-1]

    @contextmanager
    def subtheme_context(self, subtheme: Optional[str]):
        """Context manager for setting the subtheme.

        While in context, all `kvex.behaviors.XThemed` widgets will default to this
        subtheme. Subtheme contexts can be nested. For example:

        ```python
        with app.subtheme_context("secondary"):
            XLabel(text="Secondary")
            with app.subtheme_context("primary"):
                XLabel(text="Primary")
                with app.subtheme_context("accent"):
                    XLabel(text="Accent")
            XLabel(text="Secondary")
        ```
        """
        if subtheme:
            context_index = len(self._subtheme_contexts)
            self._subtheme_contexts.append(subtheme)
        try:
            yield
        finally:
            if subtheme:
                # Remove our context and all further nested contexts from list
                self._subtheme_contexts = self._subtheme_contexts[:context_index]

    def _check_focus(self, *args):
        self.current_focus = self.keyboard.target

    def run(self, *args, allow_restart: bool = True, **kwargs) -> int:
        """Run asyncronously.

        The allow_restart argument determines what happens after using
        `XApp.restart`. Will restart immediately if true, otherwise will
        return -1. All other arguments are passed to the base method.

        Returns 0 in all other cases.
        """
        super().run(*args, **kwargs)
        if allow_restart and self.__restart_flag:
            restart_script()
        return -1 if self.__restart_flag else 0

    async def async_run(self, *args, allow_restart: bool = True, **kwargs) -> int:
        """Run asyncronously. Arguments like `XApp.run`."""
        await super().async_run(*args, **kwargs)
        if allow_restart and self.__restart_flag:
            restart_script()
        return -1 if self.__restart_flag else 0

    def restart(self, *args):
        """Restart the app by stopping `XApp.run` and returning -1."""
        self.__restart_flag = True
        self.stop()

    def hook(self, func: Callable[[float], None], fps: float):
        """Schedule *func* to be called *fps* times per seconds."""
        kv.Clock.schedule_once(lambda *a: kv.Clock.schedule_interval(func, 1 / fps))

    def add_widget(self, *args, **kwargs):
        """Add a widget to the root widget."""
        return self.root.add_widget(*args, **kwargs)

    @property
    def mouse_pos(self) -> tuple[float, float]:
        """The current position of the mouse."""
        return kv.Window.mouse_pos

    @staticmethod
    def maximize(*args):
        """Maixmize the window."""
        kv.Window.maximize()

    @staticmethod
    def set_size(x: float, y: float):
        """Resize the window while maintaining it's center position."""
        oldx, oldy = kv.Window.size
        top, left = kv.Window.top, kv.Window.left
        bot, right = top + oldy, left + oldx
        center = ((top + bot) / 2, (left + right) / 2)
        center_offset = (y / 2, x / 2)
        new_top_left = (
            int(center[0] - center_offset[0]),
            int(center[1] - center_offset[1]),
        )
        kv.Window.size = x, y
        kv.Window.top, kv.Window.left = new_top_left

    @staticmethod
    def toggle_fullscreen(set_to: Optional[bool] = None):
        """Toggle window fullscreen."""
        set_to = not kv.Window.fullscreen if set_to is None else set_to
        kv.Window.fullscreen = set_to

    @staticmethod
    def toggle_borderless(set_to: Optional[bool] = None):
        """Toggle window border."""
        set_to = not kv.Window.borderless if set_to is None else set_to
        kv.Window.borderless = set_to

    @staticmethod
    def set_position(x: float, y: float):
        """Reposition the window's top left position."""
        kv.Window.left, kv.Window.top = x, y

    @staticmethod
    def enable_escape_exit(set_to: bool = True):
        """Toggles using the escape key to exit the program."""
        kv.Config.set("kivy", "exit_on_escape", str(int(set_to)))

    @staticmethod
    def disable_multitouch():
        """Toggles multitouch."""
        kv.Config.set("input", "mouse", "mouse,disable_multitouch")

    @staticmethod
    def enable_resize(set_to: bool):
        """Toggles ability to resize the window."""
        kv.Config.set("graphics", "resizable", str(int(set_to)))

    def open_settings(self, *args) -> False:
        """Overrides base class method to disable the builtin settings widget."""
        return False

    @property
    def overlay(self) -> Optional[XOverlay]:
        """The current overlay."""
        return self.__overlay

    def with_overlay(
        self,
        func: Callable,
        after: Optional[Callable] = None,
        **kwargs,
    ):
        """Queue a function with a temporary `XOverlay` that blocks input.

        Uses the `kvex.util.queue_around_frame` decorator to draw a frame before
        calling the function, otherwise the added overlay will not be seen
        until execution is yielded to kivy's clock.

        Example usage:
        ```python
        xapp.with_overlay(
            func=lambda: my_func(arg1=True),
            text="my_func is executing...",
            after=lambda: print("finished executing my_func."),
        )
        ```

        Args:
            func: Callback to queue after adding the overlay.
            after: Optionally call after removing the overlay.
            kwargs: Keyword arguments for the XOverlay object.
        """
        if self.__overlay is not None:
            raise RuntimeError("Cannot create an overlay when one already exists.")
        delay = self.root.layout_event_delay
        self.root.layout_event_delay = 0
        queue_around_frame(
            func,
            before=partial(self.__create_overlay, **kwargs),
            after=partial(self.__destroy_overlay, after, delay),
            delay=0.05,
        )()

    def _filter_touch(self, w, touch):
        if self.block_input:
            return True
        if "button" not in touch.profile:
            return True
        return False

    def __create_overlay(self, **kwargs):
        self.__overlay = XOverlay(**kwargs)
        self.__overlay.focus = True
        self.block_input = True
        self.root.add_widget(self.__overlay)

    def __destroy_overlay(self, after: Optional[Callable], delay: float):
        self.root.remove_widget(self.__overlay)
        self.__overlay = None
        self.block_input = False
        if after is not None:
            after()
        self.root.layout_event_delay = delay


__all__ = (
    "XApp",
)
