import sys
from PyQt5.QtCore import Qt, QPoint, QRect, QSize
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QFrame, QLayout, QLayoutItem
import traceback

class CustomLayout(QLayout):
    def __init__(self, parent=None):
        super(CustomLayout, self).__init__(parent)
        self.items = []

    def addItem(self, item):
        self.items.append(item)

    def count(self):
        return len(self.items)

    def itemAt(self, index):
        if 0 <= index < len(self.items):
            return self.items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.items):
            return self.items.pop(index)
        return None

    def setGeometry(self, rect):
        pass

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        return self.geometry().size()

class ContainerWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.edit_mode = False
        self.initUI()

    def initUI(self):
        self.setFixedSize(200, 200)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        #self.layout.setContentsMargins(5, 5, 5, 5)  # 5px margin
        self.setStyleSheet("padding: 5px;")

        self.button = QPushButton('Button', self)
        self.layout.addWidget(self.button)

        self.label = QLabel('Label', self)
        self.layout.addWidget(self.label)

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
                for sibling in self.parentWidget().findChildren(ContainerWidget):
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

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Draggable Containers')
        self.setGeometry(100, 100, 800, 600)

        self.layout = CustomLayout()
        self.setLayout(self.layout)

        self.container1 = ContainerWidget()
        self.layout.addWidget(self.container1)

        self.container2 = ContainerWidget()
        self.layout.addWidget(self.container2)

        self.adjustContainerPositions()  # Adjust positions to prevent overlap

        self.toggle_button = QPushButton('Toggle Edit Mode', self)
        self.toggle_button.clicked.connect(self.toggleEditMode)
        self.layout.addWidget(self.toggle_button)

    def adjustContainerPositions(self):
        containers = self.findChildren(ContainerWidget)
        for i, container in enumerate(containers):
            container.move(10 + i * 210, 10)

    def toggleEditMode(self):
        if self.container1.edit_mode:
            self.container1.disableEditMode()
            self.container2.disableEditMode()
        else:
            self.container1.enableEditMode()
            self.container2.enableEditMode()


def excepthook(exc_type, exc_value, exc_tb):
    tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("Exception caught: ", tb_str)

# Install exception hook
sys.excepthook = excepthook

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())