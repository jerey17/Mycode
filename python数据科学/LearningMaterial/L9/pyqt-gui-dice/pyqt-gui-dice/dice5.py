import sys
import random

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dice, Dice, Baby!")

        self.b = QPushButton("Let's Roll!")
        self.b.clicked.connect(self.roll)

        # What if we want to put multiple widgets in a single window?
        # For example, show the result of rolling as a separate text label.
        self.res = QLabel("Result.")
        
        # To do this, we need to create a layout manager to control widget positions.
        layout = QVBoxLayout()
        # Add the widgets to the layout.
        layout.addWidget(self.b)
        layout.addWidget(self.res)

        # We need a wrapper widget to apply the layout to.
        w = QWidget()
        w.setLayout(layout)
        # Then we can put the wrapper widget as the central widget of the window.
        self.setCentralWidget(w)
        
    def roll(self):
        self.res.setText("You rolled:" + str(random.randint(1,6)))        
        
app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()

