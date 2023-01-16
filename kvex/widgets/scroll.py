"""Home of `XScroll`."""

from .. import kivy as kv
from ..behaviors import XThemed
from .widget import XWidget


class XScroll(XThemed, XWidget, kv.ScrollView):
    """ScrollView."""

    reset_scroll_value = kv.NumericProperty(1, allownone=True)

    def __init__(
        self,
        view: kv.Widget,
        scroll_amount: float = 50,
        **kwargs,
    ):
        """Initialize the class.

        Args:
            view: A widget to put in the scroll view.
            scroll_amount: Resolution of scroll in pixels.
        """
        kwargs = dict(bar_width="10sp") | kwargs
        super().__init__(**kwargs)
        self.scroll_amount = scroll_amount
        self.scroll_type = ["bars"]
        self.view = view
        self.add_widget(view)
        self.bind(size=self._on_size, on_touch_down=self._on_touch_down)
        self.view.bind(size=self._on_size)
        self._on_size()

    def on_subtheme(self, subtheme):
        """Apply colors."""
        self.bar_color = subtheme.accent2.rgba
        self.bar_inactive_color = subtheme.accent1.rgba

    def reset_scroll(self, *, scroll: float = 1):
        """Reset scroll to the top left."""
        self.scroll_x = self.scroll_y = scroll

    def _on_size(self, *a):
        self.do_scroll_x = self.view.width > self.width
        self.do_scroll_y = self.view.height > self.height
        if self.reset_scroll_value is not None:
            self.reset_scroll(scroll=self.reset_scroll_value)

    def _on_touch_down(self, w, m):
        if m.button not in {"scrollup", "scrolldown"}:
            return False
        if not self.collide_point(*m.pos):
            return False
        return self.do_scroll(up=m.button != "scrollup")

    def do_scroll(self, count: int = 1, /, *, up: bool = False):
        """Scroll down or up by count times self.scroll_amount."""
        if not any((self.do_scroll_x, self.do_scroll_y)):
            return False
        dir = 1 if up else -1
        pixels_x, pixels_y = self.convert_distance_to_scroll(
            self.scroll_amount * count,
            self.scroll_amount * count,
        )
        self.scroll_x = min(1, max(0, self.scroll_x + pixels_x * dir))
        self.scroll_y = min(1, max(0, self.scroll_y + pixels_y * dir))
        return True


__all__ = (
    "XScroll",
)
