import cv2
import time
import threading
import numpy as np
from flask import Flask, render_template, Response, jsonify

# Frame update thread
def update_frames():
    global frames, vehicle_counts, states, signal_index, signal_timer, last_update
    while True:
        new_frames = {}
        counts = {}

        # lane groups
        if signal_index == 0:
            green_cams, red_cams = [0, 1], [2, 3]
        else:
            green_cams, red_cams = [2, 3], [0, 1]

        # process frames
        for i, cap in caps.items():
            if i in red_cams:
                with lock:
                    new_frames[i] = frames[i].copy()
                counts[i] = vehicle_counts[i]
                continue

            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()
                if not ret:
                    frame = np.zeros((480, 640, 3), dtype=np.uint8)

            frame = cv2.resize(frame, (640, 480))
            count = process_frame_simple(frame.copy())

            counts[i] = count
            new_frames[i] = frame

        elapsed = int(time.time() - last_update)
        remaining = max(0, signal_timer - elapsed)

# assign states
        for i in list(frames.keys()):
            if i in green_cams:
                states[i] = "YELLOW" if remaining <= 5 else "GREEN"
            else:
                states[i] = "RED"
            target_frame = new_frames.get(i, frames[i]).copy()
            target_frame = draw_traffic_light(target_frame, states[i])
            new_frames[i] = target_frame

        # ---- Adaptive Signal Timing ----
        if elapsed >= signal_timer:
            with lock:
                green_total = sum(vehicle_counts[i] for i in green_cams)
                red_total = sum(vehicle_counts[i] for i in red_cams)

            if green_total > 0 and red_total > 0:
                diff = abs(green_total - red_total) / min(green_total, red_total)
                if diff >= 0.0125:  # 1.25% more traffic
                    signal_timer = base_time + 15
                else:
                    signal_timer = base_time
            else:
                signal_timer = base_time

            signal_index = 1 - signal_index
            last_update = time.time()

        with lock:
            frames = new_frames
            vehicle_counts.update(counts)

        time.sleep(0.05)


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
