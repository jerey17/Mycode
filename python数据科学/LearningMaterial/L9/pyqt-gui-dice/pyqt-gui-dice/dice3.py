import sys
import random

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton

# Diversion: using events/handlers instead of signals/slots.

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dice, Dice, Baby!")

        self.b = QPushButton("Let's Roll!")
        self.b.setFixedSize(200,100)

        self.setCentralWidget(self.b)

    # No need to connect this, as the superclass is set up to receive the event.        
    def mouseReleaseEvent(self, e):
        self.b.setText(str(random.randint(1,6)))        
        
app = QApplication(sys.argv)

window = MainWindow()
window.show()

window.setMinimumSize(640,480)

app.exec()

