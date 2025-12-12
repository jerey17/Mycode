import sys

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dice, Dice, Baby!")

        # Create a button widget.
        x = QPushButton("Let's Roll!")

        self.setCentralWidget(x)
        
app = QApplication(sys.argv)

window = MainWindow()
window.show()

window.setMinimumSize(640,480)

app.exec()

