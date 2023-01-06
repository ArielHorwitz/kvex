

from . import kivy as kv


class XFocusBehavior(kv.FocusBehavior):
    escape_unfocuses = kv.BooleanProperty(False)

    def keyboard_on_key_up(self, w, key_pair):
        """Overrides base method to manually defocus on escape."""
        keycode, key = key_pair
        if self.escape_unfocuses and key == "escape":
            self.focus = False
            return True
        return False


__all__ = (
    "XFocusBehavior",
)
