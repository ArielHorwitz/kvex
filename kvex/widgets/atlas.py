"""A widgets for viewing the textures in the defaulttheme atlas."""

from ..util import from_atlas
from .layouts import XStack, XAnchor, XFrame, XBox
from .scroll import XScroll
from .label import XLabel


class XAtlasPreview(XScroll):
    """Widget to preview kivy defaulttheme atlas."""

    def __init__(self, image_width: float = 100, image_height: float = 100):
        """Initialize the class."""
        self._image_width = image_width
        self._image_height = image_height
        super().__init__(view=self._get_stack())
        self.on_size()
        self.bind(size=self.on_size)
        self.register_event_type("on_item")

    def on_touch_down(self, touch):
        """Override base method."""
        consumed = super().on_touch_down(touch)
        if consumed:
            return consumed
        if touch.button != "left":
            return False
        if not self.collide_point(*touch.pos):
            return False
        for name, w in self._widgets.items():
            if w.collide_point(*w.to_widget(*touch.pos)):
                self.dispatch("on_item", name)
                return True
        return False

    def on_item(self, item: str):
        """Dispatched when one of the atlas items has been clicked."""
        print(f"Atlas item: {item!r}")

    def _get_stack(self):
        self._widgets = dict()
        stack = XStack()
        for item in ATLAS_ITEMS:
            label = XLabel(text=item, kvex_theme=False)
            label.set_size(hy=0.5)
            image = XAnchor()
            image.make_fg(source=from_atlas(item))
            image.set_size(self._image_width, self._image_height)
            box = XBox(orientation="vertical")
            box.add_widgets(label, XAnchor.wrap(image, padding=10))
            frame = XFrame.wrap(box)
            frame.set_size(image.width + 20, image.height * 2)
            # frame.make_bg(
            #     XColor.from_name("grey"),
            #     source=from_atlas("textinput_active"),
            # )
            stack.add_widget(frame)
            self._widgets[item] = frame
        return stack

    def on_size(self, *args):
        """Adjust view size based on our width and images size."""
        per_row = max(1, self.width // (self._image_width * 1.2))
        row_count = len(self._widgets) // per_row + 1
        self.view.set_size(y=2*self._image_height*row_count)
        self.scroll_y = 1


ATLAS_ITEMS = (
    "action_bar",
    "action_group",
    "action_group_disabled",
    "action_group_down",
    "action_item",
    "action_item_down",
    "action_view",
    "audio-volume-high",
    "audio-volume-low",
    "audio-volume-medium",
    "audio-volume-muted",
    "bubble",
    "bubble_arrow",
    "bubble_btn",
    "bubble_btn_pressed",
    "button",
    "button_disabled",
    "button_disabled_pressed",
    "button_pressed",
    "checkbox_disabled_off",
    "checkbox_disabled_on",
    "checkbox_off",
    "checkbox_on",
    "checkbox_radio_disabled_off",
    "checkbox_radio_disabled_on",
    "checkbox_radio_off",
    "checkbox_radio_on",
    "close",
    "filechooser_file",
    "filechooser_folder",
    "filechooser_selected",
    "image-missing",
    "media-playback-pause",
    "media-playback-start",
    "media-playback-stop",
    "modalview-background",
    "overflow",
    "player-background",
    "player-play-overlay",
    "previous_normal",
    "progressbar",
    "progressbar_background",
    "ring",
    "selector_left",
    "selector_middle",
    "selector_right",
    "separator",
    "slider_cursor",
    "slider_cursor_disabled",
    "sliderh_background",
    "sliderh_background_disabled",
    "sliderv_background",
    "sliderv_background_disabled",
    "spinner",
    "spinner_disabled",
    "spinner_pressed",
    "splitter",
    "splitter_disabled",
    "splitter_disabled_down",
    "splitter_disabled_down_h",
    "splitter_disabled_h",
    "splitter_down",
    "splitter_down_h",
    "splitter_grip",
    "splitter_grip_h",
    "splitter_h",
    "switch-background",
    "switch-background_disabled",
    "switch-button",
    "switch-button_disabled",
    "tab",
    "tab_btn",
    "tab_btn_disabled",
    "tab_btn_disabled_pressed",
    "tab_btn_pressed",
    "tab_disabled",
    "textinput",
    "textinput_active",
    "textinput_disabled",
    "textinput_disabled_active",
    "tree_closed",
    "tree_opened",
    "vkeyboard_background",
    "vkeyboard_disabled_background",
    "vkeyboard_disabled_key_down",
    "vkeyboard_disabled_key_normal",
    "vkeyboard_key_down",
    "vkeyboard_key_normal",
)


__all__ = (
    "XAtlasPreview",
)
