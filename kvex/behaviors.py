"""Home of `XThemed` and `XFocusBehavior`."""

from typing import Optional
from . import kivy as kv
from .util import schedule_once
from .colors import SubTheme


class XThemed(kv.EventDispatcher):
    """A mixin for theming widgets.

    Each widget is configured to follow a particular subtheme by setting
    `XThemed.subtheme_name` (defaults to `kvex.app.XApp.subtheme_name`).

    Theming can be disabled by passing False to `enable_theming` on initialization.

    The `on_subtheme` event will be triggered whenever `kvex.app.XApp.theme` changes or
    when `XThemed.subtheme_name` is set.
    """

    def __init__(
        self,
        *args,
        subtheme_name: Optional[str] = None,
        enable_theming: bool = True,
        **kwargs,
    ):
        """See class documentation for details.

        Args:
            subtheme_name: Set `XThemed.subtheme_name`.
            enable_theming: Enable the `on_subtheme` event.
        """
        super().__init__(*args, **kwargs)
        self._subtheme_name = subtheme_name or kv.App.get_running_app().subtheme_name
        self._subtheme = None
        # The reason for using events instead of properties is due to initialization
        # order: some use cases require that all classes in the MRO are initialized
        # before an `on_subtheme` event is triggered. For this reason also, an initial
        # `on_subtheme` event is scheduled for the next frame after initialization.
        self._refresh_subtheme(trigger_event=False)
        self.register_event_type("on_subtheme")
        if enable_theming:
            schedule_once(self.trigger_subtheme)
            kv.App.get_running_app().bind(on_theme=self._refresh_subtheme)

    def on_subtheme(self, subtheme: SubTheme):
        """Called when the subtheme changes.

        Use the `kvex.colors.SubTheme` object to configure relevant colors.
        """
        pass

    @property
    def subtheme_name(self) -> str:
        """Current subtheme name. See also: `kvex.colors.SUBTHEME_NAMES`."""
        return self._subtheme_name

    @subtheme_name.setter
    def subtheme_name(self, subtheme_name: str, /):
        """Set `subtheme_name`."""
        self._subtheme_name = subtheme_name
        self._refresh_subtheme()

    @property
    def subtheme(self) -> SubTheme:
        """Current subtheme."""
        return self._subtheme

    def trigger_subtheme(self, *args):
        """Force the `on_subtheme` event to trigger."""
        self.dispatch("on_subtheme", self._subtheme)

    def _refresh_subtheme(self, *args, trigger_event: bool = True):
        old_subtheme = self._subtheme
        new_subtheme = getattr(kv.App.get_running_app().theme, self._subtheme_name)
        self._subtheme = new_subtheme
        if new_subtheme is not old_subtheme and trigger_event:
            self.dispatch("on_subtheme", new_subtheme)


class XFocusBehavior(kv.FocusBehavior):
    """Like Kivy's `FocusBehavior` with option to disable defocusing on escape key."""

    escape_unfocuses = kv.BooleanProperty(False)
    """Enables defocusing when pressing escape. Defaults to False."""

    def keyboard_on_key_up(self, w, key_pair):
        """Overrides base method to manually defocus on escape."""
        keycode, key = key_pair
        if self.escape_unfocuses and key == "escape":
            self.focus = False
            return True
        return False


__all__ = (
    "XThemed",
    "XFocusBehavior",
)
