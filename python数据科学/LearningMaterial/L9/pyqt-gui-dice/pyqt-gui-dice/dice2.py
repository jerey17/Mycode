import sys
import random

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dice, Dice, Baby!")

        # Create a button widget.
        # We save the pointer in self, so we can refer back to it later.
        self.b = QPushButton("Let's Roll!")
        # Connect the "clicked" signal to the "roll" slot below.
        self.b.clicked.connect(self.roll)
        # Make it look prettier?
        self.b.setFixedSize(200,100)

        self.setCentralWidget(self.b)
        
    def roll(self):
        # Self here is the MainWindow class...
        # ...which contains the pointer to the button.
        self.b.setText(str(random.randint(1,6)))        
        
app = QApplication(sys.argv)

window = MainWindow()
window.show()

window.setMinimumSize(640,480)

app.exec()

