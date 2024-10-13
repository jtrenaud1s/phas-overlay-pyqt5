# smudge_timer.py

from PyQt5.QtWidgets import QWidget, QLabel, QProgressBar, QGridLayout, QVBoxLayout
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import Qt, QTimer, QUrl, QMetaObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPainter, QColor, QPen
import os
import sys

class SmudgeBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QProgressBar { 
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
        if painter.isActive():
            pen = QPen(QColor(0, 0, 0))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawLine(int(self.width() / 2), 0, int(self.width() / 2), self.height())
            painter.drawLine(int(self.width() * 2 / 3), 0, int(self.width() * 2 / 3), self.height())


class SmudgeTimer(QWidget):
    # Signals for starting and stopping the timer
    start_timer_signal = pyqtSignal()
    stop_timer_signal = pyqtSignal()

    def __init__(self, parent=None, total_time=180):
        super().__init__(parent)
        self.setFixedSize(400, 125)
        self.total_time = total_time
        self.remaining_time = total_time

        # Initialize timer and set up connections
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.setInterval(1000)

        # Connect signals to slots
        self.start_timer_signal.connect(self.start_timer)
        self.stop_timer_signal.connect(self.stop_timer)

        # Audio setup
        audio_file = self.resource_path("countdown.mp3")
        self.countdown_audio = QMediaPlayer()
        self.countdown_audio.setMedia(QMediaContent(QUrl.fromLocalFile(audio_file)))

        # Progress bar
        self.progress_bar = SmudgeBar(self)

        # Labels
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: white; font-size: 16pt; background-color: rgba(0, 0, 0, 0);")
        self.label.setText(self.format_time(self.remaining_time))

        self.ghost_label = QLabel(self)
        self.ghost_label.setAlignment(Qt.AlignCenter)
        self.ghost_label.setStyleSheet("color: white; font-size: 16pt; background-color: rgba(0, 0, 0, 0);")
        self.ghost_label.setText("None")

        self.timer_state_label = QLabel(self)
        self.timer_state_label.setFixedSize(10, 10)
        self.timer_state_label.setStyleSheet("background-color: red; border-radius: 5px;")

        # Layout setup
        self.container = QWidget(self)
        self.container.setFixedSize(400, 125)
        self.container.setStyleSheet("background-color: rgba(30, 30, 30, 0.8);")
        container_layout = QGridLayout(self.container)
        container_layout.setContentsMargins(10, 10, 10, 10)
        container_layout.addWidget(self.progress_bar, 0, 0)
        container_layout.addWidget(self.timer_state_label, 1, 0, Qt.AlignLeft)
        container_layout.addWidget(self.label, 1, 0, Qt.AlignCenter)
        container_layout.addWidget(self.ghost_label, 2, 0, Qt.AlignCenter)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

    @pyqtSlot()
    def start_timer(self):
        """Slot to start the timer safely on the main thread."""
        if not self.timer.isActive():
            self.timer.start()
            self.timer_state_label.setStyleSheet("background-color: green; border-radius: 5px;")

    @pyqtSlot()
    def stop_timer(self):
        """Slot to stop the timer safely on the main thread."""
        if self.timer.isActive():
            self.timer.stop()
            self.timer_state_label.setStyleSheet("background-color: red; border-radius: 5px;")
            self.countdown_audio.stop()
            self.reset()

    def reset(self):
        self.remaining_time = self.total_time
        self.progress_bar.setValue(self.remaining_time)
        self.label.setText(self.format_time(self.remaining_time))
        self.ghost_label.setText("None")
        self.ghost_label.setStyleSheet("color: white; font-size: 16pt; background-color: rgba(0, 0, 0, 0);")

    def update_time(self):
        if self.remaining_time <= 0:
            self.stop_timer_signal.emit()
            return

        self.remaining_time -= 1
        self.progress_bar.setValue(self.remaining_time)
        self.label.setText(self.format_time(self.remaining_time))

        if self.remaining_time in {125, 95, 5}:
            self.countdown_audio.play()

        # Update ghost label based on remaining time
        if self.remaining_time <= 0:
            self.ghost_label.setText("Spirit")
        elif self.remaining_time <= 90:
            self.ghost_label.setText("Standard")
            self.ghost_label.setStyleSheet("color: yellow; font-size: 16pt; background-color: rgba(0, 0, 0, 0);")
        elif self.remaining_time <= 120:
            self.ghost_label.setText("Demon")
            self.ghost_label.setStyleSheet("color: red; font-size: 16pt; background-color: rgba(0, 0, 0, 0);")

    def format_time(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:01d}:{seconds:02d}"

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
