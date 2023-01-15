"""Home of `XLabel` and `XLabelClick`."""

from .. import kivy as kv
from ..behaviors import XThemed
from .widget import XWidget


class XLabel(XThemed, XWidget, kv.Label):
    """Label."""

    def __init__(self, fixed_width: bool = False, fixed_height: bool = False, **kwargs):
        """Initialize the class.

        Args:
            fixed_width: Adjust the height of the label while maintaining width.
            fixed_height: Adjust the width of the label while maintaining height.
        """
        kwargs = {
            "markup": True,
            "halign": "center",
            "valign": "center",
        } | kwargs
        if fixed_width and fixed_height:
            raise RuntimeError("Must set either fixed_width or fixed_height.")
        super().__init__(**kwargs)
        self._trigger_fix_height = kv.Clock.create_trigger(self._fix_height)
        self._trigger_fix_width = kv.Clock.create_trigger(self._fix_width)
        if fixed_width:
            self.bind(
                size=self._trigger_fix_height,
                text=self._trigger_fix_height,
            )
        elif fixed_height:
            self.bind(
                size=self._trigger_fix_width,
                text=self._trigger_fix_width,
            )
        else:
            self.bind(size=self._on_size)

    def _fix_height(self, *a):
        x = self.size[0]
        hx = self.size_hint[0]
        self.text_size = x, None
        self.texture_update()
        if hx is None:
            self.set_size(x=x, y=self.texture_size[1])
        else:
            self.set_size(hx=hx, y=self.texture_size[1])

    def _fix_width(self, *a):
        y = self.size[1]
        hy = self.size_hint[1]
        self.text_size = None, y
        self.texture_update()
        if hy is None:
            self.set_size(x=self.texture_size[0], y=y)
        else:
            self.set_size(x=self.texture_size[0], hy=hy)

    def _on_size(self, *a):
        self.text_size = self.size

    def on_subtheme(self, subtheme):
        """Override base method."""
        self.color = subtheme.fg.rgba


class XLabelClick(kv.ButtonBehavior, XLabel):
    """Label with ButtonBehavior."""

    pass


__all__ = (
    "XLabel",
    "XLabelClick",
)
