"""Home of `ThemeManager` and `ThemeSelector`."""

from .. import kivy as kv
from ..colors import XColor, THEMES
from .label import XLabel
from .layouts import XBox, XAnchor
from .scroll import XScroll
from .spinner import XSpinner, XSpinnerOption


class XThemeSelector(XSpinner):
    """A button for selecting the app's theme."""

    def __init__(self, **kwargs):
        """Initialize the class."""
        super().__init__(
            text=self.app.theme_name,
            values=list(THEMES.keys()),
            text_autoupdate=True,
            **kwargs,
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
        scroll_view = XBox(orientation="vertical", padding=("10sp", 0))
        for i, (theme_name, theme) in enumerate(THEMES.items()):
            box = _ThemePreview(i, theme_name, theme)
            scroll_view.add_widget(box)
        scroll_view.set_size(y=f"{175*len(THEMES)}sp")
        scroll = XScroll(
            view=scroll_view,
            kvex_theme=False,
            bar_color=(0, 0, 0, 0),
            bar_inactive_color=(0, 0, 0, 0),
        )
        scroll.make_bg(XColor(0.5, 0.5, 0.5))
        box = XBox(orientation="vertical")
        box.add_widgets(XThemeSelector(option_cls=self._spinner_factory), scroll)
        self.add_widget(box)

    def _spinner_factory(self, *args, **kwargs):
        return XSpinnerOption(*args, subtheme_name="secondary", **kwargs)


class _ThemePreview(kv.ButtonBehavior, XBox):
    def __init__(self, idx, theme_name, theme):
        self.theme_name = theme_name
        super().__init__(orientation="vertical", padding=(0, "5dp"))
        theme_lbl = XLabel(
            text=f"{idx+1}. {theme_name}",
            font_size="24sp",
            kvex_theme=False,
            outline_color=(1, 1, 1),
            outline_width=1.5,
            color=(0, 0, 0),
        )
        palette = XBox()
        for c in theme.palette:
            pb = XAnchor()
            pb.make_bg(c)
            palette.add_widget(pb)
        palette_frame = XAnchor.wrap(palette)
        palette_frame.add_widget(theme_lbl)
        palette_frame.set_size(y=50)
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
            outer_frame,
            palette_frame,
        )

    def _get_subtheme_frame(self, text, size, subtheme):
        acc1 = subtheme.accent1.markup(f"[size={size}sp]»[/size]")
        acc2 = subtheme.accent2.markup(f"[size={size*2/3}sp]•[/size]")
        lbl = XLabel(
            text=f"{acc2}{acc1} {text}",
            color=subtheme.fg.rgba,
            kvex_theme=False,
            font_size=f"{size}sp",
        )
        lbl.make_bg(subtheme.bg)
        return lbl

    def on_press(self, *args):
        self.app.set_theme(self.theme_name)


__all__ = (
    "XThemeManager",
    "XThemeSelector",
)
