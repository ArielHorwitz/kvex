"""Example app."""

import kvex as kx


class ExampleApp(kx.XApp):
    """Example application."""

    def __init__(self, *args, **kwargs):
        """Initialize the app."""
        super().__init__(*args, **kwargs)
        self.title = "Kvex testing"
        self.set_size(1024, 768)
        self.set_position(1600, 700)

    def build(self):
        return kx.XRoot(window_delay=False)

    def on_start(self):
        """Show loading screen while making widgets."""
        loading_sequence = [
            self._make_loading_widgets,
            0.1,
            self._make_widgets,
            0.1,
            self._finalize_loading,
        ]
        kx.schedule_many(loading_sequence)

    def _make_loading_widgets(self, *args):
        self.set_size(400, 100)
        self.root.add_widget(kx.XLabel(text="Loading Kvex example app..."))

    def _make_widgets(self, *args):
        self.controller = kx.XHotkeyController()
        self.controller.register("quit", "^+ q", self.stop)
        self.controller.register("restart", "^+ w", self.restart)
        self.controller.register("debug", "^+ d", self._debug)
        btn_bar = kx.XButtonBar(
            category_subtheme="secondary",
            dropdown_subtheme="accent",
            nested_subtheme="primary",
        )
        btn_bar.add_button("app", "quit", self.stop)
        btn_bar.add_button("app", "restart", self.restart)
        btn_bar.add_button("app", "debug", self._debug)
        btn_bar.add_theme_selectors()
        outer_container = kx.XBox(orientation="vertical")
        outer_container.add_widgets(btn_bar, MainWidget())
        outer_frame = kx.frame(outer_container, bg=True, frame=False, pad=False)
        self.root.clear_widgets()
        self.root.add_widget(outer_frame)
        self.maximize()

    def _finalize_loading(self, *args):
        self.root.window_delay = True

    def _debug(self, *args):
        self.controller.debug()


class MainWidget(kx.FocusBehavior, kx.XAnchor):
    """Main example widget, for switching themes and previewing subthemes."""

    def __init__(self):
        """Initialize the class."""
        self._palette_box = kx.XBox()
        super().__init__()
        self.focus = True
        self._make_widgets()
        self.app.bind(on_theme=self._refresh_palette_box)

    def keyboard_on_key_down(self, w, keycode, text, modifiers):
        """Switch theme using arrow keys or [shift] tab."""
        code, key = keycode
        shifted = "shift" in modifiers
        tabbed = key == "tab"
        cindex = kx.THEME_NAMES.index(self.app.theme_name)
        if key == "right" or (tabbed and not shifted):
            cindex += 1
        elif key == "left" or (tabbed and shifted):
            cindex -= 1
        elif key.isdigit():
            cindex = int(key) - 1
        elif key == "f5":
            self.app.reload_themes()
        else:
            return True
        cindex = cindex % len(kx.THEME_NAMES)
        self.app.set_theme(kx.THEME_NAMES[cindex])
        return True

    def _make_widgets(self):
        # Palette
        self._title_label = kx.XLabel(
            font_size="24sp",
            color=(0, 0, 0),
            outline_color=(1, 1, 1),
            outline_width=2,
            valign="top",
            enable_theming=False,
        )
        self._palette_frame = kx.XAnchor()
        self._palette_frame.add_widgets(self._palette_box, self._title_label)
        self._palette_frame.set_size(y="50sp")
        self._refresh_palette_box()
        # Subthemes
        primary = WidgetsBox(subtheme_name="primary")
        primary.set_size(hx=2)
        secondary = WidgetsBox(subtheme_name="secondary")
        secondary.set_size(hx=1.5)
        accent = WidgetsBox(subtheme_name="accent")
        preview_frame = kx.XBox()
        preview_frame.add_widgets(primary, secondary, accent)
        # Assemble
        main_box = kx.XBox(orientation="vertical")
        main_box.add_widgets(
            self._palette_frame,
            preview_frame,
        )
        self.add_widget(main_box)

    def _refresh_palette_box(self, *args):
        self._title_label.text = f"{self.app.theme_name.capitalize()} Theme"
        self._palette_box.clear_widgets()
        for c in self.app.theme.palette:
            pb = kx.XLabel(
                text=c.hex.upper(),
                outline_color=(0, 0, 0),
                outline_width=2,
                valign="bottom",
                enable_theming=False,
            )
            pb.make_bg(c)
            self._palette_box.add_widget(pb)


