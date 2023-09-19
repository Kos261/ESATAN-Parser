import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QStyleFactory
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

class DarkModeApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dark Mode App")
        self.setGeometry(100, 100, 400, 200)

        self.init_ui()

    def init_ui(self):
        # Przycisk
        button = QPushButton("Przycisk", self)
        button.setGeometry(150, 100, 100, 30)

        # Tworzenie ciemnego motywu
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Highlight, QColor(142, 45, 197))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)

        # Ustawianie ciemnego motywu
        self.setPalette(dark_palette)

        # Ustawianie ciemnego stylu
        QApplication.setStyle(QStyleFactory.create('Fusion'))

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Ustawienie stylu Fusion

    window = DarkModeApp()
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
