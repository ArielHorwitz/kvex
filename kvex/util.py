"""Kvex utilities."""

from typing import Optional, Any, Callable, Iterable
from functools import partial, wraps
import os
import sys
from . import kivy as kv


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


def sp2pixels(value: float | str | Iterable[float | str]) -> float | list[float]:
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
    "snooze_trigger",
    "queue_around_frame",
    "sp2pixels",
)
