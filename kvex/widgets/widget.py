"""Home of `XWidget`."""

from typing import Optional
from .. import kivy as kv
from ..util import sp2pixels
from ..colors import XColor


class XWidget:
    """A mixin for kivy widgets with useful methods."""

    def add_widgets(
        self,
        *children: tuple[kv.Widget, ...],
        insert_last: bool = False,
        **kwargs,
    ):
        """Add multiple widgets."""
        if not children:
            raise ValueError("Must supply children to add.")
        for child in children:
            if insert_last:
                kwargs["index"] = len(self.children)
            self.add_widget(child, **kwargs)

    def set_size(
        self,
        x: Optional[float | str] = None,
        y: Optional[float | str] = None,
        hx: float = 1,
        hy: float = 1,
    ):
        """Set the size of the widget.

        Designed to produce intuitive results when using size or hint without
        specifying the other.

        Args:
            x: Width in pixels.
            y: Height in pixels.
            hx: Width hint.
            hy: Height hint.
        """
        hx = hx if x is None else None
        hy = hy if y is None else None
        x = self.width if x is None else x
        y = self.height if y is None else y
        self.size_hint = hx, hy
        self.size = x, y

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
