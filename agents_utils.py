import torch

from neural_network import ActionNetwork, PredictionNetwork
from agents import Agent


Position = list[int]

class Population:
    """
    Class that holds a list of identical agents
    """

    id = 0

    def __init__(
        self,
        nb_agents:int,
        action_network:ActionNetwork,
        prediction_network:PredictionNetwork,
        agents_param:dict,
        name:str="Population"
    ) -> None:
        """
        /!\ Does not deepcopy the input networks
        """

        self.id = Population.id
        Population.id += 1

        self.name = name

        self.action_network = action_network
        self.prediction_network = prediction_network

        self.my_agents = [
            Agent(
                action_network=self.action_network,
                prediction_network=self.prediction_network,
                **agents_param
            ) for _ in range(nb_agents)
        ]

    def _get_fitness(self, length_sim:int) -> float:
        """
        Compute the fitness of the population for the current timestep
        """
        
        return sum([agent.raw_surprise for agent in self.my_agents]) / (len(self.my_agents) * length_sim)
    
    def to_tensor(self) -> torch.Tensor:
        """
        Compute a tensor representation of the population
        """

        try:
            agent = self.my_agents[0]

        except IndexError:
            raise IndexError("No agent in population {}.".format(self.id))

        return torch.cat([
            agent.action_network.to_tensor(),
            agent.prediction_network.to_tensor()
        ])

    def from_tensor(self, tensor_agent:torch.Tensor) -> None:
        """
        Changes the population's parameters according to a given tensor
        """

        for agent in self.my_agents:
            agent.action_network.from_tensor(tensor_agent[:agent.action_network.total_size])
            agent.prediction_network.from_tensor(tensor_agent[agent.action_network.total_size:])

    def __iter__(self):
        """
        Returns the population
        """

        return iter(self.my_agents)