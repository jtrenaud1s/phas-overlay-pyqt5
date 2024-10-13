from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QGridLayout
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QMetaObject, QUrl
from PyQt5.QtGui import QPainter, QColor, QPen

import os
import sys

import logging


class SmudgeBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""QProgressBar { 
          background-color: rgba(70, 70, 70, 1); 
          border-radius: 0px; 
        }

        QProgressBar::chunk {
           background-color: rgba(255, 255, 255, 1); 
           border-radius: 0px; 
           width: 1px;
           }
        """)
        self.setRange(0, 180)
        self.setValue(180)
        self.setTextVisible(False)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(int(self.width() / 2), 0, int(self.width() / 2), self.height())
        painter.drawLine(int(self.width() * 2 / 3), 0, int(self.width() * 2 / 3), self.height())

class SmudgeTimer(QWidget):
    #time_updated = pyqtSignal(int)

    def __init__(self, parent=None, total_time=180):
        super().__init__(parent)
        self.total_time = total_time
        self.remaining_time = total_time

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.setInterval(1000)

        audio_file = self.resource_path("countdown.mp3")

        self.countdown_audio = QMediaPlayer()
        self.countdown_audio.setMedia(QMediaContent(QUrl.fromLocalFile(audio_file)))

        self.progress_bar = SmudgeBar(self)

        layout = QGridLayout()
        
        # Add a label for the progress bar
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: white; font-size: 16pt; background-color: rgba(0, 0, 0, 0);")
        self.label.setText(self.format_time(self.remaining_time))

        self.ghost_label = QLabel(self)
        self.ghost_label.setAlignment(Qt.AlignCenter)
        self.ghost_label.setStyleSheet("color: white; font-size: 16pt; background-color: rgba(0, 0, 0, 0);")
        self.ghost_label.setText("None")

        self.timer_state_label = QLabel(self)
        self.timer_state_label.setFixedSize(10, 10)  # Set a fixed size for the label
        self.timer_state_label.setStyleSheet("background-color: red; border-radius: 10px;")        

        # Add the progress bar and label widgets to a container widget
        self.container = QWidget(self)
        self.container.setStyleSheet("background-color: rgba(70, 70, 70, 0); border-radius: 0px;")
        self.container_layout = QGridLayout(self.container)
        # self.container_layout.setContentsMargins(10, 10, 10, 10)

        self.container_layout.addWidget(self.progress_bar, 0, 0)
        self.container_layout.addWidget(self.timer_state_label, 1, 0)
        self.container_layout.addWidget(self.label, 1, 0, Qt.AlignCenter)
        self.container_layout.addWidget(self.ghost_label, 2, 0, Qt.AlignCenter)

        self.setLayout(self.container_layout)

    def start(self):
        QMetaObject.invokeMethod(self.timer, "start", Qt.QueuedConnection)
        self.timer_state_label.setStyleSheet("background-color: green; border-radius: 10px;")

    def stop(self):
        QMetaObject.invokeMethod(self.timer, "stop", Qt.QueuedConnection)
        self.timer_state_label.setStyleSheet("background-color: red; border-radius: 10px;")
        self.countdown_audio.stop()

    def reset(self):
        self.remaining_time = self.total_time
        self.progress_bar.setValue(self.remaining_time)
        self.label.setText(self.format_time(self.remaining_time))
        self.ghost_label.setText("None")
        self.ghost_label.setStyleSheet("color: white; font-size: 16pt; background-color: rgba(0, 0, 0, 0);")

    def update_time(self):
        self.remaining_time -= 1
        self.progress_bar.setValue(self.remaining_time)
        self.label.setText(self.format_time(self.remaining_time))

        # play audio after 1 minute, 1.5 minutes, and 3 minutes. the audio clip counts 5 4 3 2 1 ding, the ding should play at the prior specified times with that offset.
        if self.remaining_time == 125:
            self.countdown_audio.play()
        elif self.remaining_time == 95:
            self.countdown_audio.play()
        elif self.remaining_time == 5:
            self.countdown_audio.play()

        if self.remaining_time <= 0:  # 3 minutes elapsed
            self.ghost_label.setText("Spirit")
            self.ghost_label.setStyleSheet("color: white; font-size: 16pt; background-color: rgba(0, 0, 0, 0);")
        elif self.remaining_time <= 90:  # 1:30 minutes elapsed
            self.ghost_label.setText("Standard")
            self.ghost_label.setStyleSheet("color: yellow; font-size: 16pt; background-color: rgba(0, 0, 0, 0);")
        elif self.remaining_time <= 120:  # 1 minute elapsed
            self.ghost_label.setText("Demon")
            self.ghost_label.setStyleSheet("color: red; font-size: 16pt; background-color: rgba(0, 0, 0, 0);")
        elif self.remaining_time <= 180:  # 1 minute elapsed
            self.ghost_label.setText("None")
            self.ghost_label.setStyleSheet("color: white; font-size: 16pt; background-color: rgba(0, 0, 0, 0);")

        self.container.setStyleSheet("background-color: rgba(70, 70, 70, 0); border-radius: 0px;")
        
        if self.remaining_time <= 0:
            self.stop()

    def format_time(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:01d}:{seconds:02d}"
    
    def resource_path(self, relative_path):
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)