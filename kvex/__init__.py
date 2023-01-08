"""Kvex - A Kivy extension library for desktop applications.

[Kivy](https://kivy.org/) is arguably the best GUI framework for Python, and the list of
things that can be improved is short. Keeping this in mind, Kvex does not intend to
"improve" kivy but rather make it more convenient to use, in particular for desktop
applications.

## Easy importing
Kvex provides a single namespace for many kivy objects, enabling a single import for a
large part of the API:
```python3
import kvex.kivy as kv

kv.App
kv.AnchorLayout
kv.Button
kv.SliderTransition
kv.Rectangle
kv.Clock
```

Kvex offers some custom widgets (and functions), all available from a single import:
```python3
import kvex as kx

kx.XApp
kx.XAnchor
kx.XButton
kx.get_color
kx.schedule_once
```

## Widgets
All Kvex widgets use the `kvex.widgets.widget.XWidget` mixin class. It provides several
convenience methods for kivy widgets. These include an intuitive way to set size with
`XWidget.set_size` and a quick and easy way to create a background with
`XWidget.make_bg`.

Kvex offers some more complex widgets commonly required by desktop applications, such as
hotkey controls and large collections of input widgets of many types:
* `kvex.widgets.hotkeycontroller.XHotkeyController`
* `kvex.widgets.inputpanel.XInputPanel`
* `kvex.widgets.buttonbar.XButtonBar`
"""

# flake8: noqa
# Ignoring flake8 errors E402,F401 because of late imports and unused imports

import os as _os

# Kivy configuration must be done before importing kivy
_os.environ["KIVY_NO_ARGS"] = "1"  # no consuming script arguments
_os.environ["KCFG_KIVY_LOG_LEVEL"] = "warning"  # no spamming console on startup


from .kivy import *
from .util import *
from .colors import *
from .widgets import *
from .behaviors import *
from .app import *
