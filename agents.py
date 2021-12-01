from utils import *
from neural_network import *

class Agent:
    """
    A single agent able to move in a map, unaware of its current state
    """

    id = 0

    def __init__(self, sensor_range_0:float, sensor_range_1:float, speed:float, noise:list(float)) -> None:
        self.id = Agent.id
        Agent.id += 1

        self.nb_sensors = 4
        self.sensor_range_0 = sensor_range_0
        self.sensor_0 = [False, False]

        self.sensor_range_1 = sensor_range_1
        self.sensor_1 = [False, False]

        self.speed = speed
        self.noise = noise

        self.direction = 1 # direction is -1 or 1
        self.position = None

        self.nb_hiddens_layer1 = 2
        self.nb_hiddens_layer2 = 4
        self.next_action = 0

        self.action_network = NeuralNetwork(4, nb_hiddens_layer1)
        self.prediction_network = NeuralNetwork(4, nb_hiddens_layer2)
        
        self.input0 = np.concatenate([self.sensor_0[0], self.sensor_0[1], self.sensor_1[0], self.sensor_1[1], self.next_action])

    def take_decision(self):
        """
        Return the decision of the agent
        """
        output = np.clip(self.action_network.evaluate_network(input0), -1, 1)

        return output #"keep_direction" or "switch_direction"

    def predict_sensors(self):
        
        output = np.clip(self.prediction_network.evaluate_network(input0), -1, 1)
        return output
