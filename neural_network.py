import torch
import numpy as np


class GenomeNetwork(torch.nn.Module):
    """
    A Deep Neural Network that can be packed and unpacked for saving purposes
    """

    def __init__(
        self,
        input_size:int=5,
        hidden_size:int=2,
        output_size:int=1
    ) -> None:

        super().__init__()

        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        self.neural_networks = []
    
    def _compute_total_size(self) -> int:
        """
        Compute the total size of the flattened tensor representing the network
        """

        s = 0
        for my_nn in self.neural_networks:
            for p in my_nn.parameters():
                size = p.data.size()
                i, j = (size[0], 1) if len(size) == 1 else size

                s += i*j
        
        return s

    def forward(self, x):
        """
        Overidden by subclasses
        """

        raise NotImplementedError("Must be overriden by subclasses")

    def to_tensor(self) -> torch.Tensor:
        """
        Returns a vector representing the network's weights
        """

        s = []
        for my_nn in self.neural_networks:
            s += [p.data.flatten() for p in my_nn.parameters()]

        return torch.cat(s)
    
    def from_tensor(self, from_tensor:torch.Tensor) -> None:
        """
        Assigns the network's weights with a given flattened tensor
        """

        for my_nn in self.neural_networks:
            for p in my_nn.parameters():
                size = p.data.size()

                i, j = (size[0], 1) if len(size) == 1 else size
                
                p.data = from_tensor[:i*j]
                
                if j != 1:
                    p.data = p.data.reshape(i,j)

                from_tensor = from_tensor[i*j:]


class ActionNetwork(GenomeNetwork):
    """
    NN that outputs a direction index given the current direction and sensors' observations.
    """

    def __init__(
        self,
        nb_directions,
        input_size=5,
        hidden_size=2,
        output_size=1,
    ) -> None:

        super().__init__(
            input_size=input_size,
            hidden_size=hidden_size,
            output_size=output_size
        )

        self.nb_directions = nb_directions

        self.fully_connected1 = torch.nn.Linear(self.input_size, self.hidden_size)
        self.fully_connected2 = torch.nn.Linear(self.hidden_size, self.output_size)

        self.neural_networks.append(self.fully_connected1)
        self.neural_networks.append(self.fully_connected2)

        self.total_size = self._compute_total_size()

    def forward(self, x):
        relu = torch.nn.ReLU()(self.fully_connected1(x))
        sig = torch.nn.Sigmoid()(self.fully_connected2(relu))
        return int(sig.detach().numpy()[0] * self.nb_directions)


class PredictionNetwork(GenomeNetwork):
    """
    NN that output the sensors' expected state given current observations
    """

    def __init__(
        self,
        input_size=5,
        hidden_size=4,
        output_size=4
    ) -> None:

        super().__init__(
            input_size=input_size,
            hidden_size=hidden_size,
            output_size=output_size
        )

        self.fully_connected1 = torch.nn.RNN(self.input_size, self.hidden_size)
        self.fully_connected2 = torch.nn.Linear(self.hidden_size, self.output_size)

        self.neural_networks.append(self.fully_connected1)
        self.neural_networks.append(self.fully_connected2)

        self.total_size = self._compute_total_size()

        self.hn = torch.randn(1, 1, 4)

    def forward(self, x):
        out, self.hn = self.fully_connected1(x, self.hn)
        relu = torch.nn.ReLU()(out)
        sig = torch.nn.Sigmoid()(self.fully_connected2(relu))

        return np.array(
            np.round(sig[None, None, :].detach().numpy()[0]),
            dtype=bool
        ).flatten()
