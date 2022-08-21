import cv2
import dlib
import numpy as np
from imutils import face_utils
from tensorflow.keras.models import load_model
import time
import winsound as sd
import os
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
#QMainWindow, QApplication, QWidget, QTabWidget, QLabel, QVBoxLayout, QHboxLayout, QRadioButton, Grid
import recognition as rcg
from matplotlib.backends.backend_qt5agg import FigureCanvas as fcanva
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as navi
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from pylab import show
import datetime
import sqlite3

con = sqlite3.connect('practice.db')


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

class BlinkApp(QMainWindow):
    blink = rcg.blinkThread()
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowTitle('Induce Blink Program')
        self.setFixedSize(1000, 800)
        
    def closeEvent(self, event):
        if rcg.alert.active == 0:
            self.blink.stop()

    def initUI(self):
        tabs = QTabWidget()
        tabs.addTab(self.tab1(), 'Settings')
        tabs.addTab(self.tab2(), 'blink')
        #tabs.addTab(self.tab3(), 'recognition time')
        self.setCentralWidget(tabs)
        
#setFont QFont 써보기
    def tab1(self):
        grid = QGridLayout()
        self.setLayout(grid)

        #power radio button        
        grpPower = QGroupBox('전원')
        pwr1 = QRadioButton('ON', self)
        pwr2 = QRadioButton('OFF', self)
        pwr1.toggled.connect(self.On)
        pwr2.toggled.connect(self.Off)
        pwr1.setChecked(True)
        power_layout = QBoxLayout(QBoxLayout.LeftToRight)
        grpPower.setLayout(power_layout)
        power_layout.addWidget(pwr1)
        power_layout.addWidget(pwr2)
        grpPower.setFixedSize(200, 180)
        grid.addWidget(grpPower, 0, 0)

        #set seconds
        grpSec = QGroupBox('깜빡임 간격')
        sbtn1 = QPushButton('▼', self)
        sbtn2 = QPushButton('▲', self)
        sbtn1.clicked.connect(self.decrease)
        sbtn2.clicked.connect(self.increase)
        self.labelNum = QLabel(str(rcg.alert.time))
        labelSec = QLabel('초')
        seconds_layout = QBoxLayout(QBoxLayout.LeftToRight)
        grpSec.setLayout(seconds_layout)
        seconds_layout.addWidget(sbtn1)
        seconds_layout.addWidget(self.labelNum)
        seconds_layout.addWidget(labelSec)
        seconds_layout.addWidget(sbtn2)
        grpSec.setFixedSize(200, 180)
        grid.addWidget(grpSec, 0, 1)

        #alert type
        grpType = QGroupBox('알림 종류')
        type1 = QRadioButton('beep', self)
        type2 = QRadioButton('mute', self)
        type1.setChecked(True)
        type1.toggled.connect(self.beep)
        type2.toggled.connect(self.mute)
        type_layout = QBoxLayout(QBoxLayout.LeftToRight)
        grpType.setLayout(type_layout)
        type_layout.addWidget(type1)
        type_layout.addWidget(type2)
        grpType.setFixedSize(200, 180)
        grid.addWidget(grpType, 1, 0)

        #default button
        dbtn = QPushButton('DEFAULT', self)
        dbtn.setFixedWidth(100)
        dbtn.setFixedSize(200, 100)
        grid.addWidget(dbtn, 1, 1.1)
        dbtn.clicked.connect(self.default)

        tab = QWidget()
        tab.setLayout(grid)
        return tab
    
    def On(self):
        rcg.alert.activate(1)
        self.blink.start()

    def Off(self):
        rcg.alert.activate(0)
        self.blink.stop()
        with con:
            cur = con.cursor()
            D = datetime.date.today()
            cur.execute("select recognition from EYEDATA where day = '%s'" % D)
            recog_time = cur.fetchone()
            if recog_time:
                rcg.alert.total_time = rcg.alert.total_time + recog_time[0]
            
            cur.execute("select blink_count from EYEDATA where day = '%s'" % D)
            blinkCnt = cur.fetchone()
            if blinkCnt:
                rcg.alert.total_blink = rcg.alert.total_blink + blinkCnt[0]

            total_time = rcg.alert.total_time
            blink_count = rcg.alert.total_blink
            cur.execute("insert or replace into EYEDATA values('%s', %d, %d)" % (D, total_time, blink_count))


    def decrease(self):
        rcg.alert.time -= 1
        self.labelNum.setText(str(rcg.alert.time))

    def increase(self):
        rcg.alert.time += 1
        self.labelNum.setText(str(rcg.alert.time))

    def beep(self):
        rcg.alert.alertType(0)

    def mute(self):
        rcg.alert.alertType(1)

    def default(self):
        rcg.alert.time = 3
        self.labelNum.setText(str(rcg.alert.time))
    
    def tab2(self):
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        canvas = fcanva(Figure(figsize=(4, 3)))
        vbox = QVBoxLayout(self.main_widget)
        vbox.addWidget(canvas)

        #fetch last 7 days data
        cur = con.cursor()
        cur.execute("SELECT day, recognition, blink_count FROM EYEDATA ORDER BY day DESC limit 7")
        data = cur.fetchall()
        day = []
        recognition = []
        blink_count = []
        for row in data:
            day.append(row[0])
            recognition.append(row[1])
            blink_count.append(row[2])
        #rearrangement datas
        day.reverse()
        recognition.reverse()
        blink_count.reverse()
        self.ax = canvas.figure.subplots()
        self.ax.bar(day, blink_count, color = 'green', alpha = 0.3)
        self.ax2 = self.ax.twinx()
        self.ax2.plot(day, recognition, color = 'purple')      
        for i in range(0, len(day)):
            self.ax2.text(i, recognition[i], recognition[i], color='purple', size=15, ha="left")
            self.ax.text(i, blink_count[i], blink_count[i], color='green', size=13, ha="right")
        self.show()

        tab = QWidget()
        tab.setLayout(vbox)
        return tab

    '''def tab3(self):
        grid = QGridLayout()
        self.setLayout(grid)

        refreshBtn = QPushButton('🔄️', self)
        refreshBtn.clicked.connect()
        grid.addWidget()

        tab = QWidget()
        tab.setLayout(grid)
        return tab
    
    def graph(self, x, y):
        with con:
            cur = con.cursor()
            cur.execute("SELECT day, blink_count FROM EYEDATA")
            data = cur.fetchall()
            day = []
            blink_count = []
            for row in data:
                day.append(row[0])
                blink_count.append(row[1])
            self.ax = canvas.figure.subplots()
            self.ax.plot(day, blink_count)
            self.show()'''



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = BlinkApp()
    ex.show()
    sys.exit(app.exec_())