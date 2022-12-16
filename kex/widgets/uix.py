"""UI widgets."""

from typing import Optional, Any, Mapping
import re
from .. import kivy as kv
from . import XMixin
from ..util import ColorType, XColor
from .layouts import XBox, XAnchor


class XLabel(XMixin, kv.Label):
    """Label."""

    def __init__(self, fixed_width: bool = False, **kwargs):
        """Initialize the class.

        Args:
            fixed_width: Adjust the height of the label while maintaining width.
        """
        kwargs = {
            "markup": True,
            "halign": "center",
            "valign": "center",
        } | kwargs
        super().__init__(**kwargs)
        self._trigger_fix_height = kv.Clock.create_trigger(self._fix_height)
        if fixed_width:
            self.bind(
                size=self._trigger_fix_height,
                text=self._trigger_fix_height,
            )
        else:
            self.bind(size=self._on_size)

    def _fix_height(self, *a):
        x = self.size[0]
        hx = self.size_hint[0]
        self.text_size = x, None
        self.texture_update()
        if hx is None:
            self.set_size(x=x, y=self.texture_size[1])
        else:
            self.set_size(hx=hx, y=self.texture_size[1])

    def _on_size(self, *a):
        self.text_size = self.size


class XLabelClick(kv.ButtonBehavior, XLabel):
    """Label with ButtonBehavior."""

    pass


class XCheckBox(XMixin, kv.CheckBox):
    """CheckBox."""

    def toggle(self, *a):
        """Toggle the active state."""
        self.active = not self.active


class XButton(XMixin, kv.Button):
    """Button."""

    def __init__(
        self,
        background_color: ColorType = XColor.from_name("blue", 0.5).rgba,
        **kwargs,
    ):
        """Initialize the class.

        Args:
            background_color: Background color of the button.
        """
        kwargs = {
            "markup": True,
            "halign": "center",
            "valign": "center",
        } | kwargs
        super().__init__(**kwargs)
        self.background_color = background_color

    def on_touch_down(self, m):
        """Overrides base class method to only react to left clicks."""
        if m.button != "left":
            return False
        return super().on_touch_down(m)


class XToggleButton(kv.ToggleButtonBehavior, XButton):
    """ToggleButton."""

    active = kv.BooleanProperty(False)
    """Behaves like an alias for the `state` property being "down"."""

    def __init__(self, **kwargs):
        """Same arguments as kivy Button."""
        super().__init__(**kwargs)
        self.bind(state=self._set_active)
        self.bind(active=self._set_state)

    def toggle(self, *args):
        """Toggles the active state of the button."""
        self.active = not self.active

    def _set_state(self, *args):
        self.state = "down" if self.active else "normal"

    def _set_active(self, *args):
        self.active = self.state == "down"


class XEntry(XMixin, kv.TextInput):
    """TextInput with sane defaults."""

    select_on_focus = kv.BooleanProperty(False)
    deselect_on_escape = kv.BooleanProperty(False)

    def __init__(
        self,
        multiline: bool = False,
        background_color: list[float] = (0.2, 0.2, 0.2, 1),
        foreground_color: list[float] = (1, 1, 1, 1),
        disabled_foreground_color: list[float] = (0.5, 0.5, 0.5, 0.5),
        text_validate_unfocus: bool = True,
        write_tab: bool = False,
        **kwargs,
    ):
        """Initialize the class.

        Args:
            multiline: If should allow multiple lines.
            background_color: Color of the background.
            foreground_color: Color of the foreground.
            disabled_foreground_color: Color of the foreground when disabled.
            text_validate_unfocus: If focus should be removed after validation
                (pressing enter on a single-line widget).
            write_tab: Allow tabs to be written.
            kwargs: keyword arguments for TextInput.
        """
        super().__init__(
            background_color=background_color,
            foreground_color=foreground_color,
            disabled_foreground_color=disabled_foreground_color,
            multiline=multiline,
            text_validate_unfocus=text_validate_unfocus,
            write_tab=write_tab,
            **kwargs,
        )

    def _on_textinput_focused(self, *args, **kwargs):
        """Overrides base method to handle selection on focus."""
        super()._on_textinput_focused(*args, **kwargs)
        if self.focus and self.select_on_focus:
            self.select_all()

    def reset_cursor_selection(self, *a):
        """Resets the cursor position and selection."""
        self.cancel_selection()
        self.cursor = 0, 0
        self.scroll_x = 0
        self.scroll_y = 0

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        """Override base method to deselect instead of defocus on escape."""
        key, _ = keycode
        r = super().keyboard_on_key_down(window, keycode, text, modifiers)
        # Handle escape
        if key == 27:
            if not self.deselect_on_escape:
                self.cancel_selection()
                self.focus = True
        return r


