import cv2
import time
import threading
import numpy as np
from flask import Flask, render_template, Response, jsonify

#Logging thread
def log_vehicle_counts():
    while True:
        now = datetime.now()
        next_minute = (now.replace(second=0, microsecond=0) + timedelta(minutes=1))
        wait_seconds = (next_minute - now).total_seconds()
        time.sleep(wait_seconds)
        ts = datetime.now().replace(second = 0, microsecond = 0)
        with app.app_context():
            with lock:
                for lane_zero_index, count in vehicle_counts.items():
                    log = VehicleLog(lane=lane_zero_index + 1, vehicles=int(count), timestamp=ts )
                    try:
                        db.session.add(log)
                        db.session.commit()
                    except Exception:
                        db.session.rollback()

# Video streaming
def gen_video(cam_id):
    global frames
    while True:
        with lock:
            frame = frames.get(cam_id)
            if frame is None:
                blank = np.zeros((480, 640, 3), dtype=np.uint8)
                ret, buffer = cv2.imencode('.jpg', blank)
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.03)

@app.route('/video_feed/<int:cam_id>')
def video_feed(cam_id):
    if cam_id not in caps:
        return "Camera not found", 404
    return Response(gen_video(cam_id), mimetype='multipart/x-mixed-replace; boundary=frame')
