import logging
import time
from PyQt5.QtCore import QCoreApplication, QObject
from PyQt5.QtWidgets import QApplication
from overlay_model import OverlayModel
from overlay_view import OverlayView

class OverlayController:
    def __init__(self, model, view, keybind_manager, cooldowns_config):
        self.model = model
        self.view = view
        self.keybind_manager = keybind_manager
        self.timeout = cooldowns_config.get("default_interval", 120000)  # 2 minutes default
        self.start_time = time.time()
        logging.debug(f"OverlayController initialized with timeout: {self.timeout} ms.")

        # Register quit action
        self.keybind_manager.set_callback("quit", self.quit_application)
        self.keybind_manager.set_callback("toggle_overlay_visibility", self.toggle_overlay_visibility)
        self.keybind_manager.set_callback("toggle_crosshair", self.view.toggle_crosshair)
        self.keybind_manager.set_callback("toggle_timer", self.view.toggle_smudge_timer)

    def start(self):
        self.check_game_window_loop()

    def check_game_window_loop(self):
        while True:
            if self.model.find_game_window():
                self.update_overlay_position()
                break
            elif (time.time() - self.start_time) * 1000 > self.timeout:
                logging.error("Game window not found within timeout. Exiting.")
                QCoreApplication.quit()
                break
            time.sleep(1)

    def update_overlay_position(self):
        geometry = self.model.get_game_window_geometry()
        if geometry:
            x, y, width, height = geometry
            self.view.set_overlay_geometry(x, y, width, height)

    def quit_application(self):
        """Gracefully quit the application."""
        logging.info("Quitting application gracefully.")
        QApplication.quit()

    def toggle_overlay_visibility(self):
        """Toggle the visibility of the entire overlay."""
        if self.view.isVisible():
            logging.info("Hiding the overlay.")
            self.view.hide()
        else:
            logging.info("Showing the overlay.")
            self.view.show()