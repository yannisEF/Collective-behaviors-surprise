import torch
import random

from copy import deepcopy

from neural_network import ActionNetwork, PredictionNetwork


class Agent:
    """
    A single agent able to move in a map, unaware of its current state
    """

    id = 0

    def __init__(
        self,
        action_network:ActionNetwork,
        prediction_network:PredictionNetwork,
        sensors_range_and_dir:tuple[tuple[tuple[float], int]],
        nb_directions:int,
        speed:float
    ) -> None:

        self.id = Agent.id
        Agent.id += 1

        self.action_network = deepcopy(action_network)
        self.prediction_network = deepcopy(prediction_network)

        # An agent's sensor has a range (from.. to..), a direction, and two subsensors (front and back)
        self.sensors = (
            (r, d, [False, False])
            for r, d in sensors_range_and_dir
        )
        self.sensors_predictions = (
            [None, None]
            for r, d in sensors_range_and_dir
        )

        self.speed = speed
        self.direction = random.randrange(0, nb_directions)

        self.raw_surprise = 0

    def reset_sensors(self):
        
        self.sensors = (
            (r, d, [False, False])
            for r, d, s in self.sensors
        )

    def reset(self) -> None:
        """
        Reset the agent
        """

        self.reset_sensors()
        self.direction = random.choice([-1, 1])
        self.raw_surprise = 0

    def compute_surprise(self) -> None:
        """
        Adds the number of correct predictions to the agent's raw_surprise
        """

        self.raw_surprise = sum([
            sum([s[-1][i] == p[i] for i in range(2)])
            for s, p in zip(self.sensors, self.sensors_predictions)
        ])

    def take_decision(self) -> None:
        """
        Changes the agent's direction based on its action network
        """

        nn_input = torch.Tensor(
            [self.direction, *[state for sensor in self.sensors for state in sensor[-1]]]
        )

        self.direction = self.action_network(nn_input)
    
    def predict_sensors(self) -> None:
        """
        Predicts the state of the sensors with the prediction network
        """

        nn_input = torch.Tensor(
            [self.direction, *[state for sensor in self.sensors for state in sensor[-1]]]
        )[None, None, :]
        nn_output = self.prediction_network(nn_input)

        cursor = 0
        for pred in self.sensors_predictions:
            for i in range(len(pred)):
                pred[i] = nn_output[cursor + i]
            cursor += i + 1
