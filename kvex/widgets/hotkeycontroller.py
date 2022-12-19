"""XHotkeyController.

For simple use cases, use `XHotkeyController.register` to register and bind your
hotkeys. For more advanced use cases, the XHotkeyController class provides a way
to set which controls are active using a tree.

### Hotkeys
Hotkeys are represented using strings with a simple format: modifiers then
key name. The modifiers are as follows: '^' ctrl, '!' alt, '+' shift, '#'
super/meta. E.g. 'g', 'f1', '^+ s'.

Set `XHotkeyController.log_press` to see key names as they are pressed.

### Control tree
A control can be named with a path using dot (`.`) notation. For example a
control named 'root.app.login' will be the 'login' control with the path
'root.app'.

The controller's "active path" determines which controls are active based on
their paths. A control is active when it's path is part of the active path.
E.g. the active path 'root.app' will enable 'root.app.login' and 'root.quit'
but not 'root.debug.log' and not 'root.app.game.move'. See
`XHotkeyController.is_active`.
"""

from .. import kivy as kv
import collections
from typing import TypeVar, Callable, Any, Optional


KEYCODE_TEXT = {v: k for k, v in kv.Keyboard.keycodes.items()}
HotkeyFormat = TypeVar("HotkeyFormat", bound=str)
"""A type alias for a string formatted as either: `f'{modifiers} {key}'` or `key`."""
MODIFIER_SORT = "^!+#"
KEY2MOD = {
    "ctrl": "^",
    "alt-gr": "!",
    "alt": "!",
    "shift": "+",
    "super": "#",
    "meta": "#",
    "control": "^",
    "lctrl": "^",
    "rctrl": "^",
    "lalt": "!",
    "ralt": "!",
    "lshift": "+",
    "rshift": "+",
    "numlock": "",
    "capslock": "",
}
MOD2KEY = {
    "^": "ctrl",
    "!": "alt",
    "+": "shift",
    "#": "super",
}


def _to_hotkey_format(
    key_name: str,
    modifiers: list[str],
    /,
    *,
    honor_numlock: bool = True,
) -> HotkeyFormat:
    """Convert a combination of keys to a standard string format."""
    if (
        honor_numlock
        and "numlock" in modifiers
        and key_name.startswith("numpad")
        and len(key_name) == 7
    ):
        key_name = key_name[-1]
        assert isinstance(int(key_name), int)  # Sanity check that we have a number key
    # Remove duplicate modifiers
    modifiers = set(KEY2MOD[mod] for mod in modifiers)
    modifiers -= {""}
    # Remove modifier if it is the main key being pressed
    # e.g. when key_name == "lctrl" then "ctrl" will be in modifiers
    keyname_as_mod = KEY2MOD.get(key_name)
    if keyname_as_mod:
        modifiers -= {keyname_as_mod}
    # No space required in HotkeyFormat if no modifiers
    if len(modifiers) == 0:
        return key_name
    # Order of modifiers should be consistent
    sorted_modifiers = sorted(modifiers, key=lambda x: MODIFIER_SORT.index(x))
    # Return the HotkeyFormat
    mod_str = "".join(sorted_modifiers)
    return f"{mod_str} {key_name}"


def _fix_modifier_order(k: str) -> str:
    if " " not in k:
        return k
    mods, key = k.split(" ")
    sorted_mods = "".join(sorted(mods, key=lambda x: MODIFIER_SORT.index(x)))
    return f"{sorted_mods} {key}"


