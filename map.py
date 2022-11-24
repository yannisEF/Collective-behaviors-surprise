from progress.bar import Bar

from agents import Agent
from utils import Position


class Map:
    """
    The map containing the agents
    """

    def __init__(self) -> None:
        self.all_agents = {} # id:[Agent, pos]

        self.name = "Map"
    
    def _init_agent_position(self) -> Position:
        """
        Initialize a new agent's position in the map, 
        Returns its position
        """

        raise NotImplementedError("Overriden by other topologies")

    def _move_agent(self, agent:Agent, current_position:Position) -> Position:
        """
        Moves an agent on the map
        Returns its new position
        """

        raise NotImplementedError("Overriden by other topologies")
    
    def _detect_others(self, agent:Agent, position:Position, all_positions:list[float]) -> None:
        """
        Updates the agent's sensor based on the others' positions
        """

        raise NotImplementedError("Overriden by other topologies")
        
    def add_agent(self, new_agent:Agent) -> None:
        """
        Add an agent to the map
        """

        new_id = new_agent.id
        if new_id not in self.all_agents:
            new_position = self._init_agent_position()
            self.all_agents[new_id] = (new_agent, new_position)
            self.pos_to_id[new_position] = new_id

    def _step(self) -> None:
        """
        Run a step of the environment
        """

        all_positions = []
        for agent, position in self.all_agents.values():
            # The agents take their decision
            agent.compute_surprise()
            agent.take_decision()
            agent.predict_sensors()

            # The map updates the agents' position
            new_position = self._move_agent(agent, position)
            self.all_agents[agent.id][-1] = new_position
            
            all_positions.append(new_position)       

        # Checking the agents' sensors after they have all moved
        for agent, position in self.all_agents.values():
            agent.reset_sensors()
            self._detect_others(agent, position, all_positions)

    def run(self, length:int, progress_bar=False) -> None:
        """
        Run the environment for a given length
        """

        if progress_bar is True:
            print()
            bar = Bar("Simulating a run of length {}".format(length), max=length)

        for _ in range(length):
            self._step()

            if progress_bar is True:
                bar.next()
        
    def reset(self) -> None:
        """
        Reset the simulation
        """

        old_agents, self.all_agents = self.all_agents, {}
        for agent, _ in old_agents.keys():
            agent.reset()
            self.add_agent(agent)


class Map2D(Map):
    """
    A map able to cast its positions in 2D space for visualization purposes
    """

    def __init__(self) -> None:
        super().__init__()

    def get_2D_positions(self, *args, **kwargs) -> list[Position]:
        """
        Returns a list of the agent's positions in 2D space
        """

        raise NotImplementedError("Overriden by other topologies")
