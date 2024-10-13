# keybind_config_view.py

from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt, pyqtSlot
import logging

class KeybindConfigView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.keybind_buttons = {}  # Store buttons by action

    def init_ui(self):
        # Set window flags for frameless window
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setWindowOpacity(0.9)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.8); border: 1px solid white;")

        # Set fixed size and position for the settings menu
        self.setFixedSize(450, 380)
        self.move(10, 10)  # Position the window at the top-left corner of the overlay
        self.setVisible(False)  # Initially hidden

        # Container frame with minimal padding
        container = QFrame()
        container.setStyleSheet("background-color: rgba(30, 30, 30, 0.9); border: 1px solid white; padding: 6px;")

        # Main layout with container
        main_layout = QVBoxLayout()
        main_layout.addWidget(container)
        self.setLayout(main_layout)

        # Title and action layout
        self.layout = QVBoxLayout(container)
        self.layout.setSpacing(8)

        title_label = QLabel("Keybinds")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold; background: transparent;")
        self.layout.addWidget(title_label)

    def display_keybinds(self, keybinds, start_recording_callback, chord_to_user_friendly):
        # Clear the existing layout except for the title label
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget and isinstance(widget, QLabel) and widget.text() == "Keybinds":
                continue
            if widget:
                widget.deleteLater()

        # Populate keybind rows
        for action, keybind in keybinds.items():
            user_friendly_action = action.replace("_", " ").title()
            user_friendly_keybind = chord_to_user_friendly(keybind).upper()
            
            # Create label and button for each action
            action_label = QLabel(user_friendly_action)
            action_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            action_label.setFixedHeight(26)
            action_label.setStyleSheet("color: white; font-size: 13px; font-weight: bold;")

            keybind_button = QPushButton(user_friendly_keybind)
            keybind_button.setFixedHeight(26)
            keybind_button.setStyleSheet(
                "color: black; background-color: white; font-size: 12px; border: 1px solid black;"
            )
            keybind_button.clicked.connect(lambda _, a=action, btn=keybind_button: start_recording_callback(a, btn))

            # Store button for reference
            self.keybind_buttons[action] = keybind_button

            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(10, 4, 10, 4)
            row_layout.setSpacing(12)
            row_layout.addWidget(action_label)
            row_layout.addWidget(keybind_button)

            row_widget = QWidget()
            row_widget.setLayout(row_layout)
            self.layout.addWidget(row_widget)

    def get_keybind_button(self, action):
        """Retrieve the button associated with a given action."""
        return self.keybind_buttons.get(action)
    
    @pyqtSlot(str, QPushButton, str)
    def update_keybind_display(self, action, keybind_button, new_keybind, chord_to_user_friendly):
        """Update button text with a user-friendly keybind display in uppercase."""
        user_friendly_keybind = chord_to_user_friendly(new_keybind).upper()
        keybind_button.setText(user_friendly_keybind)

    @pyqtSlot()
    def toggle_visibility(self):
        """Safely toggle the visibility of the settings window."""
        self.setVisible(not self.isVisible())
