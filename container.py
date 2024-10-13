from PyQt5.QtWidgets import QVBoxLayout, QFrame
from PyQt5.QtCore import QRect, QPoint, QSize

class Container(QFrame):
    def __init__(self, widget, width, height):
        super().__init__()
        self.edit_mode = False
        self.initUI(widget, width, height)

    def initUI(self, widget, width, height):
        self.setFixedSize(width, height)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(widget)

        self.setStyleSheet("background-color: rgba(70, 70, 70, 0.3); border-radius: 0px;")

        
    def mousePressEvent(self, event):
        self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.edit_mode:
            margin = 5  # 5px margin
            new_pos = event.pos() - self.offset
            final_pos = self.pos() + new_pos

            parent_rect = self.parentWidget().rect().adjusted(10, 10, -10, -10)  # 10px padding for the main window

            new_x = final_pos.x()
            new_y = final_pos.y()

            def check_collision(test_rect):
                for sibling in self.parentWidget().findChildren(Container):
                    if sibling is not self:
                        sibling_rect = sibling.geometry().adjusted(-margin, -margin, margin, margin)
                        if sibling_rect.intersects(test_rect):
                            return True
                return False

            test_rect_x = QRect(QPoint(new_x - margin, self.y() - margin), self.size() + QSize(2 * margin, 2 * margin))
            test_rect_y = QRect(QPoint(self.x() - margin, new_y - margin), self.size() + QSize(2 * margin, 2 * margin))

            x_within_boundary = parent_rect.left() <= new_x - margin and new_x + self.width() + margin <= parent_rect.right()
            y_within_boundary = parent_rect.top() <= new_y - margin and new_y + self.height() + margin <= parent_rect.bottom()

            if x_within_boundary and not check_collision(test_rect_x):
                self.move(new_x, self.y())
            if y_within_boundary and not check_collision(test_rect_y):
                self.move(self.x(), new_y)

    def enableEditMode(self):
        self.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.setLineWidth(2)
        self.edit_mode = True

    def disableEditMode(self):
        self.edit_mode = False
        self.setFrameStyle(QFrame.NoFrame)