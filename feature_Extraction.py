import cv2
import numpy as np
from ultralytics import YOLO

# Load YOLOv8 Model (Pre-trained on COCO / Custom Traffic Dataset)
model = YOLO('yolov8n.pt')

# Passenger Car Unit (PCU) Weighting Matrix
PCU_WEIGHTS = {
    'person': 0.1,        # Pedestrians
    'bicycle': 0.2,       # Bicycles
    'motorcycle': 0.5,    # 2-Wheelers
    'autorickshaw': 0.8,  # Auto-Rickshaws
    'car': 1.0,           # Cars / 4-Wheelers
    'bus': 3.0,           # Buses
    'truck': 3.0,         # Heavy Lorries
    'ambulance': 5.0,     # Emergency Priority
    'fire_truck': 5.0,    # Emergency Priority
    'police_car': 4.0     # Emergency Priority
}

def extract_intersection_features(frame):
    """
    Processes video feed from a junction lane camera.
    Returns structured state features for the RL Agent.
    """
    results = model(frame)[0]
    
    total_pcu = 0.0
    queue_count = 0
    emergency_present = False
    vehicle_counts = {k: 0 for k in PCU_WEIGHTS.keys()}
    
    for box in results.boxes:
        cls_id = int(box.cls[0])
        label = model.names[cls_id]
        
        if label in PCU_WEIGHTS:
            vehicle_counts[label] += 1
            total_pcu += PCU_WEIGHTS[label]
            
            # Identify emergency vehicle classes directly (No stickers)
            if label in ['ambulance', 'fire_truck', 'police_car']:
                emergency_present = True
            
            # Simple heuristic: Low speed / stationary boxes count toward queue
            # (In production, track object centroids across frames)
            queue_count += 1

    total_vehicles = sum(vehicle_counts.values()) or 1
    class_proportions = {k: v / total_vehicles for k, v in vehicle_counts.items()}
    
    state_vector = {
        'total_pcu_density': round(total_pcu, 2),
        'queue_length': queue_count,
        'class_proportions': class_proportions,
        'emergency_flag': emergency_present
    }
    
    return state_vector

# Test Execution
if __name__ == "__main__":
    print("Perception Engine Ready. Class-based detection & feature extraction initialized.")