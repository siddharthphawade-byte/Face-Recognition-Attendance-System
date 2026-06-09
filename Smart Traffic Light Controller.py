import time

class AITrafficController:
    def __init__(self):
        self.lanes = ["North", "South", "East", "West"]
        self.base_time = 5  # Minimum green time in seconds (for safety)
        self.max_time = 40  # Maximum additional green time to prevent starvation

    def get_vehicle_counts(self):
        """
        Mock function: In reality, this interfaces with OpenCV/YOLO
        e.g., return yolo_model.detect(camera_feed)
        """
        # Simulating heavy traffic East, light traffic West
        return {"North": 15, "South": 5, "East": 25, "West": 2}

    def calculate_green_time(self, counts):
        """Calculates dynamic green light duration based on density."""
        total_vehicles = sum(counts.values())
        
        # If intersection is empty, revert to standard short timers
        if total_vehicles == 0:
             return {lane: self.base_time for lane in self.lanes}
             
        allocated_times = {}
        for lane, count in counts.items():
            # Proportional time allocation based on density
            weight = count / total_vehicles
            calculated_time = int(self.base_time + (self.max_time * weight))
            
            # Cap the maximum time to ensure other lanes aren't starved
            allocated_times[lane] = min(calculated_time, self.max_time + self.base_time)
            
        return allocated_times

    def run_cycle(self):
        counts = self.get_vehicle_counts()
        print(f"📊 Live Vehicle Density: {counts}")
        
        green_times = self.calculate_green_time(counts)
        
        # Smart Feature: Sort lanes by highest density to clear the worst congestion first
        prioritized_lanes = sorted(green_times.items(), key=lambda item: item[1], reverse=True)
        
        for lane, duration in prioritized_lanes:
            print(f"🚦 [GREEN] for {lane} lane. Duration: {duration} seconds.")
            # time.sleep(duration) # Uncomment to simulate the actual hardware delay
            print(f"🛑 [RED] for {lane} lane.")
            print("-" * 40)

if __name__ == "__main__":
    print("Initializing AI Traffic Control System...\n")
    controller = AITrafficController()
    controller.run_cycle()