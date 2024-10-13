import json
from pynput import keyboard
from pynput.keyboard import KeyCode
import os
from PyQt5.QtCore import QTimer, QMetaObject, Qt

control_chars = {
    '\x01': 'a', '\x02': 'b', '\x03': 'c', '\x04': 'd', '\x05': 'e', '\x06': 'f', '\x07': 'g', '\x08': 'h',
    '\x09': 'i', '\x0A': 'j', '\x0B': 'k', '\x0C': 'l', '\x0D': 'm', '\x0E': 'n', '\x0F': 'o', '\x10': 'p',
    '\x11': 'q', '\x12': 'r', '\x13': 's', '\x14': 't', '\x15': 'u', '\x16': 'v', '\x17': 'w', '\x18': 'x',
    '\x19': 'y', '\x1A': 'z', '\x1B': '[', '\x1C': '\\', '\x1D': ']', '\x1E': '^', '\x1F': '_'
}

class KeybindManager:
    def __init__(self, target):
        self.target = target
        self.load_config()
        self.current_keys = set()
        self.is_recording = False
        self.recorded_chord = []
        self.current_action = None
        self.callback = None

        # Dictionary to keep track of cooldown status and timers for each action
        self.action_cooldowns = {}
        self.action_timers = {}

        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        self.listener.start()

        # Initialize timers for each action
        for action in self.config.keys():
            self.action_cooldowns[action] = False
            timer = QTimer()
            timer.setInterval(500)  # Set cooldown interval to 500ms
            timer.setSingleShot(True)
            timer.timeout.connect(lambda a=action: self.reset_cooldown(a))
            self.action_timers[action] = timer

    def reset_cooldown(self, action):
        self.action_cooldowns[action] = False

    def load_config(self):
        with open('config.json', 'r') as f:
            self.config = json.load(f)

    def update_config(self, action, chord):
        self.config[action] = chord
        with open('config.json', 'w') as f:
            json.dump(self.config, f, indent=4)

    def replace_control_chars(self, key_name):
        return control_chars.get(key_name, key_name)

    def get_key_name(self, key):
        if hasattr(key, 'name'):
            return key.name
        else:
            if type(key) == type(KeyCode()) and '\\' in repr(key):
                return self.replace_control_chars(str(key.char))
            return str(key.char)

    def get_control_key_index(self, key_name):
        index_map = {'ctrl_l': 0, 'ctrl_r': 1, 'alt_l': 2, 'alt_r': 3, 'shift': 4, 'shift_r': 5}
        return index_map.get(key_name, -1)

    def chord_to_user_friendly(self, chord):
        key_name_map = {
            'ctrl_l': 'Ctrl',
            'ctrl_r': 'Ctrl',
            'alt_l': 'Alt',
            'alt_r': 'Alt',
            'shift': 'Shift',
            'shift_r': 'Shift'
        }

        key_names = chord.split('+')
        user_friendly_key_names = [key_name_map.get(key_name, key_name) for key_name in key_names]
        user_friendly_chord = ' + '.join(user_friendly_key_names)
        return user_friendly_chord
    
    def generate_default_config(self):
        if not os.path.exists('config.json'):
            with open('config.json', 'w') as f:
                json.dump({
                'toggle_timer': 't',
                'toggle_crosshair': 'ctrl_l+shift+c',
                'toggle_settings': 'ctrl_l+shift+s', 
                'toggle_overlay_visibility': 'ctrl_l+shift+a', 
                'toggle_edit_mode': 'ctrl_l+shift+e',
                'quit': 'ctrl_l+shift+q'
                }, f, indent=4)

    def on_press(self, key):
        if self.is_recording:
            key_name = self.get_key_name(key)
            if key_name not in ('ctrl_l', 'ctrl_r', 'alt_l', 'alt_r', 'shift', 'shift_r') and key_name not in self.recorded_chord:
                self.recorded_chord.append(key_name)
                self.is_recording = False
                self.update_config(self.current_action, '+'.join(self.recorded_chord))
                if self.callback:
                    self.callback(self.current_action, '+'.join(self.recorded_chord))
            elif key_name in ('ctrl_l', 'ctrl_r', 'alt_l', 'alt_r', 'shift', 'shift_r') and key_name not in self.recorded_chord:
                self.recorded_chord.insert(self.get_control_key_index(key_name), key_name)
        else:
            key_name = self.get_key_name(key)
            self.current_keys.add(key_name)
            for action, chord in self.config.items():
                chord_keys = set(chord.split('+'))
                if chord_keys.issubset(self.current_keys):
                    if not self.action_cooldowns.get(action, False):
                        getattr(self.target, f"{action}_action")()
                        self.action_cooldowns[action] = True
                        QMetaObject.invokeMethod(self.action_timers[action], "start", Qt.QueuedConnection)
                    break

    def on_release(self, key):
        key_name = self.get_key_name(key)
        if key_name in self.current_keys:
            self.current_keys.remove(key_name)

    def record(self, action, callback):
        self.is_recording = True
        self.recorded_chord = []
        self.current_action = action
        self.callback = callback