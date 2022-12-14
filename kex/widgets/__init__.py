"""Custom Kex widgets."""

from typing import Optional, Literal, Union
from .. import kivy as kv
from ..util import XColor


class XMixin:
    """A mixin for kivy widgets with useful methods."""

    def add(
        self,
        *children: tuple[kv.Widget, ...],
        insert_last: bool = False,
        **kwargs,
    ):
        """Replacement for kivy's `add_widget` method.

        Args:
            children: Children to be added to the widget.
            insert_last: If children should be added below all other children.
                Overwrites the "index" argument from kwargs.
            kwargs: Keyword arguments for kivy's `add_widget`.
        """
        if not children:
            raise ValueError("Must supply children to add.")
        if insert_last:
            kwargs["index"] = len(self.children)
        for child in children:
            self.add_widget(child, **kwargs)

    def set_size(
        self,
        x: Optional[float] = None,
        y: Optional[float] = None,
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
            yx: Height hint.
        """
        hx = hx if x is None else None
        hy = hy if y is None else None
        x = self.width if x is None else x
        y = self.height if y is None else y
        self.size_hint = hx, hy
        self.size = int(x), int(y)

    def set_position(self, x: float, y: float):
        """Set the x, y position of the widget."""
        self.pos = int(x), int(y)

    def set_focus(self, *args):
        """Set the focus on this widget."""
        self.focus = True

    def make_bg(self, color: Optional[XColor] = None, source: Optional[str] = None):
        """Add or update a background image using self.canvas.before."""
        self._set_image("_bg", color, source)

    def make_fg(self, color: Optional[XColor] = None, source: Optional[str] = None):
        """Add or update a foreground image using self.canvas.after."""
        self._set_image("_fg", color, source)

    def _get_image(
        self,
        attribute_name: Literal["_bg", "_fg"],
    ) -> Union[tuple[kv.Rectangle, kv.Color], tuple[None, None]]:
        """Get the background/foreground of the widget."""
        attribute_name_color = f"{attribute_name}_color"
        if not hasattr(self, attribute_name) or not hasattr(self, attribute_name_color):
            return None, None
        image = getattr(self, attribute_name)
        color = getattr(self, attribute_name_color)
        assert isinstance(image, kv.Rectangle)
        assert isinstance(color, kv.Color)
        return image, color

    def _set_image(
        self,
        attribute_name: Literal["_bg", "_fg"],
        color: Optional[XColor],
        source: Optional[str],
    ):
        """Set the background/foreground of the widget."""
        is_bg = attribute_name == "_bg"
        if color is None:
            color = XColor(0.1, 0.1, 0.1, 1) if is_bg else XColor(1, 1, 1, 1)
        image, color_instruction = self._get_image(attribute_name)
        if image:
            color_instruction.rgba = color.rgba
            image.source = source
        else:
            canvas = self.canvas.before if is_bg else self.canvas.after
            with canvas:
                color_instruction = kv.Color(*color.rgba)
                image = kv.Rectangle(size=self.size, pos=self.pos, source=source)
            setattr(self, f"{attribute_name}_color", color_instruction)
            setattr(self, attribute_name, image)
            update_func = self._update_bg if is_bg else self._update_fg
            self.bind(pos=update_func, size=update_func)

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _update_fg(self, *args):
        self._fg.pos = self.pos
        self._fg.size = self.size

    @property
    def app(self):
        """Get the running app."""
        return kv.App.get_running_app()


class XWidget(XMixin, kv.Widget):
    """Kivy Widget with XMixin"""
    pass
