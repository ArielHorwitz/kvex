"""Home of `XDateTime`."""

import arrow
from .. import kivy as kv
from ..behaviors import XThemed
from .label import XLabel
from .layouts import XBox, XDynamic, XJustify
from .button import XButton
from .divider import XDivider
from .input import XInput
from .spinner import XSpinner


_MONTH_NAMES = tuple(arrow.get(1, m+1, 1).format("MMMM") for m in range(12))


class XDateTime(XThemed, XDynamic):
    """Widget for selecting time and date.

    This widget uses the [arrow](https://arrow.readthedocs.io/en/latest/guide.html)
    library to get and set date and time.

    To use simply get and set `XDateTime.time`:
    ```python3
    datetime = XDateTime()
    print(datetime.time)
    datetime.bind(on_time=print)
    datetime.time = arrow.now()
    ```

    .. warning::
        If `utc_time` is False (configured to local time), make sure to convert to local
        time when setting the time. See the arrow library for documentation.
    """

    utc_time = kv.BooleanProperty(False)
    """If time should be in UTC, otherwise as local time. False by default."""
    date_first = kv.BooleanProperty(False)
    """Show date before time. False by default."""

    def __init__(self, **kwargs):
        """Initialize the class."""
        kwargs = dict(orientation="horizontal", both_axes=True) | kwargs
        super().__init__(**kwargs)
        self.register_event_type("on_time")
        with self.app.subtheme_context(self.subtheme_name):
            self._make_widgets()

    def _make_widgets(self):
        # Date
        self.day_input = XInput(input_filter="int", halign="center")
        self.month_input = XSpinner(
            values=_MONTH_NAMES,
            text_autoupdate=True,
            ssy="30sp",
        )
        self.year_input = XInput(input_filter="int", halign="center")
        day = XBox(orientation="vertical", ssx="50sp")
        day.add_widgets(
            self._get_increment_button("days", 1),
            self.day_input,
            self._get_increment_button("days", -1),
        )
        month = XBox(orientation="vertical", ssx="85sp")
        month.add_widgets(
            self._get_increment_button("months", 1),
            self.month_input,
            self._get_increment_button("months", -1),
        )
        year = XBox(orientation="vertical", ssx="50sp")
        year.add_widgets(
            self._get_increment_button("years", 1),
            self.year_input,
            self._get_increment_button("years", -1),
        )
        self._date_box = XDynamic(orientation="horizontal", ssy="70sp")
        self._date_box.add_widgets(day, month, year)
        # Time
        self.hour_input = XInput(input_filter="int", halign="center")
        self.minute_input = XInput(input_filter="int", halign="center")
        self.second_input = XInput(input_filter="int", halign="center")
        hour = XBox(orientation="vertical", ssx="40sp")
        hour.add_widgets(
            self._get_increment_button("hours", 1),
            self.hour_input,
            self._get_increment_button("hours", -1),
        )
        minute = XBox(orientation="vertical", ssx="40sp")
        minute.add_widgets(
            self._get_increment_button("minutes", 1),
            self.minute_input,
            self._get_increment_button("minutes", -1),
        )
        second = XBox(orientation="vertical", ssx="40sp")
        second.add_widgets(
            self._get_increment_button("seconds", 1),
            self.second_input,
            self._get_increment_button("seconds", -1),
        )
        self._time_box = XDynamic(orientation="horizontal", ssy="70sp")
        self._time_box.add_widgets(
            hour,
            XLabel(text=":", bold=True, ssx="10sp"),
            minute,
            XLabel(text=":", bold=True, ssx="10sp"),
            second,
        )
        # Assemble
        self._time_justify = XJustify(orientation="horizontal")
        self._main_divider = XDivider()
        self._refresh_geometry()
        self.time = arrow.get(0)
        # Events
        self.bind(orientation=self._refresh_geometry, date_first=self._refresh_geometry)
        self.day_input.bind(text=self._dispatch_time)
        self.month_input.bind(text=self._dispatch_time)
        self.year_input.bind(text=self._dispatch_time)
        self.hour_input.bind(text=self._dispatch_time)
        self.minute_input.bind(text=self._dispatch_time)
        self.second_input.bind(text=self._dispatch_time)

    def _refresh_geometry(self, *args):
        self.clear_widgets()
        self._time_justify.clear_widgets()
        # Orientation
        if self.orientation == "horizontal":
            time_box = self._time_box
            self._main_divider.orientation = "vertical"
        elif self.orientation == "vertical":
            time_box = self._time_justify
            self._time_justify.add_widget(self._time_box)
            self._main_divider.orientation = "horizontal"
        # Reassemble
        if self.date_first:
            self.add_widgets(self._date_box, self._main_divider, time_box)
        else:
            self.add_widgets(time_box, self._main_divider, self._date_box)

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

    @time.setter
    def time(self, time: arrow.Arrow, /):
        """Set current time from an `arrow.Arrow` object."""
        self._do_set_time(time)

    def _do_set_time(self, time: arrow.Arrow, /):
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
            ssy="20sp",
        )
        return btn

    def _increment(self, name, increment):
        self._do_set_time(self.time.shift(**{name: increment}))


__all__ = (
    "XDateTime",
)
