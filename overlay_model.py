# overlay_model.py

import logging
import pygetwindow as gw

class OverlayModel:
    def __init__(self, game_name):
        self.game_name = game_name
        self.game_window = None
        logging.debug("OverlayModel initialized with game name.")

    def find_game_window(self):
        logging.debug("Attempting to find game window.")
        try:
            windows = gw.getWindowsWithTitle(self.game_name)
            if windows:
                self.game_window = windows[0]
                logging.info("Game window found.")
                return True
            else:
                logging.warning("Game window not found.")
                return False
        except Exception as e:
            logging.error(f"Error finding game window: {e}")
            return False

    def get_game_window_geometry(self):
        if self.game_window:
            return self.game_window.left, self.game_window.top, self.game_window.width, self.game_window.height
        return None