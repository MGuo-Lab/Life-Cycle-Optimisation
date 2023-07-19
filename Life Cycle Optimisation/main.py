import sys

from PyQt6.QtWidgets import QApplication

from ui.MainWindow import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.app = app
    mainWindow.show()
    app.exec()
    sys.exit()
