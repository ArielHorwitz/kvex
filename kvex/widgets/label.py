"""Home of `XLabel` and `XLabelClick`."""

from .. import kivy as kv
from .widget import XWidget


class XLabel(XWidget, kv.Label):
    """Label."""

    def __init__(self, fixed_width: bool = False, **kwargs):
        """Initialize the class.

        Args:
            fixed_width: Adjust the height of the label while maintaining width.
        """
        kwargs = {
            "markup": True,
            "halign": "center",
            "valign": "center",
        } | kwargs
        super().__init__(**kwargs)
        self._trigger_fix_height = kv.Clock.create_trigger(self._fix_height)
        if fixed_width:
            self.bind(
                size=self._trigger_fix_height,
                text=self._trigger_fix_height,
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

    def _on_size(self, *a):
        self.text_size = self.size


class XLabelClick(kv.ButtonBehavior, XLabel):
    """Label with ButtonBehavior."""

    pass


__all__ = (
    "XLabel",
    "XLabelClick",
)
