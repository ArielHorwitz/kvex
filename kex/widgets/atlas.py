"""A widgets for viewing the textures in the defaulttheme atlas."""

from ..util import from_atlas, XColor
from .layouts import XScroll, XStack, XAnchor, XBox
from .uix import XLabel


class XAtlasPreview(XScroll):
    def __init__(self):
        super().__init__(view=self._get_stack())
        self.on_size()
        self.bind(size=self.on_size)

    def _get_stack(self):
        stack = XStack()
        for item in ATLAS_ITEMS:
            label = XLabel(text=item)
            image = XAnchor()
            image.make_fg(source=from_atlas(item))
            image.set_size(50, 50)
            box = XBox(orientation="vertical")
            box.add_widgets(label, XAnchor.wrap(image))
            frame = XAnchor.wrap(box)
            frame.set_size(100, 125)
            frame.make_bg(XColor(v=0.15), source=from_atlas("textinput_active"))
            stack.add_widget(frame)
        return stack

    def on_size(self, *args):
        self.view.set_size(y=3000)
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
