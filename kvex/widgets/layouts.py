"""Layout widgets."""

from typing import Type, Optional
from .. import kivy as kv
from .. import assets
from .widget import XWidget, XThemed


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

    def add_widget(self, w, *args, **kwargs):
        """Overrides base method in order to bind to size changes."""
        w.bind(size=self._resize)
        super().add_widget(w, *args, **kwargs)
        kv.Clock.schedule_once(self._resize, 0)

    def _resize(self, *a):
        self.set_size(hx=1, y=sum([c.height for c in self.children]))


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
    def wrap(
        cls,
        w: kv.Widget,
        /,
        x: float = 0.95,
        y: float = 0.95,
        *,
        inner_class: Optional[Type["XAnchor"]] = None,
        **kwargs,
    ):
        """Wrap a widget with padding using size hint.

        Args:
            w: Widget to wrap.
            x: Size hint of horizontal padding.
            y: Size hint of vertical padding.
            inner_class: Class to use as inner (padded) anchor. Useful for subclasses.
            kwargs: Keyword arguments for the outer anchor.
        """
        inner_class = inner_class or cls
        inner_anchor = inner_class()
        inner_anchor.set_size(hx=x, hy=y)
        inner_anchor.add_widget(w)
        anchor = cls(**kwargs)
        anchor.add_widget(inner_anchor)
        return anchor


class XTAnchor(XThemed, XAnchor):
    """Themed XAnchor."""

    BG = str(assets.get_image("xtanchor_bg"))

    @classmethod
    def wrap(cls, *args, **kwargs):
        """Overrride base method.

        Uses `XAnchor` as the inner class (to prevent overriding our own background),
        and defualts to no padding.
        """
        kwargs = dict(inner_class=XAnchor, x=1, y=1) | kwargs
        xtanchor = super().wrap(*args, **kwargs)
        return xtanchor

    def on_subtheme(self, subtheme):
        """Override base method."""
        self.make_bg(subtheme.bg, source=self.BG)


class XCurtain(XAnchor):
    """AnchorLayout that can show or hide it's content."""

    content = kv.ObjectProperty(None, allownone=True)
    showing = kv.BooleanProperty(True)
    dynamic = kv.BooleanProperty(False)

    def __init__(self, *args, **kwargs):
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
        self.showing = True

    def hide(self, *args, **kwargs):
        self.showing = False

    def toggle(self, *args, set_as: Optional[bool] = None, **kwargs):
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
    "XTAnchor",
    "XCurtain",
)
