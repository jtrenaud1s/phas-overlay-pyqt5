# keybind_manager.py

import json
import logging
from PyQt5.QtCore import QTimer, QMetaObject, Qt
from pynput import keyboard
from pynput.keyboard import KeyCode

# Special character mapping
control_chars = {
    '\x01': 'a', '\x02': 'b', '\x03': 'c', '\x04': 'd', '\x05': 'e', '\x06': 'f', '\x07': 'g', '\x08': 'h',
    '\x09': 'i', '\x0A': 'j', '\x0B': 'k', '\x0C': 'l', '\x0D': 'm', '\x0E': 'n', '\x0F': 'o', '\x10': 'p',
    '\x11': 'q', '\x12': 'r', '\x13': 's', '\x14': 't', '\x15': 'u', '\x16': 'v', '\x17': 'w', '\x18': 'x',
    '\x19': 'y', '\x1A': 'z', '\x1B': '[', '\x1C': '\\', '\x1D': ']', '\x1E': '^', '\x1F': '_'
}

class KeybindManager:
    def __init__(self, target, keybinds_config, cooldowns_config):
        self.target = target
        self.keybinds_config = keybinds_config
        self.current_keys = set()
        self.is_recording = False
        self.recorded_chord = []
        self.current_action = None
        self.callback = None
        self.keybinds = {}  # Dictionary to hold all keybinds with cooldown information
        self.action_cooldowns = {}

        self.default_interval = cooldowns_config.get("default_interval", 500)
        self.load_keybinds(self.keybinds_config, cooldowns_config.get("specific_intervals", {}))
        self.setup_listeners()

    def load_keybinds(self, keybinds_config, specific_intervals):
        """Initialize keybinds and their cooldown timers based on config."""
        for action, chord in keybinds_config.items():
            self.register_action(action, chord)

    def setup_listeners(self):
        """Set up keyboard listeners."""
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def reset_cooldown(self, action):
        """Reset cooldown status for a keybind action."""
        self.keybinds[action]['cooldown'] = False
        logging.debug(f"Cooldown reset for action: {action}")

    def register_action(self, action, chord, callback=None):
        """Registers a new action or updates an existing one in the keybinds configuration."""
        chord_keys = set(chord.split('+'))
        timer = QTimer()
        timer.setInterval(self.default_interval)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda a=action: self.reset_cooldown(a))

        self.keybinds[action] = {
            'keys': chord_keys,
            'cooldown': False,
            'timer': timer,
            'callback': callback
        }
        logging.info(f"Registered new keybind action '{action}' with chord: {chord}")

    def replace_control_chars(self, key_name):
        """Replace special character codes with readable names."""
        return control_chars.get(key_name, key_name)

    def get_key_name(self, key):
        """Retrieve the name of the key, handling special characters."""
        if hasattr(key, 'name'):
            return key.name
        else:
            if isinstance(key, KeyCode) and '\\' in repr(key):
                return self.replace_control_chars(str(key.char))
            return str(key.char)

    def on_press(self, key):
        """Handle key press events."""
        key_name = self.get_key_name(key)
        logging.debug(f"Key pressed: {key_name}")
        if self.is_recording:
            if key_name not in ('ctrl_l', 'ctrl_r', 'alt_l', 'alt_r', 'shift', 'shift_r') and key_name not in self.recorded_chord:
                self.recorded_chord.append(key_name)
            elif key_name in ('ctrl_l', 'ctrl_r', 'alt_l', 'alt_r', 'shift', 'shift_r') and key_name not in self.recorded_chord:
                self.recorded_chord.insert(self.get_control_key_index(key_name), key_name)
            logging.debug(f"Recording key chord: {self.recorded_chord}")
        else:
            # Normal key press handling
            self.current_keys.add(key_name)
            logging.debug(f"Current keys held: {self.current_keys}")
            for action, bind_info in self.keybinds.items():
                logging.debug(f"Checking action '{action}' with required keys: {bind_info['keys']}")
                if bind_info['keys'].issubset(self.current_keys) and not bind_info['cooldown']:
                    logging.debug(f"Activating keybind action '{action}' with keys: {self.current_keys}")
                    if bind_info['callback']:
                        bind_info['callback']()
                    bind_info['cooldown'] = True
                    QMetaObject.invokeMethod(bind_info['timer'], "start", Qt.QueuedConnection)
                    break

    def on_release(self, key):
        """Handle key release events."""
        key_name = self.get_key_name(key)
        if key_name in self.current_keys:
            self.current_keys.remove(key_name)
        logging.debug(f"Key released: {key_name}")
        logging.debug(f"Keys currently held after release: {self.current_keys}")

        if self.is_recording and not self.current_keys:
            chord = '+'.join(self.recorded_chord)
            self.finish_recording(chord)

    def finish_recording(self, chord):
        """Finish recording a keybind and apply the new configuration."""
        if self.is_recording:
            self.callback(self.current_action, chord)
            self.is_recording = False
            logging.info(f"Recording finished for action: {self.current_action} with new keybind: {chord}")

    def cancel_recording(self):
        """Cancel recording and reset the recording state."""
        self.is_recording = False
        logging.info("Recording canceled.")

    def get_control_key_index(self, key_name):
        """Return the preferred index for control keys in the recorded chord."""
        index_map = {'ctrl_l': 0, 'ctrl_r': 1, 'alt_l': 2, 'alt_r': 3, 'shift': 4, 'shift_r': 5}
        return index_map.get(key_name, -1)

    def chord_to_user_friendly(self, chord):
        """Convert a key chord to a user-friendly display string."""
        key_name_map = {
            'ctrl_l': 'Ctrl',
            'ctrl_r': 'Ctrl',
            'alt_l': 'Alt',
            'alt_r': 'Alt',
            'shift': 'Shift',
            'shift_r': 'Shift'
        }
        return ' + '.join(key_name_map.get(k, k) for k in chord.split('+'))

    def set_callback(self, action, callback):
        """Sets a callback for an existing keybind action without re-registering it."""
        if action in self.keybinds:
            self.keybinds[action]['callback'] = callback
            logging.debug(f"Callback set for action '{action}'")
        else:
            logging.warning(f"Action '{action}' not found. Please register it first.")

    def start_recording(self, action, callback):
        """Start recording a new keybind."""
        self.current_keys.clear()
        self.is_recording = True
        self.recorded_chord = []
        self.current_action = action
        self.callback = callback
        logging.info(f"Started recording for action: {action}")
