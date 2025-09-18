import cv2
import time
import threading
import numpy as np
from datetime import datetime, timedelta
from flask import Flask, render_template, Response, jsonify
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import UniqueConstraint

#Shared State
frames = {}
for i, cap in caps.item():
    ret, frame = cap.read()
    if not ret:
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
    else:
        frame = cv2.resize(frame, (640, 480))
    frames[i] = frame


    # signal timing setup
    base_time = 30
    signal_index = 0
    signal_timer = base_time
    last_update = time.time()

    # Thread safety lock
    lock = threading.Lock()

# Helper Functions
def process_frame_simple(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3,3), 0)
    _, th1 = cv2.threshold(blur, 50,255, cv2.THRESH_BINARY_INV)
    _, th2 = cv2.threshold(blur, 100,255, cv2.THRESH_BINARY_INV)
    thresh = cv2.bitwise_or(th1, th2)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    count = 0
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
        ar = w / h if h > 0 else 0
        if 200 < area < 80000 and 0.3 < ar < 8.0:
            count += 1
    return count
def draw_traffic_light(frame, state):
    colors = {"RED": (0,0,255), "YELLOW": (0,255,255), "GREEN": (0,255,0)}
    x, y, radius = 50, 50, 15
    cv2.circle(frame, (x, y), radius, colors["RED"] if state == "RED" else (50,50,50), -1)
    cv2.circle(frame, (x, y + 40), radius, colors["YELLOW"] if state == "YELLOW" else (50,50,50), -1)
    cv2.circle(frame, (x, y + 80), radius, colors["GREEN"] if state == "GREEN" else (50,50,50), -1)
    for shift in [0, 40, 80]:
        cv2.circle(frame, (x, y + shift), radius, (255,255,255), 2)
    return frame