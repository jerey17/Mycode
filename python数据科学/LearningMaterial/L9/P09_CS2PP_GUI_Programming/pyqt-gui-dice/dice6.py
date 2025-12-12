import sys
import random

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QLineEdit

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dice, Dice, Baby!")

        self.b = QPushButton("Let's Roll!")
        self.b.clicked.connect(self.roll)

        # Now let's give the option to enter how many dice and of what kind to roll.
        self.res = QLabel("You rolled: Nothing yet.")
        self.dice_number = QLineEdit("1")
        self.dice_size = QLineEdit("6")
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Number of dice:"))
        layout.addWidget(self.dice_number)
        layout.addWidget(QLabel("Size of dice:"))
        layout.addWidget(self.dice_size)
        layout.addWidget(self.b)
        layout.addWidget(self.res)

        # We need a wrapper widget to apply the layout to.
        w = QWidget()
        w.setLayout(layout)
        # Then we can put the wrapper widget as the central widget of the window.
        self.setCentralWidget(w)
        
    def roll(self):
        number = int(self.dice_number.text())
        size = int(self.dice_size.text())
        total = 0
        for n in range(number):
            total = total + random.randint(1, size)
        self.res.setText("You rolled:" + str(total))        
        
app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()

