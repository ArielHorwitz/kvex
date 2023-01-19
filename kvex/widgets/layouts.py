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


class XDynamic(XBox):
    """XBox that will dynamically resize based on orientation and children's size.

    When vertical, height will be adjusted to fit children exactly. When horizontal,
    width will be adjusted to fit children exactly.

    .. warning:: Layout behavior will break if children's size hint is set.
    """

    def __init__(self, **kwargs):
        """Initialize the class."""
        kwargs = dict(orientation="vertical") | kwargs
        super().__init__(**kwargs)
        self._layout_trigger = util.create_trigger(self.do_layout)

    def _trigger_layout(self, *args):
        util.snooze_trigger(self._layout_trigger)

    def do_layout(self, *args, **kwargs):
        """Resize based on children, before doing layout."""
        if self.orientation == "horizontal":
            width = sum([util.sp2pixels(c.width) for c in self.children])
            self.set_size(x=width)
        elif self.orientation == "vertical":
            height = sum([util.sp2pixels(c.height) for c in self.children])
            self.set_size(y=height)
        super().do_layout(*args, **kwargs)


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


class XMargin(XAnchor):
    """XAnchor that will dynamically resize to child's size with added margins."""

    margin_x = kv.NumericProperty("10dp")
    """Horizontal margin."""
    margin_y = kv.NumericProperty("10dp")
    """Vertical margin."""
    margin = kv.ReferenceListProperty(margin_x, margin_y)
    """Margins of x and y."""

    def __init__(self, **kwargs):
        """Initialize the class."""
        super().__init__(**kwargs)
        self._layout_trigger = util.create_trigger(self.do_layout)

    def _trigger_layout(self, *args):
        util.snooze_trigger(self._layout_trigger)

    def do_layout(self, *args, **kwargs):
        """Resize to first child's size plus margins."""
        if self.children:
            child = self.children[0]
            if not child.size_hint_x:
                margin_x = util.sp2pixels(self.margin_x)
                w = util.sp2pixels(child.width)
                self.set_size(x=w + margin_x * 2)
            if not child.size_hint_y:
                margin_y = util.sp2pixels(self.margin_y)
                h = util.sp2pixels(child.height)
                self.set_size(y=h + margin_y * 2)
        super().do_layout(*args, **kwargs)


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
    "XDynamic",
    "XMargin",
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
