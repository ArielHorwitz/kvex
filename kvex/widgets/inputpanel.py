"""Panel of simple input widgets."""

from dataclasses import dataclass, field
from typing import Any, Optional, Callable
from .. import kivy as kv
from .layouts import XAnchor, XDBox, XBox, XCurtain
from .uix import (
    XLabel,
    XButton,
    XInput,
    XIntInput,
    XFloatInput,
    XCheckBox,
    XSpinner,
)


HEIGHT_UNIT = 40


@dataclass
class XInputPanelWidget:
    label: str
    widget: str = "str"
    default: Any = None
    orientation: str = "horizontal"
    showing: bool = True
    label_hint: float = 1
    italic: bool = True
    bold: bool = False
    halign: Optional[str] = None
    choices: list = field(default_factory=list)


class BaseInputWidget(XBox):
    def __init__(self, w: XInputPanelWidget, on_value: Callable, on_invoke: Callable):
        assert w.widget == self.wtype
        self.specification = w
        super().__init__(orientation=w.orientation)
        default_halign = "right" if w.orientation == "horizontal" else "center"
        # Build
        self.label = XLabel(
            text=w.label,
            padding=(10, 5),
            italic=w.italic,
            bold=w.bold,
            halign=w.halign or default_halign,
        )
        self.widget = self._get_widget(w, on_value, on_invoke)
        assert self.widget is not None
        # Assemble
        height = HEIGHT_UNIT * (1 + (w.orientation == "vertical"))
        self.set_size(y=height)
        self.label.set_size(hx=w.label_hint)
        self.add_widgets(self.label, self.widget)

    def set_enabled(self, set_as: Optional[bool] = None, /):
        if set_as is None:
            set_as = not self.label.disabled
        self.label.disabled = set_as

    def set_focus(self):
        pass


class StringInputWidget(BaseInputWidget):
    wtype = "str"
    _entry_class = XInput
    _text_default = ""
    _password = False

    def _get_widget(
        self,
        w: XInputPanelWidget,
        on_value: Callable,
        on_invoke: Callable,
    ):
        self._entry = self._entry_class(
            text=str(w.default or self._text_default),
            password=self._password,
            select_on_focus=True,
        )
        self._entry.bind(text=on_value, on_text_validate=on_invoke)
        return self._entry

    def get_value(self) -> str:
        return self._entry.text

    def set_value(self, value: Optional[str] = None, /):
        if value is None:
            value = self.specification.default or self._text_default
        self._entry.text = value

    def set_enabled(self, set_as: Optional[bool] = None, /):
        super().set_enabled(set_as)
        if set_as is None:
            set_as = not self._entry.disabled
        self._entry.disabled = set_as

    def set_focus(self):
        self._entry.focus = True


class BooleanInputWidget(BaseInputWidget):
    wtype = "bool"

    def _get_widget(
        self,
        w: XInputPanelWidget,
        on_value: Callable,
        on_invoke: Callable,
    ):
        self._checkbox = XCheckBox(active=w.default or False)
        self._checkbox.bind(active=on_value)
        if w.orientation == "vertical":
            return self._checkbox
        self._checkbox.set_size(x=HEIGHT_UNIT)
        frame = XAnchor(anchor_x="left")
        frame.add_widget(self._checkbox)
        return frame

    def get_value(self) -> bool:
        return self._checkbox.active

    def set_value(self, value: Optional[bool] = None, /):
        if value is None:
            value = self.specification.default
        self._checkbox.active = value

    def set_enabled(self, set_as: Optional[bool] = None, /):
        super().set_enabled(set_as)
        if set_as is None:
            set_as = not self._checkbox.disabled
        self._checkbox.disabled = set_as

    def set_focus(self):
        self._checkbox.focus = True


class IntInputWidget(StringInputWidget):
    wtype = "int"
    _entry_class = XIntInput
    _text_default = "0"

    def get_value(self) -> int:
        return int(self._entry.text or 0)

    def set_value(self, value: Optional[int] = None, /):
        if value is None:
            value = self.specification.default or 0
        self._entry.text = str(value)


class FloatInputWidget(StringInputWidget):
    wtype = "float"
    _entry_class = XFloatInput
    _text_default = "0"

    def get_value(self) -> float:
        return float(self._entry.text or 0)

    def set_value(self, value: Optional[float] = None, /):
        if value is None:
            value = self.specification.default or 0
        self._entry.text = str(value)


class PasswordInputWidget(StringInputWidget):
    wtype = "password"
    _password = True


