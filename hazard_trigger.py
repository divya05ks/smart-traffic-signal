import networkx as nx

class DynamicHazardRouter:
    """
    Handles dynamic rerouting ONLY when unpredictable hazards (construction, flooding) occur.
    Ignores permanent static geography (lakes, farmlands).
    """
    def __init__(self):
        # Create road network graph (Nodes = Intersections, Edges = Roads)
        self.graph = nx.DiGraph()
        
        # Base road network with distance (km) and travel time (min)
        self.graph.add_edge('Junction_A', 'Junction_B', weight=5, condition='clear', allowed_vehicles=['all'])
        self.graph.add_edge('Junction_B', 'Junction_C', weight=4, condition='clear', allowed_vehicles=['all'])
        self.graph.add_edge('Junction_A', 'Bypass_1', weight=3, condition='clear', allowed_vehicles=['2_wheeler', 'car'])
        self.graph.add_edge('Bypass_1', 'Junction_C', weight=4, condition='clear', allowed_vehicles=['2_wheeler', 'car'])

    def register_dynamic_hazard(self, u, v, hazard_type):
        """
        Triggers when CV detects active construction, waterlogging, or severe breakage.
        """
        if self.graph.has_edge(u, v):
            print(f"⚠️ DYNAMIC HAZARD DETECTED on road {u} ➔ {v}: {hazard_type.upper()}")
            # Set weight to infinity to block route for standard navigation
            self.graph[u][v]['weight'] = 999
            self.graph[u][v]['condition'] = hazard_type

    def calculate_vehicle_route(self, origin, destination, vehicle_type):
        """
        Calculates optimal route tailored to vehicle class during active hazards.
        """
        try:
            # Filter graph for vehicle-compatible edges
            subgraph = self.graph.copy()
            for u, v, data in self.graph.edges(data=True):
                if vehicle_type not in data['allowed_vehicles'] and 'all' not in data['allowed_vehicles']:
                    subgraph.remove_edge(u, v)
                    
            path = nx.shortest_path(subgraph, source=origin, target=destination, weight='weight')
            return path
        except nx.NetworkXNoPath:
            return None

# Simulation Run
if __name__ == "__main__":
    router = DynamicHazardRouter()
    
    # Normal Route before hazard
    print("Normal Route (Lorry):", router.calculate_vehicle_route('Junction_A', 'Junction_C', 'lorry'))
    
    # CV detects active metro construction on Main Road (Junction_A ➔ Junction_B)
    router.register_dynamic_hazard('Junction_A', 'Junction_B', 'metro_construction')
    
    # Recalculate routes during hazard
    print("Post-Hazard Route (2-Wheeler):", router.calculate_vehicle_route('Junction_A', 'Junction_C', '2_wheeler'))
    print("Post-Hazard Route (Lorry):", router.calculate_vehicle_route('Junction_A', 'Junction_C', 'lorry'))