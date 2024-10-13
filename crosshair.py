from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt

class Crosshair(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.show_crosshair = True

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.show_crosshair:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QColor(0, 255, 0))
            painter.setPen(QColor(0, 255, 0))
            painter.drawEllipse(int(self.width() / 2) - 5, int(self.height() / 2) - 5, 6, 6)

    def toggle_crosshair(self):
        self.show_crosshair = not self.show_crosshair
        self.update()