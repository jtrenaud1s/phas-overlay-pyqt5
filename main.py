import sys
import json
import logging
import signal
from PyQt5.QtWidgets import QApplication
from overlay_model import OverlayModel
from overlay_view import OverlayView
from overlay_controller import OverlayController
from keybind_manager import KeybindManager
from keybind_config_controller import KeybindConfigController

def setup_logging(log_config):
    logging.basicConfig(
        level=getattr(logging, log_config.get("level", "DEBUG").upper(), None),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def load_config():
    with open("config.json", "r") as f:
        config = json.load(f)
    setup_logging(config.get("logging", {}))
    logging.debug("Configuration loaded successfully")
    return config

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Set SIGINT to default for Ctrl+C handling
    config = load_config()
    
    app = QApplication(sys.argv)
    
    model = OverlayModel(config.get("game_name", "Phasmophobia"))
    keybind_manager = KeybindManager(model, config.get("keybinds", {}), config.get("cooldowns", {}))
    keybind_config_controller = KeybindConfigController(keybind_manager, config_file='config.json')
    view = OverlayView(config.get("ui", {}), keybind_manager, keybind_config_controller)
    controller = OverlayController(model, view, keybind_manager, config.get("cooldowns", {}))
    
    controller.start()
    sys.exit(app.exec_())