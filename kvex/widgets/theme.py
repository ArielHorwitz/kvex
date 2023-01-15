"""Home of `ThemeManager` and `ThemeSelector`."""

from .. import kivy as kv
from ..colors import THEME_NAMES
from .label import XLabel
from .layouts import XBox, XDBox, XAnchor, XFrame
from .scroll import XScroll
from .spinner import XSpinner, XSpinnerOption


class XThemeSelector(XSpinner):
    """A button for selecting the app's theme."""

    def __init__(self, **kwargs):
        """Initialize the class."""
        kwargs = dict(option_cls=self._spinner_factory) | kwargs
        super().__init__(
            text=self.app.theme_name,
            values=THEME_NAMES,
            text_autoupdate=True,
            **kwargs,
        )
        self.set_size(y="50dp")
        self.bind(text=self._on_select)
        self.app.bind(on_theme=self._on_app_theme)

    def _on_app_theme(self, *args):
        self.text = self.app.theme_name

    def _on_select(self, *args):
        self.app.set_theme(self.text)

    def _spinner_factory(self, *args, **kwargs):
        return XSpinnerOption(*args, subtheme_name="secondary", **kwargs)


class XThemePreview(kv.FocusBehavior, XBox):
    """Widget to preview the current theme."""

    def __init__(self):
        """Initialize the class."""
        self._palette_box = XBox()
        self._title_label = XLabel(
            font_size="24sp",
            color=(0, 0, 0),
            outline_color=(1, 1, 1),
            outline_width=2,
            valign="top",
            enable_theming=False,
        )
        super().__init__(orientation="vertical")
        self._make_widgets()
        self.app.bind(on_theme=self._refresh_palette_box)

    def keyboard_on_key_down(self, w, keycode, text, modifiers):
        """Switch theme using arrow keys or [shift] tab."""
        code, key = keycode
        shifted = "shift" in modifiers
        tabbed = key == "tab"
        cindex = THEME_NAMES.index(self.app.theme_name)
        if key == "right" or (tabbed and not shifted):
            cindex += 1
        elif key == "left" or (tabbed and shifted):
            cindex -= 1
        elif key.isdigit():
            cindex = int(key) - 1
        else:
            return True
        cindex = cindex % len(THEME_NAMES)
        self.app.set_theme(THEME_NAMES[cindex])
        return True

    def _make_widgets(self):
        # Palette
        self._palette_frame = XAnchor()
        self._palette_frame.add_widgets(self._palette_box, self._title_label)
        self._palette_frame.set_size(y="50sp")
        self._refresh_palette_box()
        # Subthemes
        primary = XSubThemePreview(subtheme_name="primary")
        primary.set_size(hy=1.5)
        secondary = XSubThemePreview(subtheme_name="secondary")
        secondary.set_size(hx=3)
        accent = XSubThemePreview(subtheme_name="accent")
        right_frame = XBox()
        right_frame.add_widgets(secondary, accent)
        outer_frame = XBox(orientation="vertical")
        outer_frame.add_widgets(primary, right_frame)
        self.add_widgets(
            self._palette_frame,
            outer_frame,
        )

    def _refresh_palette_box(self, *args):
        self._title_label.text = self.app.theme_name.capitalize()
        self._palette_box.clear_widgets()
        for c in self.app.theme.palette:
            pb = XLabel(
                text=c.hex.upper(),
                outline_color=(0, 0, 0),
                outline_width=2,
                valign="bottom",
                enable_theming=False,
            )
            pb.make_bg(c)
            self._palette_box.add_widget(pb)


