import cv2
import time
import threading
import numpy as np
from flask import Flask, render_template, Response, jsonify

def log_vehicle_counts():
    while True:
        now = datetime.now()
        next_minute = (now.replace(second=0, microsecond=0) + timedelta(minutes=1))
        wait_seconds = (next_minute - now).total_seconds()


def gen_video(cam_id):
    global frames