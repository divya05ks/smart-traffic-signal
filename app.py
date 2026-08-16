from flask import Flask, jsonify
from flask_cors import CORS
import cv2
import threading
import time
from ultralytics import YOLO

app = Flask(__name__)
CORS(app)  # Allows your Vercel app to fetch data from this server

# Global storage for live telemetry
latest_telemetry = {
    "junction_id": "Anna Salai Junction #1 (Chennai)",
    "pcu_load": 0,
    "vehicle_counts": {"motorcycle": 0, "car": 0, "autorickshaw": 0, "bus": 0, "truck": 0, "pedestrian": 0},
    "green_time": 30,
    "route_status": "System Initializing...",
    "emergency_alert": False
}

# 1. AI Processing Loop in Background Thread
def run_ai_loop():
    global latest_telemetry
    model = YOLO('yolov8n.pt')
    cap = cv2.VideoCapture('traffic.mp4')
    
    PCU_WEIGHTS = {'motorcycle': 0.5, 'car': 1.0, 'bus': 2.2, 'truck': 2.2, 'person': 0.2}
    current_green = 30

    while True:
        if not cap.isOpened():
            cap = cv2.VideoCapture('traffic.mp4')
            
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        results = model(frame, verbose=False)[0]
        counts = {'motorcycle': 0, 'car': 0, 'autorickshaw': 0, 'bus': 0, 'truck': 0, 'pedestrian': 0}
        emergency = False

        for box in results.boxes:
            cname = model.names[int(box.cls[0])]
            if cname in ['motorbike', 'motorcycle']: counts['motorcycle'] += 1
            elif cname == 'car': counts['car'] += 1
            elif cname == 'bus': counts['bus'] += 1
            elif cname == 'truck': counts['truck'] += 1
            elif cname == 'person': counts['pedestrian'] += 1
            elif cname in ['ambulance', 'fire truck']: emergency = True

        total_pcu = (counts['motorcycle']*0.5) + counts['car'] + (counts['bus']*2.2) + (counts['truck']*2.2)

        if emergency:
            target_green, status = 60, "⚡ EMERGENCY PREEMPTION Active"
        elif total_pcu > 15:
            target_green, status = 45, "🧠 ADAPTIVE CONTROL: Heavy Queue"
        elif total_pcu > 7:
            target_green, status = 30, "🧠 ADAPTIVE CONTROL: Moderate Traffic"
        else:
            target_green, status = 15, "🧠 ADAPTIVE CONTROL: Low Traffic"

        current_green -= 1
        if current_green <= 0: current_green = target_green

        # Update live global dictionary
        latest_telemetry = {
            "junction_id": "Anna Salai Junction #1 (Chennai)",
            "pcu_load": round(total_pcu, 1),
            "vehicle_counts": counts,
            "green_time": current_green,
            "route_status": status,
            "emergency_alert": emergency
        }
        time.sleep(1)

# Start AI thread when app launches
threading.Thread(target=run_ai_loop, daemon=True).start()

# 2. Public API Endpoint
@app.route('/api/telemetry')
def get_telemetry():
    return jsonify(latest_telemetry)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    