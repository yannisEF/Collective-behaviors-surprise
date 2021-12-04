from agents import Agent

class Generation:
    """
    A class that evovles a number of agents
    """

    def __init__(self, nb_runs_per_evaluation=10, elitism=1, mutation_rate=0.05) -> None:
        self.nb_runs_per_evaluation = 10
        self.elitism = 1
        self.mutation_rate = 0.05

        self.agents = {} # id:Agent
        self.fitness = 0
    
    def add_agent(self, **params) -> Agent:
        """
        Adds an agent to the population
        """

        new_agent = Agent(**params)
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
    
    # Need to add mutation and crossover
    # Need to average the fitness over a number of runs
