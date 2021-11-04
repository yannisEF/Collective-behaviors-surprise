import json

class Agent:
    """
    A single agent able to move in a map, unaware of its current state
    """

    id = 0

    def __init__(self, sensor_range_0:float, sensor_range_1:float, speed:float, noise:list(float)) -> None:
        self.id = Agent.id
        Agent.id += 1

        self.sensor_range_0 = sensor_range_0
        self.sensor_range_1 = sensor_range_1
        self.speed = speed
        self.noise = noise

    def decision(self):
        """
        Return the decision of the agent
        """

        return "keep_direction" # "switch_direction"