"""Home of `ThemeManager` and `ThemeSelector`."""

from .. import kivy as kv
from ..colors import XColor, THEMES
from .label import XLabel
from .layouts import XBox, XAnchor
from .scroll import XScroll
from .spinner import XSpinner


class XThemeSelector(XSpinner):
    """A button for selecting the app's theme."""

    def __init__(self):
        """Initialize the class."""
        super().__init__(
            text=self.app.theme_name,
            values=list(THEMES.keys()),
            text_autoupdate=True,
        )
        self.set_size(y="50dp")
        self.bind(text=self._on_select)
        self.app.bind(theme=self._on_app_theme)

    def _on_app_theme(self, *args):
        self.text = self.app.theme_name

    def _on_select(self, *args):
        self.app.set_theme(self.text)


class XThemeManager(XAnchor):
    """See module documentation for details."""

    def __init__(self):
        """See module documentation for details."""
        super().__init__()
        scroll_view = XBox(orientation="vertical")
        for i, (theme_name, theme) in enumerate(THEMES.items()):
            box = _ThemePreview(i, theme_name, theme)
            scroll_view.add_widget(box)
        scroll_view.set_size(y=250*len(THEMES))
        scroll = XScroll(
            view=scroll_view,
            kvex_theme=False,
            bar_color=(0, 0, 0, 0),
            bar_inactive_color=(0, 0, 0, 0),
        )
        scroll.make_bg(XColor(0.5, 0.5, 0.5))
        box = XBox(orientation="vertical")
        box.add_widgets(XThemeSelector(), scroll)
        self.add_widget(box)


class _ThemePreview(kv.ButtonBehavior, XBox):
    def __init__(self, idx, theme_name, theme):
        self.theme_name = theme_name
        super().__init__(orientation="vertical")
        palette = XBox()
        for c in theme.palette:
            pb = XAnchor()
            pb.make_bg(c)
            palette.add_widget(pb)
        theme_lbl = XLabel(
            text=f"{idx+1}. {theme_name}",
            font_size=24,
            kvex_theme=False,
            outline_color=(1, 1, 1),
            outline_width=1.5,
            color=(0, 0, 0),
        )
        title = XAnchor.wrap(palette, padding=(0, "5dp", 0, 0))
        title.add_widget(theme_lbl)
        title.set_size(y=50)
        primary = self._get_subtheme_frame(
            theme_name.capitalize(),
            36,
            theme.primary,
        )
        primary.set_size(hy=2)
        secondary = self._get_subtheme_frame("Secondary", 24, theme.secondary)
        secondary.set_size(hx=3)
        accent = self._get_subtheme_frame("Accent", 16, theme.accent)
        right_frame = XBox()
        right_frame.add_widgets(secondary, accent)
        outer_frame = XBox(orientation="vertical")
        outer_frame.add_widgets(primary, right_frame)
        self.add_widgets(
            title,
            outer_frame,
        )

    def _get_subtheme_frame(self, text, size, subtheme):
        acc1 = subtheme.accent1.markup(f"[size={int(size*1.5)}]»[/size]")
        acc2 = subtheme.accent2.markup("•")
        lbl = XLabel(
            text=f"{acc2}{acc1} {text}",
            color=subtheme.fg.rgba,
            kvex_theme=False,
            font_size=size,
        )
        lbl.make_bg(subtheme.bg)
        return lbl

    def on_press(self, *args):
        self.app.set_theme(self.theme_name)


__all__ = (
    "XThemeManager",
    "XThemeSelector",
)
