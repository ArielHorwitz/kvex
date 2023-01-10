"""Home of `XButtonBar`."""

from typing import Optional, Callable
from functools import partial
from .layouts import XTAnchor, XBox
from .dropdown import XDropDown
from .spinner import XSpinner, XSpinnerOption
from ..colors import THEMES


class XButtonBar(XTAnchor):
    """A bar of buttons nested in two layers."""

    def __init__(self, nested_subtheme: Optional[str] = None, **kwargs):
        """Initialize the class.

        Args:
            nested_subtheme: Specify subtheme for nested buttons.
        """
        super().__init__(**kwargs)
        self._nested_subtheme = nested_subtheme
        self._names: dict[list[str]] = dict()
        self._spinners: dict[XSpinner] = dict()
        self._callbacks: dict[str, Callable] = dict()
        self._box = XBox()
        self.add_widget(self._box)
        self.register_event_type("on_select")

    def add_category(self, category: str, /, *, display_as: Optional[str] = None):
        """Add a category for buttons.

        Args:
            category: Category name, used for callbacks.
            display_as: Button text, defaults to the capitalized category name.
        """
        if category in self._names:
            raise ValueError(f"Category {category!r} already in use.")
        if display_as is None:
            display_as = category.capitalize()
        with self.app.subtheme_context(self.subtheme_name):
            spinner = XSpinner(
                text=display_as,
                option_cls=XButtonBarSpinnerOption,
            )
        self._spinners[category] = spinner
        self._box.add_widget(spinner)
        self._names[category] = []
        spinner.bind(on_select=partial(self._on_spinner_select, category))

    def add_button(
        self,
        category: str,
        name: str,
        /,
        callback: Optional[Callable] = None,
        *,
        display_as: Optional[str] = None,
    ):
        """Add a button in a category.

        Args:
            category: Category name, used for callbacks.
            name: Button name, used for callbacks.
            callback: Callback when button is pressed.
            display_as: Button text, defaults to a the button name formatted.
        """
        if category not in self._names:
            self.add_category(category)
        if display_as is None:
            display_as = name.replace("_", " ").capitalize()
        spinner = self._spinners[category]
        with self.app.subtheme_context(self._nested_subtheme):
            spinner.values.append(display_as)
        self._names[category].append(name)
        self._callbacks[f"{category}.{name}"] = callback

    def get_button(
        self,
        category: str,
        button: Optional[str] = None,
    ) -> XDropDown | XSpinnerOption:
        """Get the XSpinnerOption button or XDropDown if no button specified."""
        spinner = self._spinners[category]
        if not button:
            return spinner
        idx = self._names[category].index(button)
        return spinner._dropdown.container.children[-idx - 1]

    def set_callback(self, category: str, button: str, callback: Callable, /):
        """Change a callback."""
        self._callbacks[f"{category}.{button}"] = callback

    def on_select(self, category: str, button: str):
        """Called when a button is pressed."""
        pass

    def _on_spinner_select(self, category, w, index, text):
        button = self._names[category][index]
        callback = self._callbacks.get(f"{category}.{button}")
        if callback:
            callback()
        self.dispatch("on_select", category, button)

    def add_theme_selectors(
        self,
        *,
        category: str = "Themes",
        prefix: str = "Change to: ",
        suffix: str = "",
    ):
        """Add theme selection buttons."""
        for tname in THEMES.keys():
            self.add_button(
                "theme",
                tname,
                display_as=f"{prefix}{tname.capitalize()}{suffix}",
                callback=lambda *a, t=tname: self.app.set_theme(t),
            )


class XButtonBarSpinnerOption(XSpinnerOption):
    """SpinnerOption."""

    def __init__(self, *args, **kwargs):
        """Initialize the class."""
        kwargs |= dict(
            halign="left",
            valign="middle",
            padding=(10, 0),
            height="32dp",
        )
        super().__init__(*args, **kwargs)
        self.bind(size=self.on_size)

    def on_size(self, w, size):
        """Fix text size to widget size for alignment."""
        self.text_size = size


__all__ = (
    "XButtonBar",
    "XButtonBarSpinnerOption",
)
