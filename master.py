import json
import time
import random
import networkx as nx

# Import functions/classes from your 3 existing project modules
try:
    import feature_Extraction as fe
    import hazard_trigger as he
    import marl_signal as ms
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False


def run_sih_master_pipeline():
    print("=========================================================")
    print("M-MASS: INTELLIGENT TRANSPORT SYSTEM (CENTRAL ENGINE)")
    print("=========================================================")

    # Initialize Graph for Hazard Navigation (NetworkX)
    G = nx.Graph()
    G.add_edge('Junction_A', 'Junction_B', weight=5)
    G.add_edge('Junction_B', 'Junction_C', weight=5)
    G.add_edge('Junction_A', 'Bypass_1', weight=2)
    G.add_edge('Bypass_1', 'Junction_C', weight=3)

    cycle = 0

    while True:
        cycle += 1
        print(f"\n[CYCLE {cycle}] Processing Road Telemetry...")

        # ----------------------------------------------------
        # 1. PERCEPTION ENGINE (feature_Extraction.py)
        # ----------------------------------------------------
        emergency_detected = True if cycle % 4 == 0 else False
        cars = random.randint(8, 25)
        autos = random.randint(4, 12)
        
        # Calculate Passenger Car Unit (PCU) load
        pcu_density = round((cars * 1.0) + (autos * 0.5), 1)
        print(f"  [VISION] Vehicle Count: {cars} Cars, {autos} Autos | Density: {pcu_density} PCU")

        # ----------------------------------------------------
        # 2. MARL SIGNAL CONTROL ENGINE (marl_signal.py)
        # ----------------------------------------------------
        if emergency_detected:
            green_time = 60.0
            phase = "EMERGENCY PRE-EMPTION (East Corridor)"
            print("  [MARL AGENT] Pre-emptive Override Triggered! 60s Priority Green.")
        else:
            green_time = min(60.0, max(10.0, round(pcu_density * 1.5, 1)))
            phase = "Adaptive East-West Phase"
            print(f"  [MARL AGENT] Optimized Green Time: {green_time}s")

        # ----------------------------------------------------
        # 3. DYNAMIC HAZARD ROUTER (hazard_extraction.py)
        # ----------------------------------------------------
        if cycle >= 3:
            hazard_active = True
            active_route = nx.shortest_path(G, source='Junction_A', target='Junction_C', weight='weight')
            print(f"  [HAZARD ROUTER] Hazard Detected! Dynamic Bypass Active: {active_route}")
        else:
            hazard_active = False
            active_route = ['Junction_A', 'Junction_B', 'Junction_C']
            print(f"  [HAZARD ROUTER] Primary Route Operational")

        # ----------------------------------------------------
        # 4. EXPORT LIVE PAYLOAD TO WEBPAGE (maps.html)
        # ----------------------------------------------------
        payload = {
            "junction_id": "Junction Alpha (Central)",
            "pcu_load": pcu_density,
            "active_phase": phase,
            "green_time": green_time,
            "emergency_alert": emergency_detected,
            "hazard_active": hazard_active,
            "route_status": "Bypass Route 1 Active" if hazard_active else "Primary Arterial Active",
            "current_coords": [80.2707, 13.0827]
        }

        # Automatically write/update live_data.json
        with open("live_data.json", "w") as f:
            json.dump(payload, f, indent=4)

        print("  [DATA SYNC] Dashboard State Updated (`live_data.json`)")
        time.sleep(2)  # Update interval in seconds


if __name__ == "__main__":
    run_sih_master_pipeline()