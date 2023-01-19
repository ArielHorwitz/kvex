"""Home of `XWidget`."""

from typing import Optional, Iterable
from .. import kivy as kv
from ..util import sp2pixels
from ..colors import XColor


class XWidget:
    """A mixin for kivy widgets with useful methods."""

    def __init__(
        self,
        ssx: Optional[float | str] = None,
        ssy: Optional[float | str] = None,
        sshx: Optional[float] = None,
        sshy: Optional[float] = None,
        **kwargs,
    ):
        """Initialize the class.

        The `ss` args (`ssx`, `sshy`, etc.) are used for calling `ssize_size` during
        initialization.
        """
        super().__init__(**kwargs)
        size_args = ssx, ssy, sshx, sshy
        if any(s is not None for s in size_args):
            self.set_size(*size_args)

    @classmethod
    def with_add(cls, *children: Iterable[kv.Widget], **kwargs) -> "XWidget":
        """Create the widget and add children."""
        instance = cls(**kwargs)
        instance.add_widgets(*children)
        return instance

    def add_widgets(self, *children: Iterable[kv.Widget], **kwargs):
        """Add multiple widgets."""
        if not children:
            raise ValueError("No children given.")
        for child in children:
            if not isinstance(child, kv.Widget):
                raise TypeError(f"Expected widgets only, instead got: {children}")
            self.add_widget(child, **kwargs)

    def set_size(
        self,
        x: Optional[float | str] = None,
        y: Optional[float | str] = None,
        hx: Optional[float] = None,
        hy: Optional[float] = None,
    ):
        """Set the size of the widget.

        Designed to produce intuitive results when using size or hint without
        specifying the other.

        Args:
            x: Width in pixels. If none given, will use size hint.
            y: Height in pixels. If none given, will use size hint.
            hx: Width hint. If none given, will not modify axis.
            hy: Height hint. If none given, will not modify axis.
        """
        if x is not None:
            self.width = x
            self.size_hint_x = None
        elif hx is not None:
            self.size_hint_x = hx
        if y is not None:
            self.height = y
            self.size_hint_y = None
        elif hy is not None:
            self.size_hint_y = hy

    def set_focus(self, *args):
        """Set the focus on this widget."""
        self.focus = True

    def make_bg(self, color: Optional[XColor] = None, source: Optional[str] = None):
        """Add or update a background image using self.canvas.before."""
        if hasattr(self, "_kvex_bg") and hasattr(self, "_kvex_bg_color"):
            if color is not None:
                self._kvex_bg_color.rgba = color.rgba
            if source is not None:
                self._kvex_bg.source = str(source)
        else:
            if color is None:
                color = XColor(1, 1, 1, 1)
            with self.canvas.before:
                self._kvex_bg_color = kv.Color(*color.rgba)
                self._kvex_bg = kv.Rectangle(
                    size=self.size,
                    pos=self.pos,
                    source=str(source),
                )
            self.bind(pos=self._update_kvex_bg_pos, size=self._update_kvex_bg_size)

    def _update_kvex_bg_pos(self, w, pos):
        self._kvex_bg.pos = pos

    def _update_kvex_bg_size(self, w, size):
        self._kvex_bg.size = sp2pixels(size)

    @property
    def app(self):
        """Get the running app."""
        return kv.App.get_running_app()


__all__ = (
    "XWidget",
)
