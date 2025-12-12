import sys
import random

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIntValidator, QKeySequence, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QMessageBox, QAction

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dice, Dice, Baby!")

        quit_action = QAction("&Quit", self)
        quit_action.triggered.connect(self.quit)
        quit_action.setShortcut(QKeySequence("Ctrl+q"))

        roll_action = QAction("&Roll", self)
        roll_action.triggered.connect(self.roll)
        roll_action.setShortcut(QKeySequence("Ctrl+r"))

        reset_action = QAction("Rese&t", self)
        reset_action.triggered.connect(self.reset)
        reset_action.setShortcut(QKeySequence("Ctrl+t"))

        self.b = QPushButton("Let's Roll!")
        self.b.clicked.connect(self.roll)

        self.res = QLabel("You rolled: Nothing yet.")
        self.dice_number = QLineEdit("1")
        self.dice_size = QLineEdit("6")

        self.max = QLabel("Maximum possible: 6")
        self.dice_number.editingFinished.connect(self.dice_changed)
        self.dice_size.editingFinished.connect(self.dice_changed)

        number_validator = QIntValidator()
        number_validator.setBottom(1)
        self.dice_number.setValidator(number_validator)
        self.dice_size.setValidator(number_validator)

        self.q = QPushButton("Quit")
        self.q.clicked.connect(self.quit)

        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Roll:"))
        input_layout.addWidget(self.dice_number)
        input_layout.addWidget(QLabel("d"))
        input_layout.addWidget(self.dice_size)
        input_widget = QWidget()
        input_widget.setLayout(input_layout)

        # Add a picture at the top of the program.
        logo = QLabel("Logo")
        # Load a pixmap with the picture.
        dice_pic = QPixmap("dice.png")
        # Then set it on the label.
        logo.setPixmap(dice_pic)
        logo.setMinimumSize(dice_pic.width(), dice_pic.height())
        logo.setAlignment(Qt.AlignHCenter)
        
        layout = QVBoxLayout()
        layout.addWidget(logo)
        layout.addWidget(input_widget)
        layout.addWidget(self.b)
        layout.addWidget(self.res)
        layout.addWidget(self.max)
        layout.addWidget(self.q)

        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)
        
        menus = self.menuBar()
        file_menu = menus.addMenu("&File")
        file_menu.addAction(roll_action)
        file_menu.addAction(reset_action)
        file_menu.addAction(quit_action)
        
    def roll(self):
        number = int(self.dice_number.text())
        size = int(self.dice_size.text())
        total = 0
        for n in range(number):
            total = total + random.randint(1, size)
        self.res.setText("You rolled: " + str(total))

    def dice_changed(self):
        self.max.setText("Maximum possible: " + str(int(self.dice_number.text()) * int(self.dice_size.text())))

    def reset(self):
        self.dice_number.setText("1")
        self.dice_size.setText("6")
        self.dice_changed()

    def quit(self):
        really = QMessageBox.question(self, "Quit?", "Do you really want to quit?")
        if really == QMessageBox.StandardButton.Yes:
            self.close()

        
app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()

