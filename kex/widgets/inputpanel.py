"""Panel of simple input widgets."""

from dataclasses import dataclass, field
from typing import Any, Optional
from .. import kivy as kv
from .layouts import XAnchor, XDBox, XBox
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
    label_hint: float = 1
    italic: bool = True
    bold: bool = False
    halign: Optional[str] = None
    choices: list = field(default_factory=list)


class BaseInputWidget(XBox):
    def __init__(self, w: XInputPanelWidget):
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
        self.widget = self._get_widget(w)
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


class StringInputWidget(BaseInputWidget):
    wtype = "str"
    _entry_class = XInput
    _text_default = ""
    _password = False

    def _get_widget(self, w: XInputPanelWidget):
        self._entry = self._entry_class(
            text=str(w.default or self._text_default),
            password=self._password,
        )
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


class BooleanInputWidget(BaseInputWidget):
    wtype = "bool"

    def _get_widget(self, w: XInputPanelWidget):
        self._checkbox = XCheckBox(active=w.default or False)
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

    def _get_widget(self, w: XInputPanelWidget):
        self._spinner = XSpinner(
            value=w.default or "",
            values=w.choices,
        )
        return self._spinner

    def get_value(self) -> bool:
        return self._spinner.value

    def set_value(self, value: Optional[bool] = None, /):
        if value is None:
            value = self.specification.default or ""
        self._spinner.value = value

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
    reset_text = kv.StringProperty("Reset")
    """Text for the reset button, leave empty to hide."""
    invoke_text = kv.StringProperty("Send")
    """Text to show on the invoke button."""
    invoke_callback = kv.ObjectProperty(None, allownone=True)
    """Callback for when the invoke button is pressed."""

    def __init__(
        self,
        widgets: dict[str, XInputPanelWidget],
        /,
        *,
        orientation: str = "vertical",
        **kwargs,
    ):
        """Initialize the class.

        Args:
            widgets: Dictionary of names to widgets.
            orientation: Passed to the BoxLayout.
        """
        super().__init__(**kwargs)
        self.widgets: dict[str, BaseInputWidget] = dict()
        # Widgets
        self._main_frame = XBox() if orientation == "horizontal" else XDBox()
        self.add_widget(self._main_frame)
        self._reset_btn = XButton(text=self.reset_text, on_release=self.reset_defaults)
        self._invoke_btn = XButton(text=self.invoke_text, on_release=self.do_invoke)
        self._reset_btn_frame = XAnchor.wrap(self._reset_btn)
        self._invoke_btn_frame = XAnchor.wrap(self._invoke_btn)
        # Input Widgets
        for name, w in widgets.items():
            iw_cls = INPUT_WIDGET_CLASSES[w.widget]
            input_widget = iw_cls(w)
            self.widgets[name] = input_widget
            self._main_frame.add_widget(input_widget)
        # Controls
        controls = XBox()
        if self.reset_text:
            controls.add_widget(self._reset_btn_frame)
        if self.invoke_text:
            controls.add_widget(self._invoke_btn_frame)
        if len(controls.children) == 1:
            controls = XAnchor.wrap(controls, padding_weight=(.5, 0.9))
        controls.set_size(y=HEIGHT_UNIT)
        self._main_frame.add_widget(controls)
        # Bindings
        self.bind(
            reset_text=self._on_reset_text,
            invoke_text=self._on_invoke_text,
            invoke_callback=self._on_invoke_callback,
        )

    def get_values(self) -> dict[str, Any]:
        return {name: iw.get_value() for name, iw in self.widgets.items()}

    def reset_defaults(self, *args, **kwargs):
        for iw in self.widgets.values():
            iw.set_value()

    def do_invoke(self, *args):
        if self.invoke_callback:
            self.invoke_callback(self.get_values())

    def _on_invoke_callback(self, w, invoke_callback):
        self._invoke_btn_frame.showing = bool(invoke_callback)

    def _on_reset_text(self, w, text):
        self._reset_btn.text = text
        self._reset_btn_frame.showing = bool(text)

    def _on_invoke_text(self, w, text):
        self._invoke_btn.text = text
