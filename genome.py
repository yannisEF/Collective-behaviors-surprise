import torch
from copy import deepcopy

from agents import Agent
from neural_network import ActionNetwork, PredictionNetwork


class Genome:
    """
    A class that evolves a number of agents
    """

    id = 0

    def __init__(
        self,
        name="Genome",
        action_network=None,
        prediction_network=None
    ) -> None:
    
        self.id = Genome.id
        Genome.id += 1

        self.name = name

        self.agents = {} # id:Agent
        self.fitness = 0

        self.action_network = ActionNetwork() if action_network is None else deepcopy(action_network)
        self.prediction_network = PredictionNetwork() if prediction_network is None else deepcopy(prediction_network)
    
    def add_agent(self, **params) -> Agent:
        """
        Adds an agent to the population
        """

        new_agent = Agent(action_network=self.action_network, prediction_network=self.prediction_network, **params)
        self.agents[new_agent.id] = new_agent

        return new_agent
    
    def remove_agent(self, id:int) -> None:
        """
        Removes a given agent from the population
        """

        del self.agents[id]
    
    def compute_fitness(self, length_sim:int) -> None:
        """
        Compute the fitness for this timestep
        """
        
        self.fitness = sum([agent.score for agent in self.agents.values()])
        self.fitness /= len(self.agents) * length_sim

        return self.fitness
    
    def to_tensor(self) -> torch.Tensor:
        """
        Compute a tensor representation of the genome
        """

        return torch.cat([self.action_network.to_tensor(), self.prediction_network.to_tensor()])

    def from_tensor(self, tensor_genome:torch.Tensor):
        """
        Changes the genome's parameters according to a given tensor
        """

        self.action_network.from_tensor(tensor_genome[:self.action_network.total_size])
        self.prediction_network.from_tensor(tensor_genome[self.action_network.total_size:])

        return self
    
