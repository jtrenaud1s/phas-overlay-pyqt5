import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt
from pynput.keyboard import Controller, Key
from time import sleep

class ConfigWindow(QWidget):
    update_ui_signal = pyqtSignal(str)
    labelStyle = "color: white; font-size: 16pt; background-color: rgba(0, 0, 0, 0);"
    buttonStyle = """
    QPushButton {
        color: white; 
        font-size: 16pt; 
        background-color: rgba(0, 0, 0, 0); 
        border: 1px solid white; 
        border-radius: 0px;   
    }
    
    QPushButton:hover {
        background-color: rgba(255, 255, 255, 0.1);
    }
    QPushButton:pressed {
        background-color: rgba(255, 255, 255, 0.3);
    }
    """

    recordingButtonStyle = """
    QPushButton {
        color: white; 
        font-size: 16pt; 
        background-color: rgba(0, 0, 0, 0); 
        border: 1px solid red; 
        border-radius: 0px;   
    }
    """
    def __init__(self, game_overlay, keybind_manager):
        super().__init__()
        self.game_overlay = game_overlay
        self.keybind_manager = keybind_manager

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: rgba(70, 70, 70, 0.3); border-radius: 0px;")

        smudge_timer_pos = self.game_overlay.smudge_timer.pos()
        smudge_timer_width = self.game_overlay.smudge_timer.width() - 20
        self.resize(smudge_timer_width, self.sizeHint().height())
        self.move(smudge_timer_pos.x() + 10, smudge_timer_pos.y() + self.game_overlay.smudge_timer.height())

        layout = QVBoxLayout()

        self.timer_layout = QHBoxLayout()
        self.timer_label = QLabel('Toggle Timer:')
        self.timer_label.setStyleSheet(self.labelStyle)
        self.timer_button = QPushButton()
        self.timer_button.setStyleSheet(self.buttonStyle)
        self.timer_layout.addWidget(self.timer_label)
        self.timer_layout.addWidget(self.timer_button)
        layout.addLayout(self.timer_layout)

        self.toggle_layout = QHBoxLayout()
        self.toggle_label = QLabel('Toggle Visibility:')
        self.toggle_label.setStyleSheet(self.labelStyle)
        self.toggle_button = QPushButton()
        self.toggle_button.setStyleSheet(self.buttonStyle)
        self.toggle_layout.addWidget(self.toggle_label)
        self.toggle_layout.addWidget(self.toggle_button)
        layout.addLayout(self.toggle_layout)
        
        self.crosshair_layout = QHBoxLayout()
        self.crosshair_label = QLabel('Toggle Crosshair:')
        self.crosshair_label.setStyleSheet(self.labelStyle)
        self.crosshair_button = QPushButton()
        self.crosshair_button.setStyleSheet(self.buttonStyle)
        self.crosshair_layout.addWidget(self.crosshair_label)
        self.crosshair_layout.addWidget(self.crosshair_button)
        layout.addLayout(self.crosshair_layout)

        self.toggle_edit_mode_layout = QHBoxLayout()
        self.toggle_edit_mode_label = QLabel('Toggle Edit Mode:')
        self.toggle_edit_mode_label.setStyleSheet(self.labelStyle)
        self.toggle_edit_mode_button = QPushButton()
        self.toggle_edit_mode_button.setStyleSheet(self.buttonStyle)
        self.toggle_edit_mode_layout.addWidget(self.toggle_edit_mode_label)
        self.toggle_edit_mode_layout.addWidget(self.toggle_edit_mode_button)
        layout.addLayout(self.toggle_edit_mode_layout)
        
        self.settings_layout = QHBoxLayout()
        self.settings_label = QLabel('Show Settings:')
        self.settings_label.setStyleSheet(self.labelStyle)
        self.settings_button = QPushButton()
        self.settings_button.setStyleSheet(self.buttonStyle)
        self.settings_layout.addWidget(self.settings_label)
        self.settings_layout.addWidget(self.settings_button)
        layout.addLayout(self.settings_layout)
        
        self.quit_layout = QHBoxLayout()
        self.quit_label = QLabel('Quit:')
        self.quit_label.setStyleSheet(self.labelStyle)
        self.quit_button = QPushButton()
        self.quit_button.setStyleSheet(self.buttonStyle)
        self.quit_layout.addWidget(self.quit_label)
        self.quit_layout.addWidget(self.quit_button)
        layout.addLayout(self.quit_layout)
        
        self.setLayout(layout)
        
        self.load_current_keybinds()

        def record_timer_button():
            self.timer_button.setText('Press a key...')
            self.timer_button.setStyleSheet(self.recordingButtonStyle)
            self.record_keybind('toggle_timer')
        
        def record_crosshair_button():
            self.crosshair_button.setText('Press a key...')
            self.crosshair_button.setStyleSheet(self.recordingButtonStyle)
            self.record_keybind('toggle_crosshair')
        
        def record_toggle_button():
            self.toggle_button.setText('Press a key...')
            self.toggle_button.setStyleSheet(self.recordingButtonStyle)
            self.record_keybind('toggle_visibility')

        def record_toggle_edit_mode_button():
            self.toggle_edit_mode_button.setText('Press a key...')
            self.toggle_edit_mode_button.setStyleSheet(self.recordingButtonStyle)
            self.record_keybind('toggle_edit_mode')

        def record_quit_button():
            self.quit_button.setText('Press a key...')
            self.quit_button.setStyleSheet(self.recordingButtonStyle)
            self.record_keybind('quit')

        def record_settings_button():
            self.settings_button.setText('Press a key...')
            self.settings_button.setStyleSheet(self.recordingButtonStyle)
            self.record_keybind('toggle_settings')
        
        self.timer_button.clicked.connect(lambda: record_timer_button())
        self.crosshair_button.clicked.connect(lambda: record_crosshair_button())
        self.toggle_button.clicked.connect(lambda: record_toggle_button())
        self.toggle_edit_mode_button.clicked.connect(lambda: record_toggle_edit_mode_button())
        self.quit_button.clicked.connect(lambda: record_quit_button())
        self.settings_button.clicked.connect(lambda: record_settings_button())
        self.update_ui_signal.connect(self.update_ui)
    
    def load_current_keybinds(self):
        with open('config.json', 'r') as f:
            config = json.load(f)
            self.timer_button.setText(self.keybind_manager.chord_to_user_friendly(config['toggle_timer']))
            self.crosshair_button.setText(self.keybind_manager.chord_to_user_friendly(config['toggle_crosshair']))
            self.toggle_button.setText(self.keybind_manager.chord_to_user_friendly(config['toggle_visibility']))
            self.toggle_edit_mode_button.setText(self.keybind_manager.chord_to_user_friendly(config['toggle_edit_mode']))
            self.quit_button.setText(self.keybind_manager.chord_to_user_friendly(config['quit']))
            self.settings_button.setText(self.keybind_manager.chord_to_user_friendly(config['toggle_settings']))
    
    @pyqtSlot(str)
    def update_ui(self, chord):
        chord = self.keybind_manager.chord_to_user_friendly(chord)
        if self.current_action == 'toggle_visibility':
            self.toggle_button.setText(chord)
        elif self.current_action == 'toggle_timer':
            self.timer_button.setText(chord)
        elif self.current_action == 'toggle_crosshair':
            self.crosshair_button.setText(chord)
        elif self.current_action == 'toggle_edit_mode':
            self.edit_mode_button.setText(chord)
        elif self.current_action == 'quit':
            self.quit_button.setText(chord)
        elif self.current_action == 'toggle_settings':
            self.settings_button.setText(chord)

        self.timer_button.setStyleSheet(self.buttonStyle)
        self.current_action = None

    def on_record_keybind(self, action, chord):
        self.update_ui_signal.emit(chord)

    def record_keybind(self, action):
        self.current_action = action
        self.keybind_manager.record(action, self.on_record_keybind)
        
    def showEvent(self, event):
        super().showEvent(event)
        self.activateWindow()