class WidgetsBox(kx.XFrame):
    """Collection of various widgets for preview purposes."""

    def __init__(self, **kwargs):
        """Initialize the class."""
        kwargs = dict(dynamic=False, pad=True, bg=True, frame=True) | kwargs
        super().__init__(**kwargs)
        with self.app.subtheme_context(self.subtheme_name):
            self._make_widgets()

    def _make_widgets(self):
        # Title
        title_label = kx.XLabel(
            text=f"{self.app.subtheme_name.capitalize()} subtheme",
            font_size="24sp",
            shorten=True,
            shorten_from="right",
        )
        title_label.set_size(y="32sp")
        # Text
        color_count = len(self.subtheme.COLOR_NAMES)
        self._color_labels = tuple(
            kx.XLabel(font_size="12sp", font_name="RobotoMono-Regular")
            for i in range(color_count)
        )
        palette_grid = kx.XGrid(cols=3)
        palette_grid.set_size(y="80sp")
        palette_grid.add_widgets(*self._color_labels)
        self._palette_label = kx.XLabel(font_size="12sp")
        palette_box = kx.XBox(orientation="vertical")
        palette_box.set_size(y="110sp")
        palette_box.add_widgets(palette_grid, self._palette_label)
        self._lorem_label = kx.XLabel(
            text=self._get_lorem_ipsum(),
            fixed_width=True,
            padding=(10, 10),
            halign="left",
            valign="top",
        )
        # Input panel
        pwidgets = dict(
            str=kx.XInputPanelWidget("String:", default=self.subtheme_name),
            disabled=kx.XInputPanelWidget("Disabled:", default="disabled input"),
            zerohundred=kx.XInputPanelWidget("Capped -2.5 to 100:", "float"),
            float=kx.XInputPanelWidget("Float 0 to 42:", "float", default=42),
            password=kx.XInputPanelWidget("Password:", "password", default="foobar"),
            choice=kx.XInputPanelWidget("Choice:", "choice", choices=["eggs", "spam"]),
            bool=kx.XInputPanelWidget("Checkbox:", "bool", default=True),
            bool_dis=kx.XInputPanelWidget("Disabled:", "bool", default=True),
        )
        input_panel = kx.XInputPanel(pwidgets)
        input_panel.set_enabled("bool_dis", False)
        input_panel.set_enabled("disabled", False)
        input_panel.get_widget("zerohundred").max_value = 100
        input_panel.get_widget("zerohundred").min_value = -2.5
        input_panel.get_widget("zerohundred").disable_invalid = True
        input_panel.get_widget("float").max_value = 42
        disbtn = kx.pad(kx.XButton(text="Disabled button", disabled=True))
        disbtn.set_size(hx=0.5)
        disbtn = kx.pad(disbtn)
        disbtn.set_size(y="40dp")
        content_scroll_view = kx.XDynamicBox(orientation="vertical")
        content_scroll_view.add_widgets(
            palette_box,
            kx.justify(kx.frame(kx.XDateTime(), dynamic=True)),
            input_panel,
            disbtn,
            kx.XDivider(hint=0.5),
            self._lorem_label,
        )
        content = kx.XScroll(view=content_scroll_view)
        # Assemble
        main_frame = kx.XBox(orientation="vertical")
        main_frame.add_widgets(
            title_label,
            kx.XDivider(),
            content,
        )
        self.add_widget(kx.pad(main_frame, padding="3dp"))

    def on_subtheme(self, subtheme):
        """Refresh colors."""
        super().on_subtheme(subtheme)
        self._refresh_color_labels()
        self._lorem_label.text = self._get_lorem_ipsum()
        self._refresh_palette_box()

    def _refresh_palette_box(self):
        subtheme_hexes = set(c.hex for c in dict(self.subtheme).values())
        theme_hexes = set(c.hex for c in self.app.theme.palette)
        unused = sorted(theme_hexes - subtheme_hexes, key=self._palette_sort)
        unused = f"Unused palette: {', '.join(unused)}"
        extras = sorted(subtheme_hexes - theme_hexes, key=self._palette_sort)
        extras = f"Extra colors: {', '.join(extras)}"
        self._palette_label.text = f"{unused}\n{extras}"

    def _palette_sort(self, h):
        theme_palette = tuple(c.hex for c in self.app.theme.palette)
        if h in theme_palette:
            return theme_palette.index(h)
        return hash(h)

    def _refresh_color_labels(self):
        for i, (color_name, color) in enumerate(dict(self.subtheme).items()):
            lbl = self._color_labels[i]
            hex_text = color.hex.upper()[1:]
            hex_text = f"{color.markup('#')}{hex_text}"
            text = f"{color_name}\n{hex_text}"
            lbl.text = text
            lbl.subtheme_name = self.subtheme_name

    def _get_lorem_ipsum(self):
        paragraphs = list(LOREM_IPSUMS)
        paragraphs.insert(3, self.subtheme.fg_warn.markup(_WARNING_TEXT))
        paragraphs.insert(2, self.subtheme.fg_muted.markup(_MUTED_TEXT))
        paragraphs.insert(1, self.subtheme.fg_accent.markup(_ACCENT_TEXT))
        return "\n\n".join(paragraphs)


