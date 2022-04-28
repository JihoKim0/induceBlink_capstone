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

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

IMG_SIZE = (34, 26)
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
model = load_model('2022_03_08_18_29_49.h5')

class blinkThread(QThread):
    def __init__(self):
        super().__init__()
        self.power = True

    def run(self):
        #if self.power:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        while cap.isOpened() and alert.active == 1:
            #print('1')
            ret, img_cam = cap.read()
            if not ret:
                break
            img = img_cam.copy()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)
            
            for face in faces:
                shapes = predictor(gray, face)
                shapes = face_utils.shape_to_np(shapes)
                eye_img_l, eye_rect_l = crop_eye(gray, eye_points=shapes[36:42])
                eye_img_r, eye_rect_r = crop_eye(gray, eye_points=shapes[42:48])
                eye_img_l = cv2.resize(eye_img_l, dsize=IMG_SIZE)
                eye_img_r = cv2.resize(eye_img_r, dsize=IMG_SIZE)
                eye_img_r = cv2.flip(eye_img_r, flipCode=1)
                eye_input_l = eye_img_l.copy().reshape((1, IMG_SIZE[1], IMG_SIZE[0], 1)).astype(np.float32) / 255.
                eye_input_r = eye_img_r.copy().reshape((1, IMG_SIZE[1], IMG_SIZE[0], 1)).astype(np.float32) / 255.
                pred_l = model.predict(eye_input_l)
                pred_r = model.predict(eye_input_r)
                # visualize
                state_l = 'O %.1f' if pred_l > 0.1 else '- %.1f'
                state_r = 'O %.1f' if pred_r > 0.1 else '- %.1f'
                state_l = state_l % pred_l
                state_r = state_r % pred_r 
                #pred_l && pred_r < 0.5 -> return Blink alert sign
                if pred_l < 0.3 and pred_r < 0.3:
                    alert.start = time.time()
                if (time.time() - alert.start) > alert.time:
                    beepsound()
                    print('beep')
                    alert.start = time.time()

    def stop(self):
        self.power = False
        self.quit()
        self.wait(1000)

class BlinkApp(QMainWindow):
    blink = blinkThread()
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowTitle('Induce Blink Program')
        self.setFixedSize(1000, 800)
        
    def closeEvent(self, event):
        if alert.active == 0:
            self.blink.stop()

    def initUI(self):
        tabs = QTabWidget()
        tabs.addTab(self.tab1(), 'Settings')
        tabs.addTab(self.tab2(), 'Transition')
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
        self.labelNum = QLabel(str(alert.time))
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
        alert.activate(1)
        self.blink.start()

    def Off(self):
        alert.activate(0)
        self.blink.stop()

    def decrease(self):
        alert.time -= 1
        self.labelNum.setText(str(alert.time))

    def increase(self):
        alert.time += 1
        self.labelNum.setText(str(alert.time))

    def beep(self):
        alert.alertType(0)

    def mute(self):
        alert.alertType(1)

    def default(self):
        alert.time = 3
        self.labelNum.setText(str(alert.time))

    def tab2(self):
        tab = QWidget()
        return tab

#알림 관련 클래스
class Alert:
    active = 1
    start = 0
    time = 3
    type = 0

    def activate(self, on): #activate alert
        self.active = on
    def alertType(self, t):
        self.type = t

#Alert 클래스 선언
alert = Alert()

def beepsound():
    fr = 300 #frequency, range : 37~32767
    du = 200 #duration, 100ms==1second
    if alert.active == 1 and alert.type == 0:
        sd.Beep(fr, du)

def crop_eye(img, eye_points):
    x1, y1 = np.amin(eye_points, axis=0)
    x2, y2 = np.amax(eye_points, axis=0)
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    w = (x2 - x1) * 1.2
    h = w * IMG_SIZE[1] / IMG_SIZE[0]
    margin_x, margin_y = w / 2, h / 2
    min_x, min_y = int(cx - margin_x), int(cy - margin_y)
    max_x, max_y = int(cx + margin_x), int(cy + margin_y)
    eye_rect = np.rint([min_x, min_y, max_x, max_y]).astype(np.int)
    eye_img = img[eye_rect[1]:eye_rect[3], eye_rect[0]:eye_rect[2]]
    return eye_img, eye_rect



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = BlinkApp()
    ex.show()
    sys.exit(app.exec_())