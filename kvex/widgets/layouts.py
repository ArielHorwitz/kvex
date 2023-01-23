"""Layout widgets.

Contains layout widgets that inherit from `kvex.widgets.widget.XWidget` and several
common functions: `pad`, `frame`, and `justify`.
"""

from typing import Optional, Iterable
from .. import kivy as kv
from .. import assets
from .. import util
from ..colors import XColor
from ..behaviors import XThemed
from .widget import XWidget


DEFAULT_SPACING = util.to_pixels("10dp")


class XLayout(XWidget):
    """Layout base class with convenience methods."""

    def add_widgets(self, *children: Iterable[kv.Widget], **kwargs):
        """Add multiple widgets."""
        if not children:
            raise ValueError("No children given.")
        for child in children:
            if not isinstance(child, kv.Widget):
                raise TypeError(f"Expected kivy widgets, instead got: {children}")
            self.add_widget(child, **kwargs)


class XDynamicLayoutMixin:
    """Mixin for layouts that dynamically resize to their (first) child's size.

    Overrides the layout trigger to delay layout effects to the next frame. Subclasses
    should override `do_layout` (and call super) to use this mixin.
    """
    def __init__(self, **kwargs):
        """Initialize the class."""
        self._layout_trigger = util.create_trigger(self.do_layout)
        super().__init__(**kwargs)

    def _trigger_layout(self, *args):
        util.snooze_trigger(self._layout_trigger)


class XAnchor(XLayout, kv.AnchorLayout):
    """AnchorLayout.

    See class documentation for details.
    """

    def __init__(self, pad: bool = False, **kwargs):
        """Initialize the class.

        Args:
            pad: Add the default padding. Overriden by explicit `padding` in kwargs.
            kwargs: Keyword arguments for the XAnchor.
        """
        if pad:
            kwargs = dict(padding=DEFAULT_SPACING) | kwargs
        super().__init__(**kwargs)

    @classmethod
    def wrap_pad(cls, widget: kv.Widget, /, **kwargs) -> "XAnchor":
        """Wrap a widget in a padded XAnchor layout.

        ```python3
        padded = kx.wrap(widget)
        normal_anchor = kx.wrap(widget, pad=False)
        custom_padding = kx.wrap(widget, padding="20dp")
        ```
        """
        kwargs = dict(pad=True) | kwargs
        instance = cls(**kwargs)
        instance.add_widget(widget)
        return instance


class XDynamic(XDynamicLayoutMixin, XAnchor):
    """XAnchor that will dynamically resize to first child widget's size.

    Can also add `margin`.
    """

    dynamic = kv.BooleanProperty(True)
    """If layout should resize to match first child. Defaults to True."""
    margins = kv.VariableListProperty(defaultvalue=0, length=4)
    """Margins (like `Anchor.padding`)."""

    def __init__(self, margin: bool = False, **kwargs):
        """Initialize the class.

        Args:
            margin: Add the default margin. Overriden by explicit `margins` in kwargs.
            kwargs: Keyword arguments for the XDynamic.
        """
        if margin is True:
            kwargs = dict(margins=DEFAULT_SPACING) | kwargs
        super().__init__(**kwargs)
        self._trigger_layout()
        self.bind(dynamic=self._on_dynamic)

    def do_layout(self, *args, **kwargs):
        """Resize to first child's size plus margins."""
        if self.dynamic:
            self._update_dynamic_size()
        super().do_layout(*args, **kwargs)

    def _on_dynamic(self, *args):
        if self.dynamic:
            self._update_dynamic_size()
        else:
            self.set_size(hx=1, hy=1)

    def _update_dynamic_size(self):
        if not self.children:
            return
        child = self.children[0]
        pix = util.to_pixels
        margin_left, margin_top, margin_right, margin_bottom = self.margins
        if not child.size_hint_x:
            self.set_size(x=pix(child.width) + pix(margin_left) + pix(margin_right))
        if not child.size_hint_y:
            self.set_size(y=pix(child.height) + pix(margin_top) + pix(margin_bottom))


