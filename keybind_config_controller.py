# keybind_config_controller.py

import logging
from PyQt5.QtCore import pyqtSignal, QObject
from keybind_config_model import KeybindConfigModel
from keybind_config_view import KeybindConfigView
from keybind_manager import KeybindManager

class KeybindConfigController(QObject):
    keybind_recording_started = pyqtSignal(str)  # Signal for starting keybind recording
    keybind_recording_finished = pyqtSignal(str, str)  # Signal for finishing keybind recording

    def __init__(self, keybind_manager: KeybindManager, config_file='config.json'):
        super().__init__()
        self.model = KeybindConfigModel(config_file)
        self.view = KeybindConfigView()
        self.keybind_manager = keybind_manager
        self.is_recording = False
        self.current_action = None
        self.original_keybind = None

        # Initialize the view with keybinds data and set up connections
        self.view.display_keybinds(
            self.model.keybinds,
            self.start_recording,
            self.keybind_manager.chord_to_user_friendly
        )

        # Connect signals
        self.keybind_recording_finished.connect(self.update_keybind)

    def toggle_visibility(self):
        self.view.toggle_visibility()

    def start_recording(self, action, keybind_button):
        if self.is_recording:
            return  # Prevent starting a new recording if already recording

        self.is_recording = True
        self.current_action = action
        self.original_keybind = self.model.keybinds[action]
        keybind_button.setText("Recording...")

        # Emit signal to start recording
        self.keybind_manager.start_recording(action, lambda a, k: self.finish_recording(a, k, keybind_button))
        self.keybind_recording_started.emit(action)

    def finish_recording(self, action, new_keybind, keybind_button):
        self.is_recording = False
        self.current_action = None

        # Emit signal instead of directly updating
        self.keybind_recording_finished.emit(action, new_keybind)
        keybind_button.setText(self.keybind_manager.chord_to_user_friendly(new_keybind).upper())

    def update_keybind(self, action, new_keybind):
        """Slot to update model and save keybinds."""
        self.model.update_keybind(action, new_keybind)
        self.view.update_keybind_display(
            action,
            self.view.get_keybind_button(action),
            new_keybind,
            self.keybind_manager.chord_to_user_friendly
        )

    def cancel_recording(self):
        # If recording is canceled, revert to the original keybind
        if self.is_recording:
            self.model.keybinds[self.current_action] = self.original_keybind
            logging.info(f"Recording cancelled for {self.current_action}. Reverted to original bind.")
            self.is_recording = False
            self.current_action = None
            self.view.display_keybinds(self.model.keybinds, self.start_recording, self.keybind_manager.chord_to_user_friendly)
