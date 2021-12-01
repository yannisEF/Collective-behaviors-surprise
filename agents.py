import json

from utils import *

class Agent:
    """
    A single agent able to move in a map, unaware of its current state
    """

    id = 0

    def __init__(self, sensor_range_0:float, sensor_range_1:float, speed:float, noise:list(float)) -> None:
        self.id = Agent.id
        Agent.id += 1

        self.sensor_range_0 = sensor_range_0
        self.sensor_0 = [False, False]

        self.sensor_range_1 = sensor_range_1
        self.sensor_1 = [False, False]

        self.speed = speed
        self.noise = noise

        self.direction = 1 # direction is -1 or 1
        self.position = None

    def take_decision(self):
        """
        Return the decision of the agent
        """

        return "keep_direction"  # "switch_direction"

    def move(self):
        """
        Moves towards the current direction at the agent's speed
        """

        self.position += self.direction * self.speed  # noise ?
        return self.position

    def detect(self, pos_to_agent):
        """
        Updates the agent's sensor based on the others' positions
        """

        self.sensor_0 = [False, False]
        self.sensor_1 = [False, False]

        # NEED TO KNOW THE RING LENGTH, BETTER WAY
        ranges_0 = []
        max_0 = self.position + self.sensor_range_0
        if max_0 > 1:
            ranges_0 = [[self.position, 1], [0, max_0 - 1]]
        else:
            ranges_0 = [[self.position, max_0]]

        min_0 = self.position - self.sensor_range_0
        if min_0 < 0:
            ranges_0 += [[1 + min_0, 1], [0, self.position]]
        else:
            ranges_0 += [min_0, self.position]

        for other_position in pos_to_agent:
            pass
