from progress.bar import Bar

from utils import *
from agents import Agent

class Map:
    """
    The map containing the agents
    """

    def __init__(self) -> None:
        self.agents = {} # genome's id:Agent
        self.agent_to_pos = {} # genome's id:{Agent:pos}

        self.genome_to_show = 0 # id of genome to show

        self.name = "Map"
        self.length_sim = 0
    
    def _init_agent_position(self, new_agent:Agent):
        """
        Initialize a new agent's position in the map, 
        Returns its position
        """

        raise NotImplementedError("Overriden by other topologies")

    def _move_agent(self, agent:Agent):
        """
        Moves an agent on the map
        Returns its position
        """

        raise NotImplementedError("Overriden by other topologies")
    
    def _detect_others(self, agent:Agent, pos_to_agent:dict):
        """
        Updates the agent's sensor based on the others' positions
        """

        raise NotImplementedError("Overriden by other topologies")
    
    def show_console(self):
        """
        Outputs the map in the console
        """

        raise NotImplementedError("Overriden by other topologies")
        
    def add_agent(self, genome_id:int, new_agent:Agent):
        """
        Add an agent to the map
        """

        if genome_id not in self.agents:
            self.agents[genome_id] = []
        
        if genome_id not in self.agent_to_pos:
            self.agent_to_pos[genome_id] = {}

        if new_agent not in self.agents[genome_id]:
            self.agents[genome_id].append(new_agent)

            new_position = self._init_agent_position(new_agent)
            self.agent_to_pos[genome_id][new_agent] = new_position
            new_agent.position = new_position

    def _step(self, genome_id, max_record_hoziron=0):
        """
        Run a step of the environment
        """

        agents = self.agents[genome_id]

        # The agents take their decision
        for agent in agents:
            agent.compute_score()
            agent.take_decision()
            agent.predict_sensors()

        # The map updates the agents' position
        for agent in agents:
            new_position = self._move_agent(agent)
            self.agent_to_pos[genome_id][agent] = new_position
            agent.position = new_position

            agent.position_history = agent.position_history[-max_record_hoziron:] + [new_position]

        # Checking the agents' sensors
        pos_to_agent = reverse_dict_with_repeat(self.agent_to_pos[genome_id])
        for agent in agents:
            agent.reset_sensors()
            self._detect_others(agent, pos_to_agent)

    def run(self, length:int, verbose=False, genome_to_run=None, progress_bar=False):
        """
        Run the environment for a given length
        """

        if progress_bar is True:
            print()
            bar = Bar("Simulating a run of length {}".format(length), max=length)

        self.length_sim += length
        for _ in range(length):
            self._step(self.genome_to_show if genome_to_run is None else genome_to_run, max_record_hoziron=length)
        
            if verbose is True: print(self)
            if progress_bar is True:
                bar.next()
        
    def reset(self, genome_to_reset=None):
        """
        Reset the simulation
        """

        self.length_sim = 0
        for genome, agents in self.agents.items():
            if genome_to_reset is None or genome == genome_to_reset:
                for agent in agents:
                    agent.reset()
                    agent.position = self._init_agent_position(agent)
    
    def __str__(self):
        text = "{}\t{} genomes \n".format(self.name, len(self.agents))

        for genome, agents in self.agents.items():
            text += "genome {}\t {} agents\n".format(genome, len(agents))
            for agent in agents:
                text += str(agent) + "\n"
        
        return text[:-1]