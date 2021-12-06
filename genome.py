from agents import Agent
from menu import GenomeMenu
from neural_network import ActionNetwork, PredictionNetwork

class Genome:
    """
    A class that evovles a number of agents
    """

    id = 0

    def __init__(self, action_network=None, prediction_network=None, nb_runs_per_evaluation=10, elitism=1, mutation_rate=0.05) -> None:
        self.id = Genome.id
        Genome.id += 1
        
        self.nb_runs_per_evaluation = 10
        self.elitism = 1
        self.mutation_rate = 0.05

        self.agents = {} # id:Agent
        self.fitness = 0

        self.action_network = ActionNetwork() if action_network is None else action_network
        self.prediction_network = PredictionNetwork() if prediction_network is None else prediction_network
    
    def add_agent(self, **params) -> Agent:
        """
        Adds an agent to the population
        """

        new_agent = Agent(action_network=self.action_network, prediction_network=self.prediction_network, **params)
        self.agents[new_agent.id] = new_agent

        return new_agent
    
    def remove_agent(self, id) -> None:
        """
        Removes a given agent from the population
        """

        del self.agents[id]
    
    def compute_fitness(self, length_sim) -> None:
        """
        Compute the fitness for this timestep
        """
        
        self.fitness = sum([agent.score for agent in self.agents.values()])
        self.fitness /= len(self.agents) * length_sim
    