class XSubThemePreview(XFrame):
    """Widget to preview a SubTheme."""

    def __init__(self, *args, **kwargs):
        """Initialize the class."""
        super().__init__(*args, **kwargs)
        with self.app.subtheme_context(self.subtheme_name):
            self._make_widgets()

    def _make_widgets(self):
        self._title_label = XLabel(font_size="24sp", shorten=True, shorten_from="right")
        self._title_label.set_size(y="32sp")
        self._br = XAnchor()
        self._br.set_size(y="8dp")
        self._detail_label = XLabel(
            fixed_width=True,
            padding=(10, 10),
            halign="left",
            valign="top",
        )
        self._br2 = XAnchor()
        self._br2.set_size(hx=0.5, y="4dp")
        br2_wrapped = XAnchor.wrap(self._br2)
        br2_wrapped.set_size(y="10dp")
        self._lorem_label = XLabel(
            text=LOREM_IPSUM,
            fixed_width=True,
            padding=(10, 10),
            halign="left",
            valign="top",
        )
        scroll_view = XDBox()
        scroll_view.add_widgets(
            self._detail_label,
            br2_wrapped,
            self._lorem_label,
        )
        self._label_scroll = XScroll(view=scroll_view)
        main_frame = XBox(orientation="vertical", padding="10sp")
        main_frame.add_widgets(
            self._title_label,
            self._br,
            self._label_scroll,
        )
        self.add_widget(main_frame)

    def on_subtheme(self, subtheme):
        """Override base method."""
        super().on_subtheme(subtheme)
        self._br.make_bg(subtheme.accent1)
        self._br2.make_bg(subtheme.accent2)
        self._title_label.text = self.subtheme_name.capitalize()
        self._detail_label.text = self._get_lorem_text(subtheme)

    def _get_lorem_text(self, subtheme):
        bullet = subtheme.accent2.markup("•")
        fg2m = subtheme.fg2.markup
        hexes = "\n".join((
            f"{bullet} {color_name} color {fg2m(color.hex.upper())}"
            for color_name, color in subtheme._asdict().items()
        ))
        name = self.app.theme_name.capitalize()
        return f"[size=20sp][u]{name} theme[/u][/size]\n{hexes}"


LOREM_IPSUM = (
    "Non eram nescius, Brute, cum, quae summis ingeniis exquisitaque doctrina"
    " philosophi Graeco sermone tractavissent, ea Latinis litteris mandaremus, fore"
    " ut hic noster labor in varias reprehensiones incurreret.\n\nNam quibusdam, et iis"
    " quidem non admodum indoctis, totum hoc displicet philosophari. quidam autem non"
    " tam id reprehendunt, si remissius agatur, sed tantum studium tamque multam"
    " operam ponendam in eo non arbitrantur. erunt etiam, et ii quidem eruditi"
    " Graecis litteris, contemnentes Latinas, qui se dicant in Graecis legendis"
    " operam malle consumere. postremo aliquos futuros suspicor, qui me ad alias"
    " litteras vocent, genus hoc scribendi, etsi sit elegans, personae tamen et"
    " dignitatis esse negent.\n\nContra quos omnis dicendum breviter existimo. Quamquam"
    " philosophiae quidem vituperatoribus satis responsum est eo libro, quo a nobis"
    " philosophia defensa et collaudata est, cum esset accusata et vituperata ab"
    " Hortensio. qui liber cum et tibi probatus videretur et iis, quos ego posse"
    " iudicare arbitrarer, plura suscepi veritus ne movere hominum studia viderer,"
    " retinere non posse.\n\nQui autem, si maxime hoc placeat, moderatius tamen id"
    " volunt fieri, difficilem quandam temperantiam postulant in eo, quod semel"
    " admissum coerceri reprimique non potest, ut propemodum iustioribus utamur"
    " illis, qui omnino avocent a philosophia, quam his, qui rebus infinitis modum"
    " constituant in reque eo meliore, quo maior sit, mediocritatem desiderent.\n\nSive"
    " enim ad sapientiam perveniri potest, non paranda nobis solum ea, sed fruenda"
    " etiam [sapientia] est; sive hoc difficile est, tamen nec modus est ullus"
    " investigandi veri, nisi inveneris, et quaerendi defatigatio turpis est, cum id,"
    " quod quaeritur, sit pulcherrimum. etenim si delectamur, cum scribimus, quis est"
    " tam invidus, qui ab eo nos abducat?\n\nSin laboramus, quis est, qui alienae modum"
    " statuat industriae? nam ut Terentianus Chremes non inhumanus, qui novum vicinum"
    " non vult 'fodere aut arare aut aliquid ferre denique' -- non enim illum ab"
    " industria, sed ab inliberali labore deterret -- sic isti curiosi, quos"
    " offendit noster minime nobis iniucundus labor. Iis igitur est difficilius satis"
    " facere, qui se Latina scripta dicunt contemnere.\n\nIn quibus hoc primum est in"
    " quo admirer, cur in gravissimis rebus non delectet eos sermo patrius, cum idem"
    " fabellas Latinas ad verbum e Graecis expressas non inviti legant. Quis enim tam"
    " inimicus paene nomini Romano est, qui Ennii Medeam aut Antiopam Pacuvii spernat"
    " aut reiciat, quod se isdem Euripidis fabulis delectari dicat, Latinas litteras"
    " oderit?"
)


__all__ = (
    "XThemeSelector",
    "XThemePreview",
)
