import sys
import os
import ctypes
from PyQt5.QtWidgets import QApplication, QMessageBox, QWidget
from PyQt5.QtCore import QTime, QTimer, QRect
from game_overlay import GameOverlay
import signal
import json
from logger import log
import traceback

class PhasOverlay(QWidget):
    overlay = None

    def __init__(self):
        super().__init__()
        log.info("PhasOverlay::__init__()")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_target_window)
        log.info("PhasOverlay::__init__() - Waiting for game to start...")
        self.timer.start(1000)  # Check every second
        self.time_elapsed = QTime(0, 0)
        

    def check_target_window(self):
            log.debug("PhasOverlay::check_target_window()")
            hwnd = ctypes.windll.user32.FindWindowW(None, "Phasmophobia")
            if hwnd:
                log.info("PhasOverlay::check_target_window() - Game found!")
                rect = ctypes.wintypes.RECT()
                ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
                log.info("PhasOverlay::check_target_window() - Game window rect: " + str(rect))
                self.overlay = GameOverlay(rect)
                self.overlay.show()
                self.timer.stop()
            else:
                self.time_elapsed = self.time_elapsed.addSecs(1)
                if self.time_elapsed >= QTime(0, 2):  # 2 minutes
                    self.timer.stop()
                    log.info("PhasOverlay::check_target_window() - Game not found within 2 minutes. Exiting...")
                    QMessageBox.information(self, "Game Not Found", "The Phasmophobia game was not found within the specified time (2 minutes).")
                    self.quit_application()


def generate_default_config():
    if not os.path.exists('config.json'):
        log.info("generate_default_config() - Generating default config file...")
        with open('config.json', 'w') as f:
            json.dump({
              'toggle_timer': 't',
              'toggle_crosshair': 'ctrl_l+shift+c',
              'toggle_settings': 'ctrl_l+shift+s', 
              'toggle_visibility': 'ctrl_l+shift+a', 
              'toggle_edit_mode': 'ctrl_l+shift+e',
              'quit': 'ctrl_l+shift+q'
              }, f, indent=4)

def signal_handler(signal, frame):
    log.info("signal_handler() - Ctrl+C pressed. Exiting...")
    sys.exit(0)

def excepthook(exc_type, exc_value, exc_tb):
    tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("Exception caught: ", tb_str)

# Install exception hook
sys.excepthook = excepthook


if __name__ == '__main__':
    generate_default_config()
    signal.signal(signal.SIGINT, signal_handler)

    app = QApplication(sys.argv)
    phasOverlay = PhasOverlay()
    
    sys.exit(app.exec_())