class XIntEntry(XEntry):
    digits_pattern = re.compile('[^0-9]')

    def insert_text(self, substring, *args, **kwargs):
        s = re.sub(self.digits_pattern, '', substring)
        return super().insert_text(s, *args, **kwargs)


class XFloatEntry(XEntry):
    digits_pattern = re.compile('[^0-9]')

    def insert_text(self, substring, *args, **kwargs):
        if '.' in self.text:
            s = re.sub(self.digits_pattern, '', substring)
        else:
            s = '.'.join(
                re.sub(self.digits_pattern, '', s)
                for s in substring.split('.', 1)
            )
        return super().insert_text(s, *args, **kwargs)


class XSlider(XMixin, kv.Slider):
    """Slider."""

    pass


class XSliderText(XBox):
    """Slider with Label."""

    def __init__(
        self,
        prefix: str = "",
        rounding: int = 3,
        box_kwargs: Optional[Mapping[str, Any]] = None,
        label_kwargs: Optional[Mapping[str, Any]] = None,
        **kwargs,
    ):
        """Initialize the class.

        Args:
            prefix: Text to prefix the value presented in the label.
            rounding: How many decimal places to show.
            box_kwargs: Keyword arguments for XBox.
            label_kwargs: Keyword arguments for XLabel.
            kwargs: Keyword arguments for XSlider.
        """
        box_kwargs = {} if box_kwargs is None else box_kwargs
        label_kwargs = {} if label_kwargs is None else label_kwargs
        label_kwargs = {"halign": "left"} | label_kwargs
        slider_kwargs = {"cursor_size": (25, 25)} | kwargs
        super().__init__(**box_kwargs)
        self.rounding = rounding
        self.prefix = prefix
        self.label = XLabel(**label_kwargs)
        self.label.set_size(hx=0.2)
        self.slider = XSlider(**slider_kwargs)
        self.add_widgets(self.label, self.slider)
        self.slider.bind(value=self._set_text)
        self._set_text(self, self.slider.value)

    def _set_text(self, w, value):
        if isinstance(value, float):
            value = round(value, self.rounding)
        if value == round(value):
            value = int(value)
        self.label.text = str(f"{self.prefix}{value}")


class XSpinner(XMixin, kv.Spinner):
    """Spinner."""

    value = kv.StringProperty("")

    def __init__(self, update_main_text: bool = True, **kwargs):
        """Same keyword arguments for Spinner.

        Args:
            update_main_text: Update the button text based on the selected value.
        """
        super().__init__(**kwargs)
        self.update_main_text = update_main_text
        if update_main_text:
            self.text_autoupdate = True

    def on_select(self, data):
        """Overrides base method."""
        pass

    def _on_dropdown_select(self, instance, data, *largs):
        if self.update_main_text:
            self.text = data
        self.value = data
        self.is_open = False
        self.on_select(data)


class XDropDown(XMixin, kv.DropDown):
    """DropDown."""

    pass


class XPickColor(XBox):
    """Color picking widget."""

    color = kv.ObjectProperty(XColor(0.5, 0.5, 0.5, 1))

    def __init__(self, **kwargs):
        """Same keyword arguments for Slider."""
        super().__init__(orientation="vertical")
        self.set_size(x=300, y=100)
        update_color = self._update_from_sliders
        self.sliders = []
        for i, c in enumerate("RGBA"):
            slider_kwargs = {
                "range": (0, 1),
                "step": 0.01,
                "value_track": True,
                "value_track_color": XColor(**{c.lower(): 0.75}).rgba,
                "value_track_width": "6dp",
                "cursor_size": (0, 0),
            } | kwargs
            s = XSliderText(**slider_kwargs)
            s.slider.bind(value=update_color)
            self.add_widget(s)
            self.sliders.append(s)
        self.r, self.g, self.b, self.a = self.sliders
        self.set_color(self.color)

    def set_color(self, color: XColor):
        """Set the current color."""
        self.r.slider.value = color.r
        self.g.slider.value = color.g
        self.b.slider.value = color.b
        self.a.slider.value = color.a

    def _update_from_sliders(self, *a):
        color = XColor(
            self.r.slider.value,
            self.g.slider.value,
            self.b.slider.value,
            self.a.slider.value,
        )
        is_bright = sum(color.rgb) > 1.5
        for s in self.sliders:
            s.label.color = (0, 0, 0, 1) if is_bright else (1, 1, 1, 1)
        self.make_bg(color)
        self.color = color


