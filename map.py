from utils import *
from agents import Agent

class Map:
    """
    The map containing the agents
    """

    def __init__(self) -> None:
        self.agents = []
        self.agent_to_pos = {}
    
    def _init_agent_position(self, new_agent:Agent):
        """
        Initialize a new agent's position in the map
        """

        new_agent.position = None
        return new_agent.position

    def add_agent(self, new_agent:Agent):
        """
        Add an agent to the map
        """

        if new_agent not in self.agents:
            self.agents.append(new_agent)

            new_position = self._init_agent_position(new_agent)
            self.agent_to_pos[new_agent] = new_position

    def _step(self):
        """
        Run a step of the environment
        """

        # The agents take their decision
        for agent in self.agents:
            agent.take_decision()

        # The map updates the agents' position
        for agent in self.agents:
            self.agent_to_pos[agent] = agent.move()

        # Checking the agents' sensors
        pos_to_agent = reverse_dict_with_repeat(self.agent_to_pos)
        for agent in self.agents:
            agent.detect(pos_to_agent)

    def run(self, length:int):
        """
        Run the environment for a given length
        """
        for _ in range(length):
            self._step()

class Ring(Map):
    """
    A ring around which agents can turn
    """

    def __init__(self, ring_length:int) -> None:
        super().__init__()

        self.ring_length = ring_length