import json
import logging

class KeybindConfigModel:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.load_config()

    def load_config(self):
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        self.keybinds = config.get("keybinds", {})

    def save_config(self):
        with open(self.config_file, 'r+') as f:
            config = json.load(f)
            config["keybinds"] = self.keybinds
            f.seek(0)
            json.dump(config, f, indent=4)
            f.truncate()
        logging.info("Keybind configuration saved to file.")

    def update_keybind(self, action, new_keybind):
        self.keybinds[action] = new_keybind
        logging.info(f"Updated keybind for {action}: {new_keybind}")
        self.save_config()
