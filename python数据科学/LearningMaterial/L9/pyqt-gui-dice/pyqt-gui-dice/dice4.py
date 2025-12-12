import sys
import random

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton

# Diversion: using events/handlers instead of signals/slots.

# This custom button class subclasses the provided one.
class DiceButton(QPushButton):
    def mouseReleaseEvent(self, e):
        self.setText(str(random.randint(7,12)))
        # If we ignore the event, it will bubble up to the parent,
        # triggering another event handler.
        e.ignore()
    
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dice, Dice, Baby!")

        self.b = DiceButton("Let's Roll!")
        self.b.setFixedSize(200,100)

        self.setCentralWidget(self.b)

    def mouseReleaseEvent(self, e):
        self.setWindowTitle(str(random.randint(1,6)))        
        
app = QApplication(sys.argv)

window = MainWindow()
window.show()

window.setMinimumSize(640,480)

app.exec()

