"""Kvex utilities."""

from typing import Any, Callable, Iterable
from functools import partial
import os
import sys
from . import kivy as kv


DEFAULT_SPACING = "10dp"
DEFAULT_BUTTON_HEIGHT = "30sp"
_KIVY_DIMENSIONS = float | tuple[float, float] | str | tuple[str, str]


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
    """Get a path to a sprite name from the `defaulttheme` atlas."""
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
    """Create a function That consumes all arguments and prints them."""

    def placeholder_inner(*args, **kwargs):
        print(
            f"Placeholder function {wrapper_args}{wrapper_kwargs} : "
            f"{args}{kwargs} -> {returns=}"
        )
        return returns

    return placeholder_inner


create_trigger = kv.Clock.create_trigger
schedule_once = kv.Clock.schedule_once
schedule_interval = kv.Clock.schedule_interval


def schedule_many(
    sequence: Iterable[Callable | float],
    call_with: Any = None,
):
    """Schedule a list of functions with a delay between each.

    Useful for loading screens and allowing a frame to be drawn between each function:
    ```python3
    # In `XApp.on_start`:
    loading_sequence = [
        lambda: setattr(label, "text", "Loading part 1..."),
        0.1,  # Allow text to draw before execution block
        lambda: time.sleep(2),  # Expensive blocking call
        lambda: setattr(label, "text", "Loading part 2..."),
        0.1,  # Allow text to draw before execution block
        lambda: time.sleep(2),  # Expensive blocking call
        lambda: setattr(label, "text", "Done loading."),
    ]
    kx.schedule_many(loading_sequence)
    ```

    See also `kvex.example.ExampleApp.on_start` to see a more practical example.

    Args:
        sequence: Iterable of functions to call and floats of delay time in seconds.
        call_with: If given, this object will be passed as the argument for each
            function call.
    """
    sequence_list = list(sequence)
    assert len(sequence_list) > 0
    call = partial(_schedule_many, sequence_list, call_with)
    schedule_once(call, -1)


def _schedule_many(sequence_list: list[Callable | float], call_with: Any, dt: float):
    delay = -1
    next_action = sequence_list.pop(0)
    if callable(next_action):
        if call_with is None:
            next_action()
        else:
            next_action(call_with)
    else:
        delay = next_action
    if sequence_list:
        next_call = partial(_schedule_many, sequence_list, call_with)
        schedule_once(next_call, delay)


def snooze_trigger(ev: "kivy.clock.ClockEvent"):  # noqa: F821
    """Cancel and reschedule a ClockEvent."""
    if ev.is_triggered:
        ev.cancel()
    ev()


_metrics_dp = kv.metrics.dp
_metrics_sp = kv.metrics.sp


def _str2pixels(s) -> float:
    vstr = str(s)
    if vstr.endswith("dp"):
        return _metrics_dp(vstr[:-2])
    if vstr.endswith("sp"):
        return _metrics_sp(vstr[:-2])
    raise ValueError(f"Unkown format: {s!r} (please use 'dp' or 'sp')")


def to_pixels(value: float | str | Iterable[float | str]) -> float | list[float]:
    """Convert values in 'sp', 'dp', or pixels to pixels.

    Useful when wishing to convert values to pixels but it is unknown if they are given
    in pixels or 'sp' format.
    """
    if isinstance(value, int) or isinstance(value, float):
        return value
    if isinstance(value, str):
        return _str2pixels(value)
    # Handle as iterable
    values = []
    append = values.append
    for v in value:
        if isinstance(v, int) or isinstance(v, float):
            append(v)
        elif isinstance(v, str):
            append(_str2pixels(v))
        else:
            m = f"Expected float or str, instead got: {v!r} {type(v)}"
            raise ValueError(m)
    return values


def _extend_dimensions(d: _KIVY_DIMENSIONS) -> _KIVY_DIMENSIONS:
    if not isinstance(d, str):
        try:
            return tuple(c for c in d)
        except TypeError:
            pass
    return d, d


__all__ = (
    "center_sprite",
    "text_texture",
    "from_atlas",
    "restart_script",
    "placeholder",
    "consume_args",
    "create_trigger",
    "schedule_once",
    "schedule_interval",
    "schedule_many",
    "snooze_trigger",
    "to_pixels",
    "DEFAULT_SPACING",
    "DEFAULT_BUTTON_HEIGHT",
)