_ACCENT_TEXT = "Accent lorem ipsum non facere qui se curiosi."
_MUTED_TEXT = "Muted lorem ipsum operam malle consumere..."
_WARNING_TEXT = "Warning lorem ipsum genus responsum!"
LOREM_IPSUMS = [
    "[b][i]Non eram nescius[/i][/b], Brute, cum, quae summis ingeniis [b]exquisitaque doctrina philosophi[/b] Graeco sermone tractavissent, ea Latinis litteris mandaremus, [i]fore ut hic noster labor in varias reprehensiones incurreret[/i].",  # noqa: E501
    "[u]Nam quibusdam, et iis quidem non admodum indoctis[/u], totum hoc displicet philosophari. quidam autem non tam id reprehendunt, si remissius agatur, sed tantum studium tamque multam operam ponendam in eo non arbitrantur.",  # noqa: E501
    "Erunt etiam, et ii quidem eruditi Graecis litteris, contemnentes Latinas, qui se dicant in Graecis legendis operam malle consumere.",  # noqa: E501
    "Postremo aliquos futuros suspicor, qui me ad alias litteras vocent, genus hoc scribendi, etsi sit elegans, personae tamen et dignitatis esse negent. Contra quos omnis dicendum breviter existimo. Quamquam philosophiae quidem vituperatoribus satis responsum est eo libro, quo a nobis philosophia defensa et collaudata est, cum esset accusata et vituperata ab Hortensio. qui liber cum et tibi probatus videretur et iis, quos ego posse iudicare arbitrarer, plura suscepi veritus ne movere hominum studia viderer, retinere non posse.",  # noqa: E501
    "Qui autem, si maxime hoc placeat, moderatius tamen id volunt fieri, difficilem quandam temperantiam postulant in eo, quod semel admissum coerceri reprimique non potest, ut propemodum iustioribus utamur illis, qui omnino avocent a philosophia, quam his, qui rebus infinitis modum constituant in reque eo meliore, quo maior sit, mediocritatem desiderent. Sive enim ad sapientiam perveniri potest, non paranda nobis solum ea, sed fruenda etiam [sapientia] est; sive hoc difficile est, tamen nec modus est ullus investigandi veri, nisi inveneris, et quaerendi defatigatio turpis est, cum id, quod quaeritur, sit pulcherrimum. etenim si delectamur, cum scribimus, quis est tam invidus, qui ab eo nos abducat?",  # noqa: E501
    "Sin laboramus, quis est, qui alienae modum statuat industriae? nam ut Terentianus Chremes non inhumanus, qui novum vicinum non vult 'fodere aut arare aut aliquid ferre denique' -- non enim illum ab industria, sed ab inliberali labore deterret -- sic isti curiosi, quos offendit noster minime nobis iniucundus labor. Iis igitur est difficilius satis facere, qui se Latina scripta dicunt contemnere. In quibus hoc primum est in quo admirer, cur in gravissimis rebus non delectet eos sermo patrius, cum idem fabellas Latinas ad verbum e Graecis expressas non inviti legant. Quis enim tam inimicus paene nomini Romano est, qui Ennii Medeam aut Antiopam Pacuvii spernat aut reiciat, quod se isdem Euripidis fabulis delectari dicat, Latinas litteras oderit?",  # noqa: E501
]


def run():
    """Run the example app."""
    print("Running Kvex ExampleApp...")
    ExampleApp().run()


if __name__ == "__main__":
    run()
