"""Home of `XDateTime`."""

import arrow
from .. import kivy as kv
from ..behaviors import XThemed
from .label import XLabel
from .layouts import XBox
from .button import XButton
from .divider import XDivider
from .input import XInput
from .spinner import XSpinner


_MONTH_NAMES = tuple(arrow.get(1, m+1, 1).format("MMMM") for m in range(12))


class XDateTime(XThemed, XBox):
    """Widget for selecting time and date.

    This widget uses the [arrow](https://arrow.readthedocs.io/en/latest/guide.html)
    library to get and set date and time.

    .. warning:: If `utc_time` is False (configured to local time), make sure to convert
        to local time when calling `XDateTime.set`.
    """

    utc_time = kv.BooleanProperty(False)
    """If time should be in UTC, otherwise as local time."""

    def __init__(self, **kwargs):
        """Initialize the class."""
        super().__init__(**kwargs)
        self.set_size(x="335sp", y="70sp")
        self.register_event_type("on_time")
        with self.app.subtheme_context(self.subtheme_name):
            self._make_widgets()

    def _make_widgets(self):
        self.day_input = XInput(input_filter="int", halign="center")
        self.month_input = XSpinner(values=_MONTH_NAMES, text_autoupdate=True)
        self.month_input.set_size(y="30sp")
        self.year_input = XInput(input_filter="int", halign="center")
        day = XBox(orientation="vertical")
        day.set_size(x="50sp")
        day.add_widgets(
            self._get_increment_button("days", 1),
            self.day_input,
            self._get_increment_button("days", -1),
        )
        month = XBox(orientation="vertical")
        month.set_size(x="85sp")
        month.add_widgets(
            self._get_increment_button("months", 1),
            self.month_input,
            self._get_increment_button("months", -1),
        )
        year = XBox(orientation="vertical")
        year.set_size(x="50sp")
        year.add_widgets(
            self._get_increment_button("years", 1),
            self.year_input,
            self._get_increment_button("years", -1),
        )
        self.hour_input = XInput(input_filter="int", halign="center")
        self.minute_input = XInput(input_filter="int", halign="center")
        self.second_input = XInput(input_filter="int", halign="center")
        hour = XBox(orientation="vertical")
        hour.set_size(x="40sp")
        hour.add_widgets(
            self._get_increment_button("hours", 1),
            self.hour_input,
            self._get_increment_button("hours", -1),
        )
        minute = XBox(orientation="vertical")
        minute.set_size(x="40sp")
        minute.add_widgets(
            self._get_increment_button("minutes", 1),
            self.minute_input,
            self._get_increment_button("minutes", -1),
        )
        second = XBox(orientation="vertical")
        second.set_size(x="40sp")
        second.add_widgets(
            self._get_increment_button("seconds", 1),
            self.second_input,
            self._get_increment_button("seconds", -1),
        )
        div0 = XDivider(orientation="vertical")
        div1 = XLabel(text=":", bold=True)
        div2 = XLabel(text=":", bold=True)
        div0.set_size(x="15sp")
        div1.set_size(x="10sp")
        div2.set_size(x="10sp")
        self.add_widgets(
            day,
            month,
            year,
            div0,
            hour,
            div1,
            minute,
            div2,
            second,
        )
        self.set(arrow.now())
        self.day_input.bind(text=self._dispatch_time)
        self.month_input.bind(text=self._dispatch_time)
        self.year_input.bind(text=self._dispatch_time)
        self.hour_input.bind(text=self._dispatch_time)
        self.minute_input.bind(text=self._dispatch_time)
        self.second_input.bind(text=self._dispatch_time)

    @property
    def time(self) -> arrow.Arrow:
        """Current time as an `arrow.Arrow` object."""
        return arrow.get(
            int(self.year_input.text or 2000),
            _MONTH_NAMES.index(self.month_input.text or _MONTH_NAMES[0]) + 1,
            int(self.day_input.text or 0),
            int(self.hour_input.text or 0),
            int(self.minute_input.text or 0),
            int(self.second_input.text or 0),
        ).replace(tzinfo="utc" if self.utc_time else "local")

    def set(self, time: arrow.Arrow, /):
        """Set the time from an `arrow.Arrow` object."""
        self.year_input.text = str(time.year)
        self.month_input.text = time.format("MMMM")
        self.day_input.text = f"{time.day:0>2}"
        self.hour_input.text = f"{time.hour:0>2}"
        self.minute_input.text = f"{time.minute:0>2}"
        self.second_input.text = f"{time.second:0>2}"
        self._dispatch_time()

    def _dispatch_time(self, *args):
        self.dispatch("on_time", self.time)

    def on_time(self, time: arrow.Arrow):
        """Called when time changes."""
        pass

    def _get_increment_button(self, name, increment):
        btn = XButton(
            text="+" if increment > 0 else "-",
            on_release=lambda *a: self._increment(name, increment),
        )
        btn.set_size(y="20sp")
        return btn

    def _increment(self, name, increment):
        self.set(self.time.shift(**{name: increment}))


__all__ = (
    "XDateTime",
)