class XHotkeyController:
    """See module documentation for details."""

    def __init__(
        self,
        logger: Callable[[str], Any] = print,
        log_press: bool = False,
        log_release: bool = False,
        log_register: bool = False,
        log_bind: bool = False,
        log_callback: bool = False,
        honor_numlock: bool = True,
    ):
        """Initialize the class. See module documentation for details.

        Args:
            logger: Function to pass logging messages.
            log_press: Log key presses.
            log_release: Log key releases.
            log_register: Log control registration.
            log_bind: Log control binding.
            log_callback: Log control events.
            honor_numlock: Convert numpad keys to numbers when numlock is
                enabled.
        """
        self.registered_controls: set[str] = set()
        self.active_path: Optional[str] = ""
        self._callbacks: dict[str, Callable] = dict()
        self._hotkeys: dict[str, set] = collections.defaultdict(set)
        self.logger: Callable = logger
        self.log_press: bool = log_press
        self.log_release: bool = log_release
        self.log_register: bool = log_register
        self.log_bind: bool = log_bind
        self.log_callback: bool = log_callback
        self.honor_numlock: bool = honor_numlock
        kv.Window.bind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)

    @staticmethod
    def humanize_hotkey(hotkey: HotkeyFormat, /) -> str:
        """Generate a human-readable string from a HotkeyFormat."""
        mods, key = hotkey.split(" ") if " " in hotkey else ([], hotkey)
        dstr = [MOD2KEY[mod] for mod in mods]
        dstr.append(key)
        return " + ".join(dstr)

    def register(
        self,
        control: str,
        hotkey: HotkeyFormat,
        /,
        bind: Optional[Callable] = None,
    ):
        """Register a control with a hotkey.

        Can be used multiple times on the same control or hotkey.
        """
        if self.log_register:
            self.logger(f"Registering {control!r} with {hotkey!r}")
        self._hotkeys[hotkey].add(control)
        self.registered_controls.add(control)
        if bind:
            self.bind(control, bind)

    def bind(self, control: str, callback: Callable, *, allow_overwrite: bool = True):
        """Bind a control to a callback."""
        if not allow_overwrite and control in self._callbacks:
            raise KeyError(f"Control {control!r} already bound.")
        if control not in self.registered_controls:
            raise RuntimeError(
                f"Cannot bind to unregistered control {control!r}."
                f" Use XHotkeyController.register()."
            )
        if self.log_bind:
            self.logger(f"Binding {control!r} to {callback}")
        self._callbacks[control] = callback

    def set(self, path: Optional[str], /):
        """Set the currently active path.

        Passing None will disable all controls. Passing an empty string will
        enable all controls. See module documentation for details.
        """
        if path in self.registered_controls:
            raise RuntimeError(
                f"Cannot set to control {path!r} as active."
                f" Try setting the parent path instead."
            )
        self.active_path = path

    def is_active(self, control: str, /) -> bool:
        """Check if a control is active. See module documentation for details."""
        if self.active_path is None:
            return False
        if self.active_path == "":
            return True
        control_path = ".".join(control.split(".")[:-1])
        return self.active_path.startswith(control_path)

    def _on_key_down(
        self,
        window: kv.Window,
        key: int,
        scancode: int,
        codepoint: str,
        modifiers: list[str],
    ):
        key_name = KEYCODE_TEXT.get(key, "")
        kf = _to_hotkey_format(key_name, modifiers, honor_numlock=self.honor_numlock)
        if self.log_press:
            self.logger(
                f"Pressed:  |{kf}| ({key=} {scancode=} {codepoint=} {modifiers=})"
            )
        paths = self._hotkeys.get(kf, set())
        consumed = False
        for path in paths:
            # Skip if path is not active
            if not self.is_active(path):
                continue
            # Skip if no callback
            callback = self._callbacks.get(path)
            if not callback:
                continue
            if self.log_callback:
                self.logger(f"Control {path!r} invoking {callback}")
            callback()
            consumed = True
            break
        return consumed

    def _on_key_up(self, window: kv.Window, key: int, scancode: int):
        if self.log_release:
            key_name = KEYCODE_TEXT.get(key, "")
            self.logger(f"Released: |{key_name}|")

    def debug(self, *args, **kwargs):
        """Send debug info to logger."""
        strs = [
            f"Active path: {self.active_path}",
            "Bound hotkeys:",
            *(
                f"  {repr(hk):>20} {control!r}"
                for hk, control in self._hotkeys.items()
            ),
            "Active controls:",
            *(
                f"  {self.is_active(path)} {path!r}"
                for path in self.registered_controls
            ),
        ]
        self.logger("\n".join(strs))
