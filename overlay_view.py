# overlay_view.py

import logging
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer
from crosshair_widget import CrosshairWidget
from smudge_timer import SmudgeTimer

class OverlayView(QWidget):
    def __init__(self, ui_config, keybind_manager, keybind_config_controller):
        super().__init__()
        self.keybind_manager = keybind_manager
        self.keybind_config_controller = keybind_config_controller
        self.toggle_timer_allowed = True

        # Set the widget attributes
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.WindowTransparentForInput)
        self.setWindowOpacity(ui_config.get("window_opacity", 0.7))

        min_size = ui_config.get("min_window_size", {"width": 200, "height": 100})
        self.setMinimumSize(min_size["width"], min_size["height"])

        # Create and position the crosshair widget
        self.crosshair_widget = CrosshairWidget()
        self.crosshair_widget.setParent(self)
        self.crosshair_widget.move(self.width() // 2 - 5, self.height() // 2 - 5)
        self.crosshair_widget.show()  # Initially hidden

        # Initialize Smudge Timer widget
        self.smudge_timer = SmudgeTimer(self)
        self.smudge_timer.move(self.width() - self.smudge_timer.width() - 10, 10)  # Position at top-right
        self.smudge_timer.show()  # Initially shown

        # Register keybind actions
        self.keybind_manager.set_callback("toggle_settings", self.toggle_keybind_config_view)

        self.keybind_config_controller.view.setParent(self)
        self.keybind_config_controller.view.move(10, 10)  # Adjust offset as needed

        # Register keybinds for activation
        for action, bind_info in self.keybind_manager.keybinds.items():
            if bind_info['callback'] is None:
                self.keybind_manager.set_callback(action, lambda a=action: self.activate_action(a))

        self.show()  # Ensure the overlay is shown upon initialization

    def toggle_smudge_timer(self):
        """Toggle the smudge timer with debounce to prevent rapid toggling."""

        # Emit start or stop signal based on timer status
        if self.smudge_timer.timer.isActive():
            self.smudge_timer.stop_timer_signal.emit()
        else:
            self.smudge_timer.start_timer_signal.emit()

    def allow_toggle_timer(self):
        """Re-enable timer toggling."""
        self.toggle_timer_allowed = True

    def toggle_keybind_config_view(self):
        """Toggle the visibility of the keybind configuration view."""
        self.keybind_config_controller.view.toggle_visibility()
        if self.keybind_config_controller.view.isVisible():
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowTransparentForInput)
        else:
            self.setWindowFlags(self.windowFlags() | Qt.WindowTransparentForInput)
        self.show()  # Refresh the window flags

    def toggle_crosshair(self):
        """Toggle visibility of the crosshair widget."""
        self.crosshair_widget.setVisible(not self.crosshair_widget.isVisible())

    def resizeEvent(self, event):
        """Ensure crosshair stays centered on resize."""
        self.crosshair_widget.move(self.width() // 2 - 5, self.height() // 2 - 5)
        self.smudge_timer.move(self.width() - self.smudge_timer.width() - 10, 10)
        super().resizeEvent(event)

    def set_overlay_geometry(self, x, y, width, height):
        """Sets the overlay's geometry to match the game window."""
        logging.debug(f"Setting overlay geometry to x: {x}, y: {y}, width: {width}, height: {height}")
        self.setGeometry(x, y, width, height)
        self.show()
        logging.info("Overlay displayed and positioned.")