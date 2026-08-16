import cv2
import json
import time
from ultralytics import YOLO

# 1. Load Pre-trained AI Object Detection Model (YOLOv8)
print("Loading Traffic AI Detection Model...")
model = YOLO('yolov8n.pt')  # Standard YOLO model

# 2. Indian PCU Weights
PCU_WEIGHTS = {
    'motorcycle': 0.5,
    'car': 1.0,
    'bus': 2.2,
    'truck': 2.2,
    'person': 0.2  # Pedestrian weight
}

# 3. Open Video Stream
video_path = 'traffic.mp4'
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"Error: Could not open video '{video_path}'. Make sure it's in your project folder!")
    exit()

print("AI Traffic Control System Active! Processing video feed...")

# Dynamic timer tracker
current_green_countdown = 30

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        # Loop video when it ends
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    # Run AI Detection
    results = model(frame, verbose=False)[0]
    
    # Initialize Vehicle & Pedestrian Counts
    counts = {
        'motorcycle': 0,
        'car': 0,
        'autorickshaw': 0,
        'bus': 0,
        'truck': 0,
        'pedestrian': 0
    }
    emergency_detected = False

    # Extract detected objects from YOLO
    for box in results.boxes:
        class_id = int(box.cls[0])
        class_name = model.names[class_id]

        # Map COCO class names to standard keys
        if class_name in ['motorbike', 'motorcycle']:
            counts['motorcycle'] += 1
        elif class_name == 'car':
            counts['car'] += 1
        elif class_name == 'bus':
            counts['bus'] += 1
        elif class_name == 'truck':
            counts['truck'] += 1
        elif class_name == 'person':
            counts['pedestrian'] += 1
        
        # Simple Emergency vehicle detection tag
        if class_name in ['ambulance', 'fire truck']:
            emergency_detected = True

    # Calculate Total Indian PCU Load
    total_pcu = (
        (counts['motorcycle'] * PCU_WEIGHTS['motorcycle']) +
        (counts['car'] * PCU_WEIGHTS['car']) +
        (counts['bus'] * PCU_WEIGHTS['bus']) +
        (counts['truck'] * PCU_WEIGHTS['truck']) +
        (counts['pedestrian'] * PCU_WEIGHTS['person'])
    )

    # ADAPTIVE SIGNAL CONTROL ALGORITHM
    if emergency_detected:
        target_green = 60
        status_msg = "⚡ EMERGENCY PREEMPTION: Clearing Priority Lane"
    elif total_pcu > 15:
        target_green = 45  # Heavy queue
        status_msg = "🧠 ADAPTIVE CONTROL: Heavy Queue (+20s Extension)"
    elif total_pcu > 7:
        target_green = 30  # Moderate traffic
        status_msg = "🧠 ADAPTIVE CONTROL: Moderate Traffic Flow"
    else:
        target_green = 15  # Light traffic
        status_msg = "🧠 ADAPTIVE CONTROL: Low Traffic (Optimizing Cycle)"

    # Countdown tick simulation
    current_green_countdown -= 1
    if current_green_countdown <= 0:
        current_green_countdown = target_green

    # Telemetry payload matching maps.html requirements
    telemetry = {
        "junction_id": "Anna Salai Junction #1 (Chennai)",
        "pcu_load": round(total_pcu, 1),
        "vehicle_counts": counts,
        "green_time": current_green_countdown,
        "active_phase": "North-South Corridor",
        "route_status": status_msg,
        "emergency_alert": emergency_detected,
        "current_coords": [80.2707, 13.0827]
    }

    # Write telemetry data to live_data.json
    with open("live_data.json", "w") as f:
        json.dump(telemetry, f, indent=2)

    print(f"[LIVE AI] Detected PCU: {round(total_pcu, 1)} | Timer: {current_green_countdown}s | Status: {status_msg}")

    time.sleep(1)

cap.release()