class ChoiceInputWidget(BaseInputWidget):
    wtype = "choice"

    def _get_widget(
        self,
        w: XInputPanelWidget,
        on_value: Callable,
        on_invoke: Callable,
    ):
        self._spinner = XSpinner(
            text=w.default or "",
            values=w.choices,
            text_autoupdate=True,
        )
        self._spinner.bind(text=on_value)
        return self._spinner

    def get_value(self) -> bool:
        return self._spinner.text

    def set_value(self, value: Optional[str] = None, /):
        if value is None:
            value = self.specification.default or ""
        self._spinner.text = value

    def set_enabled(self, set_as: Optional[bool] = None, /):
        super().set_enabled(set_as)
        if set_as is None:
            set_as = not self._spinner.disabled
        self._spinner.disabled = set_as


INPUT_WIDGET_CLASSES: dict[str, BaseInputWidget] = dict(
    str=StringInputWidget,
    bool=BooleanInputWidget,
    int=IntInputWidget,
    float=FloatInputWidget,
    password=PasswordInputWidget,
    choice=ChoiceInputWidget,
)


class XInputPanel(XAnchor):
    reset_text = kv.StringProperty("Reset defaults")
    """Text for the reset button, leave empty to hide."""
    invoke_text = kv.StringProperty("Send")
    """Text to show on the invoke button, leave empty to hide."""

    def __init__(
        self,
        widgets: dict[str, XInputPanelWidget],
        /,
        **kwargs,
    ):
        """Initialize the class.

        Args:
            widgets: Dictionary of names to widgets.
        """
        super().__init__(**kwargs)
        self.widgets: dict[str, BaseInputWidget] = dict()
        self._curtains: dict[str, XCurtain] = dict()
        # Widgets
        self._main_frame = XDBox()
        self.add_widget(self._main_frame)
        self._reset_btn = XButton(text=self.reset_text, on_release=self.reset_defaults)
        self._invoke_btn = XButton(text=self.invoke_text, on_release=self._do_invoke)
        self._reset_btn_frame = XAnchor.wrap(self._reset_btn)
        self._invoke_btn_frame = XAnchor.wrap(self._invoke_btn)
        # Input Widgets
        for name, w in widgets.items():
            iw_cls = INPUT_WIDGET_CLASSES[w.widget]
            input_widget = iw_cls(w, self._do_values, self._do_invoke)
            curtain = XCurtain(content=input_widget, showing=w.showing)
            curtain.set_size(y=input_widget.height)
            self.widgets[name] = input_widget
            self._curtains[name] = curtain
            self._main_frame.add_widget(curtain)
        # Controls
        controls = XBox()
        if self.reset_text:
            controls.add_widget(self._reset_btn_frame)
        if self.invoke_text:
            controls.add_widget(self._invoke_btn_frame)
        if len(controls.children) == 1:
            controls = XAnchor.wrap(controls, x=.5)
        controls.set_size(y=HEIGHT_UNIT)
        if len(controls.children) > 0:
            self._main_frame.add_widget(controls)
        # Bindings
        self.bind(
            reset_text=self._on_reset_text,
            invoke_text=self._on_invoke_text,
        )
        self.register_event_type("on_invoke")
        self.register_event_type("on_values")

    def get_value(self, widget_name: str, /) -> Any:
        """Get a value by name."""
        widget = self.widgets[widget_name]
        return widget.get_value()

    def get_values(self) -> dict[str, Any]:
        """Get all values."""
        return {name: iw.get_value() for name, iw in self.widgets.items()}

    def reset_defaults(self, *args, **kwargs):
        """Reset all values to their defaults."""
        for iw in self.widgets.values():
            iw.set_value()

    def set_focus(self, widget_name: str, /):
        """Focus a widget by name."""
        widget = self.widgets[widget_name]
        widget.set_focus()

    def set_enabled(self, widget_name: str, set_as: bool = True, /):
        """Enable or disable a widget by name."""
        widget = self.widgets[widget_name]
        widget.set_enabled(set_as)

    def set_showing(self, widget_name: str, set_as: bool = True, /):
        """Show or hide a widget by name."""
        curtain = self._curtains[widget_name]
        curtain.showing = set_as

    def on_invoke(self, values: dict):
        """Triggered when the invoke button is pressed or otherwise sent by user."""
        pass

    def on_values(self, values: dict):
        """Triggered when any of the values change."""
        pass

    def _do_invoke(self, *args):
        self.dispatch("on_invoke", self.get_values())

    def _do_values(self, *args):
        self.dispatch("on_values", self.get_values())

    def _on_reset_text(self, w, text):
        self._reset_btn.text = text

    def _on_invoke_text(self, w, text):
        self._invoke_btn.text = text
