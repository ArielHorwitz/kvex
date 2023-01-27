"""Home of `XDateTime`."""

import arrow
from .. import kivy as kv
from .. import util
from ..behaviors import XThemed
from .label import XLabel, XLabelClick
from .layouts import XBox, XGrid, XDynamicBox, XJustify, XCurtain
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


class XDateTime(XThemed, XDynamicBox):
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
    show_hours = kv.BooleanProperty(True)
    """Show hour. Defaults to True."""
    show_minutes = kv.BooleanProperty(True)
    """Show minute. Defaults to True."""
    show_seconds = kv.BooleanProperty(True)
    """Show second. Defaults to True."""
    show_days = kv.BooleanProperty(True)
    """Show day. Defaults to True."""
    show_months = kv.BooleanProperty(True)
    """Show month. Defaults to True."""
    show_years = kv.BooleanProperty(True)
    """Show year. Defaults to True."""
    increment_years = kv.NumericProperty(1)
    """Default years increment."""
    increment_months = kv.NumericProperty(1)
    """Default months increment."""
    increment_days = kv.NumericProperty(1)
    """Default days increment."""
    increment_hours = kv.NumericProperty(1)
    """Default hours increment."""
    increment_minutes = kv.NumericProperty(1)
    """Default minutes increment."""
    increment_seconds = kv.NumericProperty(1)
    """Default seconds increment."""

    def __init__(self, **kwargs):
        """Initialize the class."""
        kwargs = dict(orientation="horizontal", both_axes=True) | kwargs
        time = kwargs.pop("time", None)
        super().__init__(**kwargs)
        self._last_time = self._time
        self._update_trigger = util.create_trigger(self._update_time, -1)
        with self.app.subtheme_context(self.subtheme_name):
            self._make_widgets()
        self._set_time(time or self._time)
        self._update_time()
        self._start_events()

    def _trigger_update(self, *args):
        util.snooze_trigger(self._update_trigger)

    def _update_time(self, *args):
        if not all((
            self.year_input.valid,
            self.hour_input.valid,
            self.minute_input.valid,
            self.second_input.valid,
        )):
            return
        self._fix_month()
        time = arrow.get(
            self.year_input.number,
            _MONTH_NAMES.index(self.month_input.text) + 1,
            int(self.day_input.text),
            self.hour_input.number,
            self.minute_input.number,
            self.second_input.number,
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
        self._day_selector.set_month(self.year_input.number, month_index)

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
            halign="center",
            ssy="30sp",
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
        self._day_curtain = XCurtain(dynamic=True, content=day)
        self._month_curtain = XCurtain(dynamic=True, content=month)
        self._year_curtain = XCurtain(dynamic=True, content=year)
        self._date_box = XDynamicBox(orientation="horizontal", ssy="70sp")
        self._date_box.add_widgets(
            self._day_curtain,
            self._month_curtain,
            self._year_curtain,
        )
        # Time
        self.hour_input = XInputNumber(
            text="00",
            input_filter="int",
            min_value=0,
            max_value=23,
            halign="center",
            ssy="30sp",
        )
        self.minute_input = XInputNumber(
            text="00",
            input_filter="int",
            min_value=0,
            max_value=59,
            halign="center",
            ssy="30sp",
        )
        self.second_input = XInputNumber(
            text="00",
            input_filter="int",
            min_value=0,
            max_value=59,
            halign="center",
            ssy="30sp",
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
        self._hour_curtain = XCurtain(dynamic=True, content=hour)
        minute_content = XDynamicBox(ssx="50sp", ssy="70sp")
        minute_content.add_widgets(
            XLabel(text=":", bold=True, ssx="10sp"),
            minute,
        )
        second_content = XDynamicBox(ssx="50sp", ssy="70sp")
        second_content.add_widgets(
            XLabel(text=":", bold=True, ssx="10sp", ssy="70sp"),
            second,
        )
        self._minute_curtain = XCurtain(dynamic=True, content=minute_content)
        self._second_curtain = XCurtain(dynamic=True, content=second_content)
        self._time_box = XDynamicBox(orientation="horizontal", ssy="70sp")
        self._time_box.add_widgets(
            self._hour_curtain,
            self._minute_curtain,
            self._second_curtain,
        )
        # Assemble
        self._time_justify = XJustify(orientation="horizontal")
        self._main_divider = XDivider(thickness="2dp", hint=0.5)
        self._refresh_geometry()
        self._update_curtains()

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
        self.year_input.bind(number=self._trigger_update)
        self.hour_input.bind(number=self._trigger_update)
        self.minute_input.bind(number=self._trigger_update)
        self.second_input.bind(number=self._trigger_update)
        self.bind(
            show_hours=self._update_curtains,
            show_minutes=self._update_curtains,
            show_seconds=self._update_curtains,
            show_days=self._update_curtains,
            show_months=self._update_curtains,
            show_years=self._update_curtains,
        )

    def _update_curtains(self, *args):
        self._hour_curtain.showing = self.show_hours
        self._minute_curtain.showing = self.show_minutes
        self._second_curtain.showing = self.show_seconds
        self._day_curtain.showing = self.show_days
        self._month_curtain.showing = self.show_months
        self._year_curtain.showing = self.show_years

    def _day_dropdown_open(self, *args):
        self._day_dropdown.open(self.day_input)

    def _day_dropdown_callback(self, day: int):
        self.day_input.text = str(day)
        self._day_dropdown.dismiss()

    def _get_increment_button(self, name, increment):
        d = {name: increment}
        btn = XButton(
            text="+" if increment > 0 else "-",
            on_release=lambda *a: self.increment(**d),
            ssy="20sp",
        )
        return btn

    def increment(self, **increments: dict[str, int]):
        time = self.time
        for name, inc in increments.items():
            increment = getattr(self, f"increment_{name}") * inc
            time = time.shift(**{name: increment})
        self._set_time(time)

    def on_touch_down(self, touch):
        tpos = touch.pos
        if not self.collide_point(*tpos):
            return False
        if touch.button == "right":
            self.reset_time()
            return True
        elif touch.button == "scrollup":
            inc = -1
        elif touch.button == "scrolldown":
            inc = 1
        else:
            return super().on_touch_down(touch)
        return self._on_touch_scroll(tpos, inc)

    def _on_touch_scroll(self, tpos, inc):
        if self.year_input.collide_point(*tpos):
            self.increment(years=inc)
        elif self.month_input.collide_point(*tpos):
            self.increment(months=inc)
        elif self.day_input.collide_point(*tpos):
            self.increment(days=inc)
        elif self.hour_input.collide_point(*tpos):
            self.increment(hours=inc)
        elif self.minute_input.collide_point(*tpos):
            self.increment(minutes=inc)
        elif self.second_input.collide_point(*tpos):
            self.increment(seconds=inc)
        else:
            return False
        return True

    def reset_time(self) -> arrow.Arrow:
        """Reset the time. Override this method to changed default time."""
        self.time = arrow.now()


class _DaySelector(XGrid):

    WIDTH = util.to_pixels("35sp") * 7
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
        self.set_size(y=row_count * util.to_pixels("40sp"))

    def _get_label(self, day: int):
        return XLabelClick(text=str(day + 1), on_release=self._on_select)

    def _on_select(self, w):
        self._callback(int(w.text))


__all__ = (
    "XDateTime",
)
