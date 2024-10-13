from PyQt5.QtWidgets import QLayout

class DraggableLayout(QLayout):
    def __init__(self, parent=None):
        super(DraggableLayout, self).__init__(parent)
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