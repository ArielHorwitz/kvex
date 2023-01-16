"""Layout widgets."""

from typing import Optional
import functools
from .. import kivy as kv
from .. import assets
from .. import util
from ..behaviors import XThemed
from .widget import XWidget


class XBox(XWidget, kv.BoxLayout):
    """BoyLayout."""

    pass


class XZBox(XWidget, kv.GridLayout):
    """Behaves like a Box where widgets are drawn in reverse order."""

    def __init__(
        self,
        *,
        orientation: str = "horizontal",
        **kwargs,
    ):
        """Initialize the class."""
        if orientation == "horizontal":
            kwargs["orientation"] = "rl-tb"
            kwargs["rows"] = 1
        elif orientation == "vertical":
            kwargs["orientation"] = "lr-bt"
            kwargs["cols"] = 1
        else:
            raise ValueError('orientation must be "horizontal" or "vertical"')
        super().__init__(**kwargs)

    def add_widget(self, *args, **kwargs):
        """Overrides base method to insert correctly."""
        kwargs["insert_last"] = True
        super().add_widget(*args, **kwargs)


class XDBox(XWidget, kv.GridLayout):
    """Behaves like a Box that will dynamically resize based on children's height."""

    def __init__(self, cols: int = 1, **kwargs):
        """Initialize the class."""
        super().__init__(cols=cols, **kwargs)
        self.bind(children=self._resize)
        trigger = util.create_trigger(self._resize)
        self._snooze_trigger = lambda *a: util.snooze_trigger(trigger)

    def add_widget(self, w, *args, **kwargs):
        """Overrides base method in order to bind to size changes."""
        w.bind(size=self._resize)
        super().add_widget(w, *args, **kwargs)
        self._snooze_trigger()

    def _resize(self, *a):
        self.set_size(hx=1, y=sum([util.sp2pixels(c.height) for c in self.children]))


class XGrid(XWidget, kv.GridLayout):
    """GridLayout."""

    pass


class XStack(XWidget, kv.StackLayout):
    """StackLayout."""

    pass


class XRelative(XWidget, kv.RelativeLayout):
    """RelativeLayout."""

    pass


class XAnchor(XWidget, kv.AnchorLayout):
    """AnchorLayout."""

    @classmethod
    def wrap(cls, widget: kv.Widget, /, **kwargs) -> "XAnchor":
        """Create `XAnchor` with child widget.

        Args:
            widget: Widget to wrap.
            kwargs: Keyword arguments for the XAnchor.
        """
        anchor = cls(**kwargs)
        anchor.add_widget(widget)
        return anchor


class XFrame(XThemed, XAnchor):
    """Themed `XAnchor` with a background."""

    BG = str(assets.get_image("xframe_bg"))

    def on_subtheme(self, subtheme):
        """Apply background color."""
        self.make_bg(subtheme.bg, source=self.BG)


wrap = XAnchor.wrap
pwrap = functools.partial(XAnchor.wrap, padding="10sp")
"""Like `wrap` but with '10sp' padding."""
fwrap = XFrame.wrap
"""Like `wrap` but with `XFrame`."""
fpwrap = functools.partial(XFrame.wrap, padding="10sp")
"""Like `fwrap` but with '10sp' padding."""


class XAnchorDelayed(XAnchor):
    """An XAnchor that delays layout events.

    Useful for preventing window drag-resize from creating too many events.
    """

    layout_event_delay = kv.NumericProperty(0.1)
    """Delay for layout events."""
    _delayed_layout_event = None

    def do_layout(self, *args, **kwargs):
        """Override base method to delay layout events."""
        if self._delayed_layout_event:
            self._delayed_layout_event.cancel()
        _real_do_layout = super().do_layout
        self._delayed_layout_event = util.schedule_once(
            lambda dt: _real_do_layout(*args, **kwargs),
            self.layout_event_delay,
        )


class XCurtain(XAnchor):
    """AnchorLayout that can show or hide it's content."""

    content = kv.ObjectProperty(None, allownone=True)
    """Widget to show and hide."""
    showing = kv.BooleanProperty(True)
    """If the content widget is showing."""
    dynamic = kv.BooleanProperty(False)
    """If the the curtain should resize based on content size and visibility."""

    def __init__(self, *args, **kwargs):
        """Initialize the class."""
        super().__init__(*args, **kwargs)
        self.bind(
            content=self._on_properties,
            showing=self._on_properties,
            dynamic=self._on_properties,
        )
        self._on_properties()

    def _on_properties(self, *args):
        if self.showing and self.content:
            if self.content.parent:
                self.clear_widgets()
            if not self.content.parent:
                self.add_widget(self.content)
            if self.dynamic:
                self.set_size(*self.content.size)
        else:
            self.clear_widgets()
            if self.dynamic:
                self.set_size(0, 0)

    def show(self, *args, **kwargs):
        """Show the content widget."""
        self.showing = True

    def hide(self, *args, **kwargs):
        """Hide the content widget."""
        self.showing = False

    def toggle(self, *args, set_as: Optional[bool] = None, **kwargs):
        """Toggle showing the content widget."""
        if set_as is None:
            set_as = not self.showing
        self.showing = set_as


__all__ = (
    "XBox",
    "XZBox",
    "XDBox",
    "XGrid",
    "XRelative",
    "XStack",
    "XAnchor",
    "XFrame",
    "wrap",
    "pwrap",
    "fwrap",
    "fpwrap",
    "XAnchorDelayed",
    "XCurtain",
)
