"""List widget."""

from typing import Optional
from .. import kivy as kv
from ..util import text_texture, from_atlas
from ..colors import XColor
from ..behaviors import XThemed, XFocusBehavior
from .layouts import XRelative


SELECTION_SOURCE = from_atlas("vkeyboard_background")
SELECTION_ALPHA = 0.5, 1  # When focus is False, True respectively
EMPTY_TEXTURE = text_texture(" ")

# Cache setup
kv.Cache.register("XList")
cache_append = kv.Cache.append
cache_get = kv.Cache.get
cache_remove = kv.Cache.remove


class XList(XThemed, XFocusBehavior, XRelative):
    """Text list widget."""

    font_name = kv.StringProperty("Roboto")
    """Text font."""
    font_size = kv.NumericProperty(16)
    """Text font size."""
    item_height = kv.NumericProperty(35)
    """Item height size."""
    item_padding = kv.ListProperty([10, 5])
    """Item padding."""
    items = kv.ListProperty()
    """Items in list."""
    selection = kv.NumericProperty(0)
    """Currently selected item index."""
    paging_size = kv.NumericProperty(None)
    """Number of items to move when paging (e.g. page up/down)."""
    scroll_width = kv.NumericProperty(5)
    """Scroll bar width."""
    scroll_color = kv.ColorProperty([0.5, 0.5, 0.5, 0.5])
    """Scroll bar color."""
    shorten = kv.BooleanProperty(True)
    """Like `Label.shorten`."""
    shorten_from = kv.StringProperty("center")
    """Like `Label.shorten_from`."""
    bg_color = kv.ColorProperty([0, 0, 0, 0])
    """Widget background."""
    text_color = kv.ColorProperty()
    """Text color."""
    selection_color = kv.ColorProperty([1, 1, 1, 0.5])
    """Selection highlighting color."""
    enable_shifting = kv.BooleanProperty(False)
    """Enable changing the order of items."""
    invoke_double_tap_only = kv.BooleanProperty(True)
    """Only invoke items when double clicking."""
    _label_kwargs = kv.DictProperty()

    def __init__(self, **kwargs):
        """See class documentation for details."""
        super().__init__(**kwargs)
        self._rects = []
        self._scroll = 0
        self.items = self.items or ["placeholder"]
        self._refresh_label_kwargs()
        self._create_other_graphics()
        self._refresh_graphics()
        self._refresh_selection_graphics()
        self.register_event_type("on_invoke")
        self.bind(
            focus=self._refresh_colors,
            items=self._on_items,
            scroll=self._on_scroll,
            size=self._on_geometry,
            pos=self._on_geometry,
            selection=self._on_selection,
            bg_color=self._refresh_colors,
            text_color=self._refresh_label_kwargs,
            selection_color=self._refresh_colors,
            scroll_color=self._refresh_colors,
            item_height=self._refresh_label_kwargs,
            item_padding=self._refresh_label_kwargs,
            font_name=self._refresh_label_kwargs,
            font_size=self._refresh_label_kwargs,
            shorten=self._refresh_label_kwargs,
            shorten_from=self._refresh_label_kwargs,
            _label_kwargs=self._on_label_kwargs,
        )

    def _on_items(self, w, items):
        assert len(self.items) > 0
        self.select()
        self._refresh_items()
        self._refresh_scroll_indicator()

    def _on_scroll(self, *args):
        self._refresh_items()
        self._refresh_scroll_indicator()

    def select(self, index: Optional[int] = None, /, *, delta: int = 0):
        """Select an item at index and/or index delta."""
        if index is None:
            index = self.selection
        index += delta
        index = max(0, min(index, len(self.items) - 1))
        self.selection = index

    def set_scroll(self, index: Optional[int] = None, /, *, delta: int = 0):
        """Scroll to item at index and/or index delta."""
        if index is None:
            index = self.scroll
        index += delta
        self.scroll = index

    def on_subtheme(self, subtheme):
        """Apply colors."""
        self.bg_color = subtheme.bg.rgba
        self.text_color = subtheme.fg.rgba
        self.selection_color = subtheme.accent1.modified_alpha(0.5).rgba
        self.scroll_color = subtheme.accent2.modified_alpha(0.5).rgba

    def _on_selection(self, *args):
        self.set_scroll()
        self._refresh_selection_graphics()

    def on_touch_down(self, touch):
        """Handle invoking items."""
        r = super().on_touch_down(touch)
        if not self.collide_point(*touch.pos):
            return r
        disable_invoke = False
        rel_pos = self.to_widget(*touch.pos)
        idx = int((self.height - rel_pos[1]) // self.item_height)
        if idx >= len(self.items):
            idx = len(self.items) - 1
            disable_invoke = True
        self.select(idx)
        if idx == self.selection:
            disable_by_dtap = self.invoke_double_tap_only and not touch.is_double_tap
            if not disable_invoke and not disable_by_dtap:
                self.invoke()
        return True

    def _refresh_selection_graphics(self, *args):
        idx = self.selection
        offset = idx - self.scroll
        self._selection_rect.pos = self._get_rect_pos(offset)
        self._selection_rect.size = self._rects[offset].size

    def _refresh_scroll_indicator(self, *args):
        scroll = self.scroll
        rect_count = len(self._rects)
        item_count = len(self.items)
        widget_height = self.height
        indicator_width = self.scroll_width
        # Find relative scroll of indicator top and bottom edges
        indicator_rel_top = 1 - scroll / item_count
        indicator_rel_height = min(rect_count, item_count) / item_count
        indicator_rel_bot = max(0, indicator_rel_top - indicator_rel_height)
        # Adjust based on widget size
        indicator_height = widget_height * indicator_rel_height
        indicator_y = widget_height * indicator_rel_bot
        indicator_x = self.width - indicator_width
        # Sometimes we are asked to refresh when not all properties have finished
        # updating, let's gracefully handle that by pretending we see the entire list
        broken_geometry = (
            (not 0 <= indicator_rel_bot <= indicator_rel_top <= 1)
            or (not 0 <= indicator_rel_height <= 1)
        )
        if broken_geometry:
            indicator_height = widget_height
            indicator_y = 0
        self._scroll_indicator.pos = indicator_x, indicator_y
        self._scroll_indicator.size = indicator_width, indicator_height

    def _on_geometry(self, *args):
        self._bg.size = self.size
        self._refresh_label_kwargs()
        self._refresh_graphics()

    def _create_other_graphics(self, *args):
        with self.canvas.before:
            self._bg_color = kv.Color(*self.bg_color)
            self._bg = kv.Rectangle(size=(50, 50))
            kv.Color()
            self._selection_rect_color = kv.Color(*self.selection_color)
            self._selection_rect = kv.BorderImage(
                source=SELECTION_SOURCE,
                size=(50, 50),
            )
            self._scroll_indicator_color = kv.Color(*self.scroll_color)
            self._scroll_indicator = kv.Rectangle()
            kv.Color()
        self._refresh_colors()

    def _refresh_colors(self, *args):
        self._bg_color.rgba = XColor(*self.bg_color).rgba
        self._scroll_indicator_color.rgba = XColor(*self.scroll_color).rgba
        selection = XColor(*self.selection_color)
        self._selection_rect_color.rgba = selection.rgba
        self._selection_rect_color.a *= SELECTION_ALPHA[int(self.focus)]

    def _refresh_graphics(self, *args):
        self.canvas.clear()
        height = self.height
        item_height = self.item_height
        rect_count = max(1, int(height / item_height))
        size = self.width, item_height
        self._rects = []
        append = self._rects.append
        with self.canvas:
            for i in range(rect_count):
                pos = self._get_rect_pos(i)
                rect = kv.Rectangle(size=size, pos=pos, texture=EMPTY_TEXTURE)
                append(rect)
        self._refresh_items()
        self._refresh_selection_graphics()
        self._refresh_scroll_indicator()

    def _get_rect_pos(self, idx: int):
        return 0, self.height - (self.item_height * (idx + 1))

    def _refresh_items(self, *args):
        items = self.items
        scroll = self.scroll
        item_count = len(items)
        for i, rect in enumerate(self._rects):
            text = None
            texture = EMPTY_TEXTURE
            idx = i + scroll
            if idx < item_count:
                text = items[idx]
                texture = self._get_texture(text)
            rect.texture = texture

    def _on_label_kwargs(self, w, kwargs):
        cache_remove("XList")
        self._refresh_graphics()

    def _refresh_label_kwargs(self, *args):
        self._label_kwargs = dict(
            font_name=self.font_name,
            font_size=self.font_size,
            text_size=(self.width, self.item_height),
            padding=self.item_padding,
            shorten=self.shorten,
            shorten_from=self.shorten_from,
            color=self.text_color,
            valign="middle",
        )

    def _get_texture(self, text: str):
        texture_id = f"{text}{self._label_kwargs}"
        texture = cache_get("XList", texture_id)
        if texture is None:
            label = kv.CoreMarkupLabel(text=text, **self._label_kwargs)
            label.refresh()
            texture = label.texture
            cache_append("XList", texture_id, texture)
        return texture

    def _get_scroll(self):
        return self._scroll

    def _set_scroll(self, scroll):
        selection = self.selection
        line_count = len(self._rects)
        min_scroll = max(0, selection - line_count + 1)
        max_scroll = min(selection, len(self.items) - line_count)
        new_scroll = max(min_scroll, min(scroll, max_scroll))
        is_new_scroll = new_scroll != self._scroll
        self._scroll = new_scroll
        return is_new_scroll

    scroll = kv.AliasProperty(_get_scroll, _set_scroll)

    def invoke(self, *args, index: Optional[int] = None):
        """Invoke an item (as if it were selected and clicked)."""
        if index is None:
            index = self.selection
        self.dispatch("on_invoke", index, self.items[index])

    def on_invoke(self, index: int, label: str):
        """Triggered when an item was invoked."""
        pass

    def keyboard_on_key_down(self, w, key_pair, text, mods):
        """Handle key presses for navigation and invocation."""
        keycode, key = key_pair
        if key in {"up", "down", "pageup", "pagedown"}:
            self._handle_arrow_key(key, mods)
        elif key.isnumeric():
            try:
                index = int(key)
            except ValueError:
                index = None
            if index is not None:
                self.select(index)
                self.invoke()
        elif key in {"enter", "numpadenter"}:
            self.invoke()
        else:
            return super().keyboard_on_key_down(w, key_pair, text, mods)

    def _handle_arrow_key(self, key, mods):
        mods = set(mods) - {"numpad"}
        is_up = key.endswith("up")
        is_down = key.endswith("down")
        is_paging = key.startswith("page")
        is_ctrl = "ctrl" in mods
        is_shift = "shift" in mods
        item_count = len(self.items)
        paging_size = max(2, self.paging_size or int(len(self._rects) / 2))
        delta = item_count if is_ctrl else paging_size if is_paging else 1
        select = 0
        shift = 0
        if is_up:
            select = -delta
        elif is_down:
            select = delta
        if self.enable_shifting and is_shift:
            shift = select
        self.shift(delta=shift)
        self.select(delta=select)

    def shift(self, delta: int, index: Optional[int] = None):
        """Shift an item at index by delta positions (default to currently selected)."""
        if delta == 0:
            return
        if index is None:
            index = self.selection
        items = list(self.items)
        moving = items.pop(index)
        new_index = index + delta
        new_index = max(0, min(new_index, len(items)))
        items.insert(new_index, moving)
        self.items = items


__all__ = (
    "XList",
)
