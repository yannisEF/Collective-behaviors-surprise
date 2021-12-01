import numpy as np 

class NeuralNetwork:

    def __init__(self, nb_sensors, nb_hiddens_layer):
        self.parameters = self.init_random_parameters(nb_sensors, nb_hiddens_layer)

    def init_random_parameters(self, nb_sensors, nb_hiddens_layer):
        """
        Init random weights parameters from normal (gaussian) distribution
        """
        parameters = [np.random.normal(0, 1, (self.nb_sensors+1, self.nb_hiddens_layer)),
                    np.random.normal(0, 1, (self.nb_hiddens_layer, 2))]

        return parameters

    def get_parameters(self):
        return self.parameters

    def evaluate_network(self, x):
        """
        Return the response of the network to the input x
        """
        out = np.concatenate([[1], x_])
        for elem in self.parameters[:-1]:
            out = np.tanh(out @ elem)
        out = out @ self.parameters[-1]  # linear output for last layer    
        out[-2:] = np.where(np.tanh(out[-2:])>0, 1, 0)
        
        return out


