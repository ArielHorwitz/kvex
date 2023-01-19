"""Layout widgets."""

from typing import Optional
from .. import kivy as kv
from .. import assets
from .. import util
from ..colors import XColor
from ..behaviors import XThemed
from .widget import XWidget


class XDynamicLayoutMixin:
    """Mixin for layouts that are responsive to their children.

    Overrides the layout trigger to delay layout effects to the next frame. Subclasses
    should override `do_layout` (and call super) to leverage this mixin.
    """
    def __init__(self, **kwargs):
        """Initialize the class."""
        self._layout_trigger = util.create_trigger(self.do_layout)
        super().__init__(**kwargs)

    def _trigger_layout(self, *args):
        util.snooze_trigger(self._layout_trigger)


class XBox(XWidget, kv.BoxLayout):
    """BoyLayout."""

    pass


class XDynamic(XDynamicLayoutMixin, XBox):
    """XBox that will dynamically resize based on orientation and children's size.

    When vertical, height will be adjusted to fit children exactly. When horizontal,
    width will be adjusted to fit children exactly.

    .. warning:: Layout behavior will break if children's size hint is set.
    """

    def __init__(self, **kwargs):
        """Initialize the class."""
        kwargs = dict(orientation="vertical") | kwargs
        super().__init__(**kwargs)

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

    pass


class XMargin(XDynamicLayoutMixin, XAnchor):
    """XAnchor that will dynamically resize to child's size with added margins."""

    margin_x = kv.NumericProperty("10dp")
    """Horizontal margin."""
    margin_y = kv.NumericProperty("10dp")
    """Vertical margin."""
    margin = kv.ReferenceListProperty(margin_x, margin_y)
    """Margins of x and y."""

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


class XJustify(XDynamicLayoutMixin, XAnchor):
    """XAnchor that will dynamically resize to justify the first child widget.

    First child widget must not have size_hint set along the specified axis in
    `orientation`.
    """

    orientation = kv.OptionProperty("horizontal", options=["horizontal", "vertical"])
    """Axis to justify."""

    def do_layout(self, *args, **kwargs):
        """Resize to center first child."""
        if self.children:
            child = self.children[0]
            hx, hy = child.size_hint
            if self.orientation == "horizontal" and child.size_hint_x is None:
                self.set_size(y=child.height)
            elif self.orientation == "vertical" and child.size_hint_y is None:
                self.set_size(x=child.width)
        super().do_layout(*args, **kwargs)


class XFrame(XThemed, XAnchor):
    """Themed `XAnchor` with a background."""

    BG = str(assets.get_image("xframe_bg"))

    def on_subtheme(self, subtheme):
        """Apply background color."""
        self.make_bg(subtheme.bg, source=self.BG)


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


def wrap(
    widget: kv.Widget,
    /,
    pad: bool | util._KIVY_DIMENSIONS | XAnchor = False,
    frame: bool | XFrame = False,
    margin: bool | util._KIVY_DIMENSIONS | XMargin = False,
    justify: Optional[str | XJustify] = None,
    debug: bool = False,
    **kwargs,
):
    """Wrap a widget in layouts.

    Wraps the widget with a layout for each argument ***in order***: pad, frame, margin,
    and justify. For more fine-grained control, each layout can be premade manually and
    passed as the argument.

    Will skip any layout not specified. If no other layout has been used or if any extra
    keyword arguments are passed, they will be passed to a final `XAnchor` which will
    wrap everything.

    For example:
    ```python3
    widget = kx.XLabel()
    widget.set_size("50dp", "50dp")
    # This:
    outer = kx.wrap(widget, margin="10dp", justify="horizontal")
    # Is equivalent to:
    inner = kx.XMargin(margin="10dp")
    inner.add_widget(widget)
    outer = kx.wrap(inner, justify="horizontal")
    # Is equivalent to:
    inner = kx.XMargin(margin="10dp")
    inner.add_widget(widget)
    outer = kx.XJustify(orientation="horizontal")
    outer.add_widget(inner)
    ```

    .. warning::
        Wrapping all these layouts in sequence may not lead to the results you are
        looking for.

    Some layouts are responsive to the children's size, others are not. For example,
    wrapping padding and then wrapping justify will not seem to have an effect, since
    the padding layout (which is not responsive to children's size) will simply take up
    all available space and justifying may not seem to work.

    For this reason, automatically wrapping in this order may not be enough, and would
    require you to call this function multiple times for each layout to achieve the
    intended behavior. See class documentations for details.

    Args:
        pad: Add padding using an `XAnchor` layout.
        frame: Frame using an `XFrame` layout.
        margin: Add margins using an `XMargin` layout.
        justify: Orientation to justify using an `XJustify` layout.
        debug: Add background color to layouts: blue for padding, green for frame, red
            for margin, and cyan for justify.
        kwargs: Keyword arguments for an outermost `XAnchor`.
    """
    outer = widget
    if debug:
        outer.make_bg(XColor(0, 0, 0))
    outer = _wrap_pad(outer, pad, debug)
    outer = _wrap_frame(outer, frame, debug)
    outer = _wrap_margin(outer, margin, debug)
    outer = _wrap_justify(outer, justify, debug)
    if kwargs or outer is widget:
        outer = XAnchor.with_add(outer, **kwargs)
        if debug:
            outer.make_bg(XColor(1, 0, 1))
    return outer


def _wrap_pad(outer, pad, debug):
    # Blue
    if pad is not False:
        if pad is True:
            padding = "10dp", "10dp"
        else:
            padding = util._extend_dimensions(pad)
        outer = XAnchor.with_add(outer, padding=padding)
        if debug:
            outer.make_bg(XColor(0, 0, 1))
    return outer


def _wrap_frame(outer, frame, debug):
    # Green
    if frame:
        if not isinstance(frame, XFrame):
            frame = XFrame(enable_theming=not debug)
        frame.add_widget(outer)
        outer = frame
        if debug:
            outer.make_bg(XColor(0, 1, 0))
    return outer


def _wrap_margin(outer, margin, debug):
    # Red
    if margin is not False:
        if margin is True:
            margin = "10dp", "10dp"
        if not isinstance(margin, XMargin):
            margin = XMargin(margin=util._extend_dimensions(margin))
        margin.add_widget(outer)
        outer = margin
        if debug:
            outer.make_bg(XColor(1, 0, 0))
    return outer


def _wrap_justify(outer, justify, debug):
    # Cyan
    if justify is not None:
        if not isinstance(justify, XJustify):
            justify = XJustify(orientation=justify)
        justify.add_widget(outer)
        outer = justify
        if debug:
            outer.make_bg(XColor(0, 1, 1))
    return outer


__all__ = (
    "wrap",
    "XBox",
    "XDynamic",
    "XJustify",
    "XMargin",
    "XGrid",
    "XRelative",
    "XStack",
    "XAnchor",
    "XFrame",
    "XAnchorDelayed",
    "XCurtain",
    "XDynamicLayoutMixin",
)