class XSelectColor(XLabelClick):
    """An XPickColor that drops down from an XLabelClick."""

    def __init__(
        self,
        prefix: str = "[u]Color:[/u]\n",
        show_color_values: bool = True,
        **kwargs,
    ):
        """Initialize the class.

        Args:
            prefix: Text to show before the RGB values.
            show_color_values: Show the RGB values of the current color.
            kwargs: Keyword arguments for the XLabelClick.
        """
        self.prefix = prefix
        self.show_color_values = show_color_values
        super().__init__(**kwargs)
        self.picker = XPickColor()
        self.dropdown = XDropDown(auto_width=False, on_dismiss=self._on_color)
        self.dropdown.set_size(*self.picker.size)
        self.dropdown.add_widget(self.picker)
        self.picker.bind(size=lambda w, s: self.dropdown.set_size(*s))
        self.bind(on_release=self.dropdown.open)
        self.on_color()

    def _on_color(self, *args):
        color = self.picker.color
        self.make_bg(color)
        text = self.prefix
        if self.show_color_values:
            text += " , ".join(str(round(c, 2)) for c in color.rgba)
        self.text = text


class XScreen(XMixin, kv.Screen):
    """Screen that can only contain one widget."""

    def __init__(self, **kwargs):
        """Same arguments as Screen."""
        super().__init__(**kwargs)
        self.view = None

    def add_widget(self, w, *args, **kwargs):
        """Overrides base method to set the view."""
        self.view = w
        super().add_widget(w, *args, **kwargs)
        if len(self.children) > 1:
            raise RuntimeError(
                f"Cannot add more than 1 widget to XScreen: {self.children=}"
            )


class XScreenManager(XMixin, kv.ScreenManager):
    """ScreenManager with custom transition behavior."""

    transition_speed = kv.NumericProperty(0.4)

    def __init__(self, **kwargs):
        """Same arguments as for ScreenManager, minus transition."""
        if "transition" in kwargs:
            del kwargs["transition"]
        super().__init__(**kwargs)
        self.transition = kv.SlideTransition(
            direction="left",
            duration=self.transition_speed,
        )

    def add_screen(self, name: str, widget: XMixin) -> XScreen:
        """Add a screen."""
        screen = self.add_widget(XScreen(name=name))
        screen.add_widget(widget)
        return screen

    def switch_name(self, name: str) -> bool:
        """Switch to a screen by name."""
        if name == self.current:
            return True
        if self.mid_transition:
            return False
        if name not in self.screen_names:
            raise ValueError(f'Found no screen by name "{name}" in {self.screen_names}')
        old_index = self.screen_names.index(self.current)
        new_index = self.screen_names.index(name)
        dir = "left" if old_index < new_index else "right"
        self.transition = kv.SlideTransition(
            direction=dir,
            duration=self.transition_speed,
        )
        self.current = name
        return True

    @property
    def mid_transition(self) -> bool:
        """If there is a transition in progress."""
        return 0 < self.current_screen.transition_progress < 1

    @classmethod
    def from_widgets(cls, widgets: Mapping[str, XMixin], **kwargs) -> "XScreenManager":
        """Create an XScreenManager from a dictionary of screen names and widgets."""
        sm = cls(**kwargs)
        for n, w in widgets.items():
            screen = XScreen(name=n)
            screen.add_widget(w)
            sm.add_widget(screen)
        return sm


class XModalView(XMixin, kv.ModalView):
    pass


class XModal(XAnchor):
    """A XAnchor with an XInputManager that can de/attach to a container."""

    def __init__(self, container: XAnchor, name: str = "Unnamed", **kwargs):
        super().__init__(**kwargs)
        self.container = container
        self.bind(parent=self._on_parent)

    def toggle(self, *args, set_as: Optional[bool] = None):
        if set_as is None:
            set_as = self.parent is None
        if set_as:
            self.open()
        else:
            self.dismiss()

    def open(self, *args):
        if self.parent is not None:
            return
        self.container.add_widget(self)

    def dismiss(self, *args):
        if self.parent is None:
            return
        self.container.remove_widget(self)

    def _on_parent(self, w, parent):
        self.im.active = parent is not None
