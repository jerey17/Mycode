import sys
import random

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIntValidator, QKeySequence
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QMessageBox, QAction

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
        self.dice_number.editingFinished.connect(self.dice_changed)
        self.dice_size.editingFinished.connect(self.dice_changed)

        number_validator = QIntValidator()
        number_validator.setBottom(1)
        self.dice_number.setValidator(number_validator)
        self.dice_size.setValidator(number_validator)

        # Now let's add a button for quitting the application.
        self.q = QPushButton("Quit")
        self.q.clicked.connect(self.quit)

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
        layout.addWidget(self.q)

        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)
        
        # Add a menu bar to provide an alternative way of accessing different functions.
        # First, get the menu bar from the window.
        menus = self.menuBar()
        # Then add a menu to the menu bar.
        file_menu = menus.addMenu("&File")
        # Now we can define actions to go on the menu.
        quit_action = QAction("&Quit", self)
        # Specify what the action does.
        quit_action.triggered.connect(self.quit)
        # Give it a keyboard shortcut.
        quit_action.setShortcut(QKeySequence("Ctrl+q"))
        # Actually add the action to the menu.
        file_menu.addAction(quit_action)
        
    def roll(self):
        number = int(self.dice_number.text())
        size = int(self.dice_size.text())
        total = 0
        for n in range(number):
            total = total + random.randint(1, size)
        self.res.setText("You rolled:" + str(total))

    def dice_changed(self):
        self.max.setText("Maximum possible:" + str(int(self.dice_number.text()) * int(self.dice_size.text())))

    def quit(self):
        # Use a dialogue box to ask if the user really wants to quit.
        really = QMessageBox.question(self, "Quit?", "Do you really want to quit?")
        # Check what button was pressed.
        if really == QMessageBox.StandardButton.Yes:
            self.close()

        
app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()

