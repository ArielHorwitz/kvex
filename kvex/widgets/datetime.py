"""Home of `XDateTime`."""

import arrow
from .. import kivy as kv
from .. import util
from ..behaviors import XThemed
from .label import XLabel, XLabelClick
from .layouts import XBox, XGrid, XDynamic, XJustify
from .button import XButton
from .divider import XDivider
from .dropdown import XDropDown
from .input import XInputNumber
from .spinner import XSpinner


_MONTH_NAMES = tuple(arrow.get(1, m+1, 1).format("MMMM") for m in range(12))
_LAST_MONTH_DAY = {
    name: arrow.get(1, m+1, 1).ceil("month").day
    for m, name in enumerate(_MONTH_NAMES)
}


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

    _time = kv.ObjectProperty(arrow.now())

    def _get_time(self) -> arrow.Arrow:
        return self._time

    def _set_time(self, time: arrow.Arrow, /):
        """Set current time from an `arrow.Arrow` object."""
        self.year_input.text = str(time.year)
        self.month_input.text = time.format("MMMM")
        self.day_input.text = f"{time.day:0>2}"
        self.hour_input.text = f"{time.hour:0>2}"
        self.minute_input.text = f"{time.minute:0>2}"
        self.second_input.text = f"{time.second:0>2}"

    time = kv.AliasProperty(_get_time, _set_time, bind=["_time"])
    """Current time as an `arrow.Arrow` object."""
    utc_time = kv.BooleanProperty(False)
    """If time should be in UTC, otherwise as local time. Defaults to False."""
    date_first = kv.BooleanProperty(False)
    """Show date before time. Defaults to False."""

    def __init__(self, **kwargs):
        """Initialize the class."""
        kwargs = dict(orientation="horizontal", both_axes=True) | kwargs
        time = kwargs.pop("time", None)
        super().__init__(**kwargs)
        self._last_time = self._time
        self._update_trigger = util.create_trigger(self._update_time)
        with self.app.subtheme_context(self.subtheme_name):
            self._make_widgets()
        self._start_events()
        self._set_time(time or self._time)
        self._update_time()

    def _trigger_update(self, *args):
        util.snooze_trigger(self._update_trigger)

    def _update_time(self, *args):
        self._fix_month()
        time = arrow.get(
            self.year_input.number_value,
            _MONTH_NAMES.index(self.month_input.text) + 1,
            int(self.day_input.text),
            self.hour_input.number_value,
            self.minute_input.number_value,
            self.second_input.number_value,
        ).replace(tzinfo="utc" if self.utc_time else "local")
        if time.timestamp() != self._last_time.timestamp():
            self._last_time = time
            self._time = time

    def _fix_month(self):
        month_name = self.month_input.text
        last_day = _LAST_MONTH_DAY[month_name] + 1
        if int(self.day_input.text) > last_day:
            self.day_input.text = str(last_day)
        month_index = _MONTH_NAMES.index(month_name) + 1
        self._day_selector.set_month(self.year_input.number_value, month_index)

    def _make_widgets(self):
        # Date
        self._day_selector = _DaySelector(self._day_dropdown_callback)
        self._day_dropdown = XDropDown(
            auto_width=False,
            bg_alpha=1,
            ssx=self._day_selector.width,
        )
        self._day_dropdown.add_widget(self._day_selector)
        self.day_input = XButton(
            text="1",
            halign="center",
            on_release=self._day_dropdown_open,
        )
        self.month_input = XSpinner(
            text=_MONTH_NAMES[0],
            values=_MONTH_NAMES,
            text_autoupdate=True,
            ssy="30sp",
        )
        self.year_input = XInputNumber(
            input_filter="int",
            min_value=2,
            max_value=5000,
            default_valid=2000,
            disable_invalid=False,
            halign="center",
        )
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
        self.hour_input = XInputNumber(
            text="00",
            input_filter="int",
            min_value=0,
            max_value=23,
            disable_invalid=True,
            halign="center",
        )
        self.minute_input = XInputNumber(
            text="00",
            input_filter="int",
            min_value=0,
            max_value=59,
            disable_invalid=True,
            halign="center",
        )
        self.second_input = XInputNumber(
            text="00",
            input_filter="int",
            min_value=0,
            max_value=59,
            disable_invalid=True,
            halign="center",
        )
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
        self._main_divider = XDivider(thickness="2dp", hint=0.5)
        self._refresh_geometry()

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

    def _start_events(self):
        self.bind(orientation=self._refresh_geometry, date_first=self._refresh_geometry)
        self.day_input.bind(text=self._trigger_update)
        self.month_input.bind(text=self._trigger_update)
        self.year_input.bind(number_value=self._trigger_update)
        self.hour_input.bind(number_value=self._trigger_update)
        self.minute_input.bind(number_value=self._trigger_update)
        self.second_input.bind(number_value=self._trigger_update)

    def _day_dropdown_open(self, *args):
        self._day_dropdown.open(self.day_input)

    def _day_dropdown_callback(self, day: int):
        self.day_input.text = str(day)
        self._day_dropdown.dismiss()

    def _get_increment_button(self, name, increment):
        btn = XButton(
            text="+" if increment > 0 else "-",
            on_release=lambda *a: self._increment(name, increment),
            ssy="20sp",
        )
        return btn

    def _increment(self, name, increment):
        self._set_time(self.time.shift(**{name: increment}))


class _DaySelector(XGrid):

    WIDTH = util.sp2pixels("35sp") * 7
    LABELS = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]

    def __init__(self, callback):
        """Initialize the class."""
        super().__init__(cols=7, ssx=self.WIDTH)
        self._callback = callback
        self._last_month = (0, 0)
        self._labels = tuple(XLabel(text=self.LABELS[i], bold=True) for i in range(7))
        self._days = tuple(self._get_label(day) for day in range(31))

    def set_month(self, year: int, month: int):
        if self._last_month == (year, month):
            return
        self._last_month = (year, month)
        time = arrow.get(year, month, 1)
        first, last = time.span("month")
        start = first.weekday() + 1
        # Adjust for monday being "first" day of the week
        if start == 7:
            start = 0
        end_fill = 42 - last.day - start
        end_fill %= 7
        self.clear_widgets()
        self.add_widgets(*self._labels)
        if start:
            self.add_widgets(*(kv.Widget() for i in range(start)))
        self.add_widgets(*self._days[:last.day])
        if end_fill:
            self.add_widgets(*(kv.Widget() for i in range(end_fill)))
        row_count = len(self.children) // 7
        self.set_size(y=row_count * util.sp2pixels("40sp"))

    def _get_label(self, day: int):
        return XLabelClick(text=str(day + 1), on_release=self._on_select)

    def _on_select(self, w):
        self._callback(int(w.text))


__all__ = (
    "XDateTime",
)
