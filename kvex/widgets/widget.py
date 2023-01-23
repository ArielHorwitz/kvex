"""Home of `XWidget`."""

from typing import Optional
from .. import kivy as kv
from ..util import to_pixels
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

    def make_bg(
        self,
        color: Optional[XColor] = None,
        source: Optional[str] = None,
        index: int = 0,
        border: bool = False,
    ):
        """Add or update a background image using `self.canvas.before`.

        Args:
            color: XColor of background.
            source: Texture source of background.
            index: Used as an identifier, allowing to use multiple background images.
            border: Determines type of canvas instruction. If True will use BorderImage
                otherwise uses Rectangle.
        """
        assert index >= 0
        bg_name, color_name = f"_kvex_bg_{index}", f"_kvex_bg_color_{index}"
        if hasattr(self, bg_name) and hasattr(self, color_name):
            if color is not None:
                getattr(self, color_name).rgba = color.rgba
            if source is not None:
                getattr(self, bg_name).source = str(source)
        else:
            if color is None:
                color = XColor(1, 1, 1, 1)
            with self.canvas.before:
                setattr(self, color_name, kv.Color(*color.rgba))
                image_class = kv.BorderImage if border else kv.Rectangle
                bgi = image_class(size=self.size, pos=self.pos, source=str(source))
                setattr(self, bg_name, bgi)
            self.bind(
                pos=lambda w, pos: self._update_kvex_bg_pos(bgi, pos),
                size=lambda w, size: self._update_kvex_bg_size(bgi, size),
            )

    def _update_kvex_bg_pos(self, instruction, pos):
        instruction.pos = to_pixels(pos)

    def _update_kvex_bg_size(self, instruction, size):
        instruction.size = to_pixels(size)

    @property
    def app(self):
        """Get the running app."""
        return kv.App.get_running_app()


__all__ = (
    "XWidget",
)
