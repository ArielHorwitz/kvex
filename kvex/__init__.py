""".. include:: ../README.md

# Install
```bash
pip install git+https://github.com/ArielHorwitz/kvex.git
```

# Using Kvex

## Easy importing
Kvex provides a single namespace for many Kivy objects, enabling a single import for a
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

Virtually all of the objects that Kvex offers are available from a single import:
```python3
import kvex as kx

kx.XApp
kx.XAnchor
kx.XButton
kx.XThemed
kx.pad
kx.frame
kx.schedule_once
kx.snooze_trigger
```

.. note::
    The documentation may name the full path (e.g. `kvex.widgets.widget.XWidget`) for
    sake of reference, but should still be available directly from `kvex.XWidget`.

## Widgets
Kvex widgets use the `kvex.widgets.widget.XWidget` mixin class. It provides several
convenience methods for Kivy widgets. These include an intuitive way to set size with
`XWidget.set_size` and a quick and easy way to create a background with
`XWidget.make_bg`.

Kvex offers some more complex widgets commonly required by desktop applications. Some
such examples are:
* `kvex.widgets.hotkeycontroller.XHotkeyController`
* `kvex.widgets.inputpanel.XInputPanel`
* `kvex.widgets.buttonbar.XButtonBar`


## Themes
Many Kvex widgets use the `kvex.behaviors.XThemed` mixin class. It enables using a
consistent color palette across widgets. The theme is managed by `kvex.app.XApp`:
```python3
import kx

app = kx.XApp()
app.set_theme("mousefox")
```

Each theme has several subthemes (which are essentially labelled color palettes) that
can be used interchangeably (see `kvex.colors.SubTheme`). Each of these subthemes has
background, foreground, and accent colors to be used by widgets. Everything should look
fine as long as you match background and foreground colors from the same subtheme.

When creating widgets:
```python3
with self.app.subtheme_context("secondary"):  # Set default subtheme
    # All widgets in this code block will default to "secondary"
    label = kx.XLabel(text="Secondary fg on secondary bg")
    label_frame = kx.frame(label, background=True)  # Put label on background color
```

When subclassing widgets:
```python3
import kx
import kx.kivy as kv

class MyThemedLabel(kx.Themed, kv.Label):
    # Example of a themed label.

    def on_subtheme(self, subtheme: kx.SubTheme):
        # Set the label's background and foreground colors.
        self.make_bg(subtheme.bg)
        self.color = subtheme.fg.rgba

my_label = MyThemedLabel(
    text="Secondary fg on secondary bg",
    subtheme_name="secondary",
)
```
"""  # noqa: D415

# flake8: noqa
# Ignoring flake8 errors E402,F401,F403 because of late imports and unused imports

import os as _os

# Kivy configuration must be done before importing kivy
_os.environ["KIVY_NO_ARGS"] = "1"  # no consuming script arguments
_os.environ["KCFG_KIVY_LOG_LEVEL"] = "warning"  # no spamming console on startup


from .kivy import *
from .util import *
from .colors import *
from .assets import *
from .widgets import *
from .behaviors import *
from .app import *
