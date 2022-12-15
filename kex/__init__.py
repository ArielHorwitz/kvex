"""The Kex library.

An extension of the [Kivy](https://kivy.org/) library. It focuses on programmatically
writing Kivy desktop apps.
"""

# flake8: noqa
# Ignoring flake8 errors E402,F401 because of late imports and unused imports

import os as __os

# Kivy configuration must be done before importing kivy
__os.environ["KIVY_NO_ARGS"] = "1"  # no consuming script arguments
__os.environ["KCFG_KIVY_LOG_LEVEL"] = "warning"  # no spamming console on startup


from .kivy import (
    EventDispatcher,
    ButtonBehavior,
    FocusBehavior,
    ToggleButtonBehavior,
    NoTransition,
    FadeTransition,
    CardTransition,
    SlideTransition,
    SwapTransition,
    WipeTransition,
    ShaderTransition,
    InstructionGroup,
    Color,
    Rectangle,
    Rotate,
    PushMatrix,
    PopMatrix,
    ObjectProperty,
    AliasProperty,
    StringProperty,
    NumericProperty,
    BooleanProperty,
    ListProperty,
    DictProperty,
    OptionProperty,
    ReferenceListProperty,
    CoreLabel,
    CoreMarkupLabel,
    escape_markup,
)
from .util import (
    ColorType,
    XColor,
    get_color,
    random_color,
    center_sprite,
    text_texture,
    restart_script,
    placeholder,
    consume_args,
    schedule_once,
    schedule_interval,
    create_trigger,
    snoozing_trigger,
    queue_around_frame,
)
from .widgets import XMixin, XWidget
from .widgets.layouts import (
    XBox as Box,
    XZBox as ZBox,
    XDBox as DBox,
    XGrid as Grid,
    XRelative as Relative,
    XStack as Stack,
    XAnchor as Anchor,
    XScroll as Scroll,
)
from .widgets.uix import (
    XLabel as Label,
    XCheckBox as CheckBox,
    XButton as Button,
    XToggleButton as ToggleButton,
    XEntry as Entry,
    XSlider as Slider,
    XSliderText as SliderText,
    XSpinner as Spinner,
    XDropDown as DropDown,
    XPickColor as PickColor,
    XSelectColor as SelectColor,
    XScreenManager as ScreenManager,
    XScreen as Screen,
    XModalView as ModalView,
    XModal as Modal,
)
from .widgets.list import XList as List
from .widgets.hotkeycontroller import HotkeyController
from .widgets.app import XApp as App


__all__ = []
