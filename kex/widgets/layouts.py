"""Layout widgets."""

from typing import Literal
from .. import kivy as kv
from . import XMixin


class XBox(XMixin, kv.BoxLayout):
    """BoyLayout."""

    pass


class XZBox(XMixin, kv.GridLayout):
    """Behaves like a Box where widgets are drawn in reverse order."""

    def __init__(
        self,
        orientation: Literal["horizontal", "vertical"] = "horizontal",
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
            raise ValueError(
                'FlipZIndex orientation must be "horizontal" or "vertical"'
            )
        super().__init__(**kwargs)

    def add_widget(self, *args, **kwargs):
        """Overrides base method to insert correctly."""
        kwargs["insert_last"] = True
        super().add_widget(*args, **kwargs)


class XDBox(XMixin, kv.GridLayout):
    """Behaves like a Box that will dynamically resize based on children's height."""

    def __init__(self, cols: int = 1, **kwargs):
        """Initialize the class."""
        super().__init__(cols=cols, **kwargs)
        self.bind(children=self._resize)

    def add_widget(self, w, *args, **kwargs):
        """Overrides XMixin `add` in order to bind to size changes."""
        w.bind(size=self._resize)
        super().add_widget(w, *args, **kwargs)
        kv.Clock.schedule_once(self._resize, 0)

    def _resize(self, *a):
        self.set_size(hx=1, y=sum([c.height for c in self.children]))


class XGrid(XMixin, kv.GridLayout):
    """GridLayout."""

    pass


class XStack(XMixin, kv.StackLayout):
    """StackLayout."""

    pass


class XRelative(XMixin, kv.RelativeLayout):
    """RelativeLayout."""

    pass


class XAnchor(XMixin, kv.AnchorLayout):
    """AnchorLayout."""

    @classmethod
    def wrap(
        cls,
        w: kv.Widget,
        padding_weight: tuple[float, float] = (0.95, 0.95),
        **kwargs,
    ):
        padding_anchor = cls()
        padding_anchor.set_size(hx=padding_weight[0], hy=padding_weight[1])
        padding_anchor.add_widget(w)
        anchor = cls(**kwargs)
        anchor.add_widget(padding_anchor)
        return anchor


Direction = Literal["vertical", "horizontal"]


class XScroll(XMixin, kv.ScrollView):
    """ScrollView."""

    def __init__(
        self,
        view: XMixin,
        scroll_dir: Direction = "vertical",
        scroll_amount: float = 50,
        **kwargs,
    ):
        """Initialize the class.

        Args:
            view: A widget to put in the scroll view.
            scroll_dir: Direction of scroll: "horizontal" or "vertical"
            scroll_amount: Resolution of scroll in pixels.
        """
        super().__init__(**kwargs)
        self.scroll_dir = scroll_dir
        self.scroll_amount = scroll_amount
        self.bar_width = 15
        self.scroll_type = ["bars"]
        self.view = self.add_widget(view)
        self.bind(size=self._on_size, on_touch_down=self._on_touch_down)
        self.view.bind(size=self._on_size)

    @property
    def scroll_dir(self):
        """Scrolling direction."""
        return self.__scroll_dir

    @scroll_dir.setter
    def scroll_dir(self, v: Direction):
        """Set the scrolling direction"""
        self.__scroll_dir = v
        self.do_scroll_x = v == "horizontal"
        self.do_scroll_y = v == "vertical"

    def _on_size(self, *a):
        self.do_scroll_x = (
            self.view.size[0] > self.size[0] and self.scroll_dir == "horizontal"
        )
        self.do_scroll_y = (
            self.view.size[1] > self.size[1] and self.scroll_dir == "vertical"
        )
        if self.size[0] >= self.view.size[0]:
            self.scroll_x = 1
        if self.size[1] >= self.view.size[1]:
            self.scroll_y = 1

    def _on_touch_down(self, w, m):
        if m.button not in {"scrollup", "scrolldown"}:
            return False
        if not self.collide_point(*m.pos):
            return False
        return self.do_scroll(m.button != "scrollup")

    def do_scroll(self, count: int = 1, /, *, up: bool = False):
        """Scroll down or up by count times self.scroll_amount."""
        if not any((self.do_scroll_x, self.do_scroll_y)):
            return False
        dir = 1 if up else -1
        pixels_x, pixels_y = self.convert_distance_to_scroll(
            self.scroll_amount * count,
            self.scroll_amount * count,
        )
        if self.scroll_dir == "horizontal":
            self.scroll_x = min(1, max(0, self.scroll_x + pixels_x * dir))
        elif self.scroll_dir == "vertical":
            self.scroll_y = min(1, max(0, self.scroll_y + pixels_y * dir))
        return True
