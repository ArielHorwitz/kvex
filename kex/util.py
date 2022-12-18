"""Kex utilities."""

from typing import Optional, Literal, Any, Callable
from functools import partial, wraps
import os
import sys
import random
from . import kivy as kv


COLORS = {
    "black": (0.0, 0.0, 0.0),
    "grey": (0.5, 0.5, 0.5),
    "white": (1.0, 1.0, 1.0),
    "red": (0.6, 0.0, 0.1),
    "pink": (0.9, 0.3, 0.4),
    "yellow": (0.8, 0.7, 0.1),
    "orange": (0.7, 0.4, 0.0),
    "lime": (0.1, 0.4, 0.0),
    "green": (0.4, 0.7, 0.1),
    "cyan": (0.1, 0.7, 0.7),
    "blue": (0.1, 0.4, 0.9),
    "navy": (0.0, 0.1, 0.5),
    "violet": (0.7, 0.1, 0.9),
    "purple": (0.4, 0.0, 0.7),
    "magenta": (0.7, 0.0, 0.5),
}
ColorName = Literal[
    "black",
    "grey",
    "white",
    "red",
    "pink",
    "yellow",
    "orange",
    "lime",
    "green",
    "cyan",
    "blue",
    "navy",
    "violet",
    "purple",
    "magenta",
]
ColorType = tuple[float, float, float, float]


class XColor:
    """A class to represent a color."""

    def __init__(
        self,
        r: float = 1,
        g: float = 1,
        b: float = 1,
        a: float = 1,
        *,
        v: float = 1,
    ):
        """Initialize the class.

        Args:
            r: Red component.
            g: Green component.
            b: Blue component.
            a: Alpha component.
            v: Value multiplier (multiplies `rgb` values).
        """
        r, g, b = r * v, g * v, b * v
        self.__rgba = r, g, b, a

    @classmethod
    def from_name(cls, name: ColorName, /, *, a: float = 1, v: float = 1) -> "XColor":
        """Return a `XColor` from color name."""
        color = [c * v for c in COLORS[name]]
        return cls(*color, a)

    @classmethod
    def from_random(cls, *, a: float = 1, v: float = 1) -> "XColor":
        """Get a new `XColor` with random values."""
        color = tuple(random.random() * v for _ in range(3))
        return cls(*color, a)

    def alternate_color(self, *, drift: float = 0.5) -> "XColor":
        """Return a color that is offset from self by *drift* amount."""
        alt_rgb = [(c + drift) % 1 for c in self.rgb]
        return self.__class__(*alt_rgb, self.a)

    @property
    def r(self) -> float:
        """The red component."""
        return self.__rgba[0]

    @property
    def g(self) -> float:
        """The green component."""
        return self.__rgba[1]

    @property
    def b(self) -> float:
        """The blue component."""
        return self.__rgba[2]

    @property
    def a(self) -> float:
        """The alpha component."""
        return self.__rgba[3]

    @property
    def rgb(self) -> tuple[float, float, float]:
        """The red, green, and blue components."""
        return self.__rgba[:3]

    @property
    def rgba(self) -> ColorType:
        """The red, green, blue, and alpha components."""
        return self.__rgba


get_color = XColor.from_name
random_color = XColor.from_random


def queue_around_frame(
    func,
    before: Optional[Callable] = None,
    after: Optional[Callable] = None,
):
    """Decorator for queuing functions before and after drawing frames.

    Used for performing GUI operations before and after functions that will
    block code execution for a significant period of time. Functions that would
    otherwise freeze the GUI without feedback can be wrapped with this decorator
    to give user feedback.

    The following order of operations will be queued:

    1. Call *before*
    2. Draw GUI frame
    3. Call the wrapped function
    4. Call *after*

    ### Example usage:
    ```python
    @queue(
        before=lambda: print("Drawing GUI frame then executing function..."),
        after=lambda: print("Done executing..."),
    )
    def do_sleep():
        time.sleep(2)
    ```
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if before is not None:
            before()
        wrapped = partial(func, *args, **kwargs)
        kv.Clock.schedule_once(lambda dt: _call_with_after(wrapped, after), 0.05)

    return wrapper


def _call_with_after(func: Callable, after: Optional[Callable] = None):
    func()
    if after is not None:
        # In order to schedule properly, we must tick or else all the time spent
        # calling func will be counted as time waited on kivy's clock schedule.
        kv.Clock.tick()
        kv.Clock.schedule_once(lambda dt: after(), 0.05)


def center_sprite(
    pos: tuple[float, float],
    size: tuple[float, float],
) -> tuple[int, int]:
    """Given *size* and center position *pos*, return the bottom left corner."""
    assert len(pos) == 2 and len(size) == 2
    return int(pos[0] - (size[0] / 2)), int(pos[1] - (size[1] / 2))


def text_texture(text, **kwargs):
    """Create a label texture using kivy.core.Label."""
    label = kv.CoreLabel(text=text, **kwargs)
    label.refresh()
    return label.texture


def from_atlas(name: str, /) -> str:
    return f"atlas://data/images/defaulttheme/{name}"


def restart_script(*args, **kwargs):
    """Restart the Python script. Ignores all arguments."""
    os.execl(sys.executable, sys.executable, *sys.argv)


def consume_args(*args, **kwargs):
    """Empty function that will consume all arguments passed to it."""
    pass


def placeholder(
    *wrapper_args,
    verbose: bool = False,
    returns: Any = None,
    **wrapper_kwargs,
) -> Callable:
    """Create a placeholder function that can consume all arguments passed to it."""

    def placeholder_inner(*args, **kwargs):
        print(
            f"Placeholder function {wrapper_args}{wrapper_kwargs} : "
            f"{args}{kwargs} -> {returns=}"
        )
        return returns

    return placeholder_inner


class SnoozingTrigger:
    def __init__(self, *args, **kwargs):
        self.ev = kv.Clock.create_trigger(*args, **kwargs)

    def __call__(self, *args):
        if self.ev.is_triggered:
            self.ev.cancel()
        self.ev()


schedule_once = kv.Clock.schedule_once
schedule_interval = kv.Clock.schedule_interval
create_trigger = kv.Clock.create_trigger
snoozing_trigger = SnoozingTrigger
