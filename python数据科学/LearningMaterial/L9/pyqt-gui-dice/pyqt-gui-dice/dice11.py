import sys
import random

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dice, Dice, Baby!")

        self.b = QPushButton("Let's Roll!")
        self.b.clicked.connect(self.roll)

        self.res = QLabel("You rolled: Nothing yet.")
        self.dice_number = QLineEdit("1")
        self.dice_size = QLineEdit("6")

        self.max = QLabel("Maximum possible: 6")
        # Use the editingFinished signal to send the signal only for valid inputs.
        self.dice_number.editingFinished.connect(self.dice_changed)
        self.dice_size.editingFinished.connect(self.dice_changed)

        number_validator = QIntValidator()
        number_validator.setBottom(1)
        self.dice_number.setValidator(number_validator)
        self.dice_size.setValidator(number_validator)

        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Roll:"))
        input_layout.addWidget(self.dice_number)
        input_layout.addWidget(QLabel("d"))
        input_layout.addWidget(self.dice_size)
        input_widget = QWidget()
        input_widget.setLayout(input_layout)
        
        layout = QVBoxLayout()
        layout.addWidget(input_widget)
        layout.addWidget(self.b)
        layout.addWidget(self.res)
        layout.addWidget(self.max)

        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)
        
    def roll(self):
        number = int(self.dice_number.text())
        size = int(self.dice_size.text())
        total = 0
        for n in range(number):
            total = total + random.randint(1, size)
        self.res.setText("You rolled:" + str(total))

    def dice_changed(self):
        self.max.setText("Maximum possible:" + str(int(self.dice_number.text()) * int(self.dice_size.text())))
        
app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()

