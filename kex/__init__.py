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
    from_atlas,
    restart_script,
    placeholder,
    consume_args,
    schedule_once,
    schedule_interval,
    create_trigger,
    snoozing_trigger,
    queue_around_frame,
)
from .widgets import XWidget
from .widgets.layouts import (
    XBox,
    XZBox,
    XDBox,
    XGrid,
    XRelative,
    XStack,
    XAnchor,
    XCurtain,
    XScroll,
)
from .widgets.uix import (
    XLabel,
    XCheckBox,
    XButton,
    XToggleButton,
    XEntry,
    XIntEntry,
    XFloatEntry,
    XSlider,
    XSliderText,
    XSpinner,
    XDropDown,
    XPickColor,
    XSelectColor,
    XScreenManager,
    XScreen,
    XModalView,
    XModal,
)
from .widgets.list import XList
from .widgets.inputpanel import XInputPanel, XInputPanelWidget
from .widgets.hotkeycontroller import XHotkeyController
from .widgets.atlas import XAtlasPreview
from .behaviors import XFocusBehavior
from .app import XApp


__all__ = []
