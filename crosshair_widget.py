# crosshair_widget.py

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor

class CrosshairWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Set widget to be small and centered with a lime-green dot
        self.setFixedSize(10, 10)  # Adjust size as needed
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setVisible(False)  # Initially hidden

    def paintEvent(self, event):
        # Paint a lime-green dot in the center
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(0, 255, 0))  # Lime green color
        painter.setPen(Qt.NoPen)
        # Draw a circle in the center
        painter.drawEllipse(int(self.width() / 2) - 3, int(self.height() / 2) - 3, 6, 6)
