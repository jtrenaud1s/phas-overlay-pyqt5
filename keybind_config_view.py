# keybind_config_view.py

from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt, pyqtSlot
import logging

class KeybindConfigView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.keybind_buttons = {}  # Dictionary to store buttons by action

    def init_ui(self):
        # Set window flags for an always-on-top frameless window
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setWindowOpacity(0.9)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.8); border: 1px solid white;")
        
        # Set fixed size for the settings menu
        self.setFixedSize(450, 380)
        self.move(0, 0)  # Position the window at the top-left corner of the screen
        self.setVisible(False)  # Initially hidden

        # Container frame with minimal padding
        container = QFrame()
        container.setStyleSheet("background-color: rgba(30, 30, 30, 0.9); border: 1px solid white; padding: 6px;")

        # Main layout with container
        main_layout = QVBoxLayout()
        main_layout.addWidget(container)
        self.setLayout(main_layout)

        # Layout inside the container for the title label and keybind rows
        self.layout = QVBoxLayout(container)
        self.layout.setSpacing(8)  # Slightly reduced spacing for compactness

        # Add a centered title label at the top
        title_label = QLabel("Keybinds")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold; background: transparent; border: none; margin-bottom: 12px;")
        self.layout.addWidget(title_label)

    def display_keybinds(self, keybinds, start_recording_callback, chord_to_user_friendly):
        # Clear existing layout except for the title label
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget and isinstance(widget, QLabel) and widget.text() == "Keybinds":
                continue  # Keep the title label
            if widget:
                widget.deleteLater()

        # Add keybind rows
        for action, keybind in keybinds.items():
            # Format action name to be user-friendly
            user_friendly_action = action.replace("_", " ").title()

            # Convert keybind chord to a user-friendly display format and make uppercase
            user_friendly_keybind = chord_to_user_friendly(keybind).upper()
            
            # Create a label with the user-friendly action name
            action_label = QLabel(user_friendly_action)
            action_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            action_label.setFixedHeight(26)
            action_label.setStyleSheet("color: white; font-size: 13px; font-weight: bold; border: none;")

            # Create a button with the same height as the label
            keybind_button = QPushButton(user_friendly_keybind)
            keybind_button.setFixedHeight(26)
            keybind_button.setStyleSheet(
                "color: black; background-color: white; font-size: 12px; border: 1px solid black; border-radius: 0;"
            )
            keybind_button.clicked.connect(lambda _, a=action, btn=keybind_button: start_recording_callback(a, btn))

            # Store button in the dictionary
            self.keybind_buttons[action] = keybind_button

            # Layout for each action and button pair
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

    def toggle_visibility(self):
        self.setVisible(not self.isVisible())
