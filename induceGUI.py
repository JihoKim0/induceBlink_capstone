from calendar import c
import sys
from PyQt5.QtWidgets import *
#QMainWindow, QApplication, QWidget, QTabWidget, QLabel, QVBoxLayout, QHboxLayout, QRadioButton, Grid
import printAlert as pA

class BlinkApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowTitle('Induce Blink Program')
        self.setFixedSize(1000, 800)

    def initUI(self):
        tabs = QTabWidget()
        tabs.addTab(self.tab1(), 'Settings')
        tabs.addTab(self.tab2(), 'Transition')
        self.setCentralWidget(tabs)

    def tab1(self):
        #power radio button
        grid = QGridLayout()
        self.setLayout(grid)
        grid.addWidget(QLabel('전원'), 0, 0)
        rbtn1 = QRadioButton('ON', self)
        grid.addWidget(rbtn1, 0, 1)
        rbtn2 = QRadioButton('OFF', self)
        grid.addWidget(rbtn2, 0, 2)

        #set seconds
        grid.addWidget(QLabel('깜빡임 간격'), 1, 0)
        second = QLineEdit(self)
        second.setFixedWidth(100)
        grid.addWidget(second, 1, 1)

        #alert type(use combobox)
        grid.addWidget(QLabel('알림 종류'), 2, 0)
        cb = QComboBox(self)
        cb.addItem('소리 알림')
        cb.addItem('시스템 알림')
        cb.addItem('아이콘 알림')
        grid.addWidget(cb, 2, 1)
        #default button
        dbtn = QPushButton('DEFAULT', self)
        dbtn.setFixedWidth(100)
        grid.addWidget(dbtn, 3, 1)




        tab = QWidget()
        tab.setLayout(grid)
        return tab


    def tab2(self):
        tab = QWidget()
        return tab



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = BlinkApp()
    ex.show()
    sys.exit(app.exec_())