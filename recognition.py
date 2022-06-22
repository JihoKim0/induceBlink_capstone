import cv2
import dlib
import numpy as np
import time
import winsound as sd
from imutils import face_utils
from tensorflow.keras.models import load_model
import sys
from PyQt5.QtCore import *


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
            ret, img_cam = cap.read()
            if not ret:
                break
            img_cam = cv2.resize(img_cam, dsize=(0, 0), fx=0.6, fy=0.6)
            img = img_cam.copy()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)

            cv2.imshow('result', img)
            if cv2.waitKey(1) & 0xFF == 27:
                break
            
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
                    alert.start = time.time()

    def stop(self):
        self.power = False
        self.quit()
        self.wait(1000)


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