class XFrame(XThemed, XDynamic):
    """Themed `XDynamic` with optional background and frame.

    See class documentation for details.
    """

    _source_bg = str(assets.get_image("rounded_square"))
    _source_frame = str(assets.get_image("frame"))
    _frame_width = util.to_pixels("4dp")

    bg = kv.BooleanProperty(True)
    """If background should be drawn. Defaults to True."""
    frame = kv.BooleanProperty(True)
    """If frame should be drawn. Defaults to True."""

    def __init__(self, **kwargs):
        """Initialize the class."""
        super().__init__(**kwargs)
        self._make_graphics()
        self.bind(bg=self._refresh_graphics, frame=self._refresh_graphics)

    @classmethod
    def wrap_frame(cls, widget: kv.Widget, /, **kwargs) -> "XFrame":
        """Wrap a widget in an XFrame.

        ```python3
        # Center widget in a frame with background color:
        bg_frame = kx.frame(widget, bg=True)
        # Center widget in a frame with padding:
        padded_frame = kx.frame(widget, pad=True)
        # Add a frame to a widget of fixed size:
        dynamic_frame = kx.frame(widget, dynamic=True)
        # Add margin to dynamic frame:
        margin_frame = kx.frame(widget, dynamic=True, margin=True)
        custom_margins = kx.frame(widget, dynamic=True, margins="20dp")
        ```
        """
        dynamic = kwargs.get("dynamic", False)
        kwargs = dict(
            dynamic=dynamic,
            pad=not dynamic,
            margin=dynamic,
            bg=False,
            frame=True,
        ) | kwargs
        instance = cls(**kwargs)
        instance.add_widget(widget)
        return instance

    def on_subtheme(self, subtheme):
        """Apply colors."""
        self._refresh_graphics()

    def _refresh_graphics(self, *args):
        bg_color = self.subtheme.bg if self.bg else XColor(a=0)
        frame_color = self.subtheme.accent if self.frame else XColor(a=0)
        self._bg_color.rgba = bg_color.rgba
        self._frame_color.rgba = frame_color.rgba

    def _make_graphics(self):
        with self.canvas.before:
            self._bg_color = kv.Color()
            self._bg_image = kv.BorderImage(source=str(self._source_bg))
            self._frame_color = kv.Color()
            self._frame_image = kv.BorderImage(source=str(self._source_frame))
        self.bind(
            pos=self._update_graphics_geometry,
            size=self._update_graphics_geometry,
        )
        self._refresh_graphics()

    def _update_graphics_geometry(self, *args):
        pix = util.to_pixels
        fw = self._frame_width
        self._bg_image.pos = pix(self.pos)
        self._bg_image.size = pix(self.size)
        left, top, right, bottom = self.margins if self.dynamic else self.padding
        x = self.x + pix(left) - fw
        y = self.y + pix(bottom) - fw
        w = self.width - pix(left) - pix(right) + fw + fw
        h = self.height - pix(top) - pix(bottom) + fw + fw
        self._frame_image.pos = max(x, 0), max(y, 0)
        self._frame_image.size = max(w, 0), max(h, 0)


class XJustify(XDynamicLayoutMixin, XAnchor):
    """XAnchor that will resize to justify a widget of fixed size.

    See class documentation for details.
    """

    orientation = kv.OptionProperty("horizontal", options=["horizontal", "vertical"])
    """Axis to justify."""

    @classmethod
    def wrap_justify(cls, widget: kv.Widget, /, **kwargs) -> "XJustify":
        """Wrap a widget in an XJustify layout.

        ```python3
        # Label of fixed size (200 width by 50 height)
        label = kx.XLabel(ssx=200, ssy=50)
        # Layout that will resize to label's height (with `size_hint_x` of 1)
        justified_label_frame = kx.justify(label, orientation="horizontal")  # 50 height
        ```

        .. note::
            Child widget must not have `size_hint` set along the specified axis in
            `orientation` (only considers the first child).
        """
        instance = cls(**kwargs)
        instance.add_widget(widget)
        return instance

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


class XBox(XLayout, kv.BoxLayout):
    """BoyLayout."""

    pass


class XDynamicBox(XDynamicLayoutMixin, XBox):
    """XBox that will dynamically resize based on orientation and children's size.

    When vertical, height will be adjusted to fit children exactly. When horizontal,
    width will be adjusted to fit children exactly. If `both_axes` is True, will also
    adjust the other axis based on maximum size of children widgets.

    .. warning::
        Layout behavior will break if children's size hint is set on an axis that is
        responsive (based on `orientation` and `both_axes`).
    """

    both_axes = kv.BooleanProperty(False)
    """If layout should be responsive on both axes."""

    def do_layout(self, *args, **kwargs):
        """Resize based on children, before doing layout."""
        if self.orientation == "horizontal":
            width = sum(util.to_pixels(c.width) for c in self.children)
            self.set_size(x=width)
            if self.both_axes:
                heights = tuple(
                    util.to_pixels(c.height) for c in self.children
                    if c.size_hint_y is None
                )
                if heights:
                    self.set_size(y=max(heights))
        elif self.orientation == "vertical":
            height = sum(util.to_pixels(c.height) for c in self.children)
            self.set_size(y=height)
            if self.both_axes:
                widths = tuple(
                    util.to_pixels(c.width) for c in self.children
                    if c.size_hint_x is None
                )
                if widths:
                    self.set_size(x=max(widths))
        super().do_layout(*args, **kwargs)


class XGrid(XLayout, kv.GridLayout):
    """GridLayout."""

    pass


class XStack(XLayout, kv.StackLayout):
    """StackLayout."""

    pass


class XRelative(XLayout, kv.RelativeLayout):
    """RelativeLayout."""

    pass


pad = XAnchor.wrap_pad
frame = XFrame.wrap_frame
justify = XJustify.wrap_justify


__all__ = (
    "pad",
    "frame",
    "justify",
    "XAnchor",
    "XDynamic",
    "XFrame",
    "XJustify",
    "XAnchorDelayed",
    "XCurtain",
    "XBox",
    "XDynamicBox",
    "XGrid",
    "XRelative",
    "XStack",
    "XLayout",
    "XDynamicLayoutMixin",
    "DEFAULT_SPACING",
)
