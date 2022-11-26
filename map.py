from tkinter import Canvas
from progress.bar import Bar

from agents import Agent
from agents_utils import Position, Population


class Map:
    """
    The map containing the agents
    """

    # Overriden by other topologies
    default_params_action_nn:dict = {}
    default_params_prediction_nn:dict = {}

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
            self.all_agents[new_id] = [new_agent, new_position]

    def _step(self, no_prediction:bool=False) -> None:
        """
        Run a step of the environment
        """

        all_positions = []
        for agent, position in self.all_agents.values():
            # The agents take their decision
            if no_prediction is False:
                agent.compute_surprise()
                agent.take_decision()
                agent.predict_sensors()
            else:
                agent.take_decision()

            # The map updates the agents' position
            new_position = self._move_agent(agent, position)
            self.all_agents[agent.id][-1] = new_position
            
            all_positions.append(new_position)       

        # Checking the agents' sensors after they have all moved
        for agent, position in self.all_agents.values():
            agent.reset_sensors()
            self._detect_others(agent, position, all_positions)

    def run(
        self,
        length:int,
        reset:bool=False,
        no_prediction:bool=False,
        input_population:Population=None,
        progress_bar:bool=False
    ) -> None:
        """
        Run the environment for a given length
        """

        if progress_bar is True:
            print()
            bar = Bar("Simulating a run of length {}".format(length), max=length)
        
        if reset is True:
            self.reset(input_population)
            
        for _ in range(length):
            self._step(no_prediction=no_prediction)

            if progress_bar is True:
                bar.next()
        
    def reset(self, input_population:Population=None) -> None:
        """
        Reset the simulation
        """

        if input_population is not None:
            old_agents = input_population
        else:
            old_agents = [ta[0] for ta in self.all_agents.values()]

        self.all_agents = {}
        for agent in old_agents:
            agent.reset()
            self.add_agent(agent)


class Map2D(Map):
    """
    A map able to cast its positions in 2D space for visualization purposes
    """

    def __init__(self) -> None:
        super().__init__()
    
    def draw_map(self, canvas:Canvas, canvas_width:int, canvas_height:int) -> None:
        """
        Draws the map's topology on a given Canvas
        """
        
        raise NotImplementedError("Overriden by other topologies") 

    def get_2D_positions(self, *args, **kwargs) -> list[Position]:
        """
        Returns a list of the agent's positions in 2D space
        """

        raise NotImplementedError("Overriden by other topologies")
