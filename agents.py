import random
import torch

from utils import *
from neural_network import ActionNetwork, PredictionNetwork

class Agent:
    """
    A single agent able to move in a map, unaware of its current state
    """

    id = 0

    def __init__(self, sensor_range_0:float, sensor_range_1:float, speed:float, noise) -> None:
        self.id = Agent.id
        Agent.id += 1

        self.sensor_range_0 = sensor_range_0
        self.sensor_0 = [False, False]

        self.sensor_range_1 = sensor_range_1
        self.sensor_1 = [False, False]

        self.speed = speed
        self.noise = noise

        self.direction = random.choice([-1, 1])
        self.position = None

        self.action_network = ActionNetwork()
        self.prediction_network = PredictionNetwork()

    def reset_sensors(self) -> None:
        """
        Reset the agent's sensors
        """

        self.sensor_0 = [False, False]
        self.sensor_1 = [False, False]   

    def take_decision(self) -> None:
        """
        Changes the agent's direction based on its action network
        """

        nn_input = torch.Tensor([self.direction > 0, *self.sensor_0, *self.sensor_1])
        nn_output = self.action_network.forward(nn_input)

        self.direction = int(torch.round(2 * nn_output - 1))
    
    def predict_sensors(self) -> None:
        """
        Predicts the state of the sensors with the prediction network
        """

        pass
    
    def __str__(self):
        return "Agent {}:\tposition: {}\tdirection: {}\tsensors 0: {}\tsensors 1: {}".format(self.id, self.position, self.direction, self.sensor_0, self.sensor_1)
