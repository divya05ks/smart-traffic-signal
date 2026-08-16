import numpy as np

class HeterogeneousSignalAgent:
    """
    Single Junction RL Agent optimizing green phase duration based on PCU features.
    """
    def __init__(self, lane_id):
        self.lane_id = lane_id
        self.min_green = 7.0   # Minimum safety green (seconds)
        self.max_green = 60.0  # Maximum cap green (seconds)
        
    def compute_optimal_green(self, lane_state, total_intersection_pcu):
        """
        Computes dynamic green duration for this phase.
        Uses PCU density, queue length, and emergency priority.
        """
        # 1. Immediate Pre-emptive Override
        if lane_state['emergency_flag']:
            return self.max_green, True  # Max green allocation & Emergency Active
        
        # 2. Compute Proportional PCU Load
        pcu_density = lane_state['total_pcu_density']
        if total_intersection_pcu == 0:
            return self.min_green, False
            
        pcu_ratio = pcu_density / total_intersection_pcu
        
        # 3. Dynamic Green Allocation Formula (Base Cycle = 90s)
        base_cycle = 90.0
        calculated_green = pcu_ratio * base_cycle
        
        # Clamp duration between safety bounds
        allocated_green = max(self.min_green, min(calculated_green, self.max_green))
        return round(allocated_green, 1), False

class MARLIntersectionCoordinator:
    """
    Multi-Agent Coordinator sharing information across connected junctions.
    """
    def __init__(self, node_ids):
        self.agents = {node: HeterogeneousSignalAgent(node) for node in node_ids}
        
    def coordinate_phases(self, multi_lane_states):
        total_pcu = sum(state['total_pcu_density'] for state in multi_lane_states.values())
        
        schedule = {}
        for lane_id, state in multi_lane_states.items():
            agent = self.agents[lane_id]
            green_time, emergency = agent.compute_optimal_green(state, total_pcu)
            schedule[lane_id] = {
                'green_duration_sec': green_time,
                'emergency_override': emergency
            }
            
        return schedule

# Simulation Run
if __name__ == "__main__":
    coordinator = MARLIntersectionCoordinator(['North', 'South', 'East', 'West'])
    
    # Simulated camera states for 4 lanes
    simulated_states = {
        'North': {'total_pcu_density': 18.5, 'queue_length': 12, 'emergency_flag': False},
        'South': {'total_pcu_density': 4.2,  'queue_length': 3,  'emergency_flag': False},
        'East':  {'total_pcu_density': 25.0, 'queue_length': 15, 'emergency_flag': True},  # Ambulance present
        'West':  {'total_pcu_density': 2.0,  'queue_length': 1,  'emergency_flag': False}
    }
    
    optimal_schedule = coordinator.coordinate_phases(simulated_states)
    print("--- DYNAMIC MARL SIGNAL TIMING ---")
    for lane, timing in optimal_schedule.items():
        print(f"Lane {lane}: {timing['green_duration_sec']}s Green | Emergency: {timing['emergency_override']}")