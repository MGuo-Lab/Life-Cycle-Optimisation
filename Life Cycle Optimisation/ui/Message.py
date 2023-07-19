from PyQt6.QtWidgets import QMessageBox


class Message(QMessageBox):
    def __init__(self, text):
        super().__init__()
        self.setText(text)
        self.setIcon(QMessageBox.Icon.Warning)
