import random
import sys
import math

from utils import *

from map import Map
from agents import Agent

class Ring(Map):
    """
    A ring around which agents can turn
    """

    def __init__(self, ring_length:int, resolution:float=None) -> None:
        super().__init__()

        self.name = "Ring map"
        self.ring_length = ring_length
        self.resolution = resolution

    def _init_agent_position(self, new_agent:Agent):
        """
        Initialize a new agent's position in the map, uniform distribution
        Returns its position
        """

        position = random.random() * self.ring_length
        return  position if self.resolution is None else position - position % self.resolution

    def _move_agent(self, agent:Agent):
        """
        Moves an agent on the map, adds noise to the new position
        Returns its position
        """
        
        position_shift = agent.direction * agent.speed
        position_shift += agent.noise * (2 * random.random() - 1)

        new_position = agent.position + position_shift
        
        if self.resolution is not None:
            new_position = new_position - new_position % self.resolution
        
        return new_position % self.ring_length
    
    def _detect_others(self, agent:Agent, pos_to_agent:dict):
        """
        Updates the agent's sensor based on the others' positions
        """

        for other_pos in pos_to_agent.keys():
            # Erase the agent from the currently checked position
            try:
                pos_to_agent[other_pos].remove(agent)
                if len(pos_to_agent[other_pos]) == 0: continue
            except ValueError:
                pass
        
            other_pos_modulo = [other_pos - self.ring_length, other_pos, other_pos + self.ring_length]

            for other_modulo in other_pos_modulo:
                diff_pos = agent.position - other_modulo

                # Check if agent in range of sensor 0
                if abs(diff_pos) <= agent.sensor_range_0:
                    agent.sensor_0[diff_pos <= 0] = True
                    break
                # Check if agent is not in range of sensor 0 but in range of sensor 1
                elif abs(diff_pos) <= agent.sensor_range_1:
                    agent.sensor_1[diff_pos <= 0] = True
                    break
            
            # Check if all the sensors are activated (therefore nothing more can be done)
            if all(agent.sensor_0) and all(agent.sensor_1):
                break

    def show_console(self, genome_id=0, erase=True, stop=True):
        """
        Simple console output according to the map's resolution
        """

        if self.resolution is None:
            raise NotImplementedError("Can't show continuous map for now")

        # Agents on the same position are printed at a different level
        pos_to_agent = reverse_dict_with_repeat(self.agent_to_pos[genome_id])
        other_lines = [round(self.ring_length/self.resolution) * '.' for _ in range(
            max([len(pos_to_agent[pos]) for pos in pos_to_agent]))]

        # Printing each agent at the correct index, if the index is already taken, outputs on another line
        for pos in pos_to_agent:
            index = round(pos/self.resolution)

            agents = pos_to_agent[pos]
            for i, agent in enumerate(agents):
                other_lines[i] = other_lines[i][:index] + \
                    str(agent.id) + other_lines[i][index+1:]

        text = ""
        for agent in self.agents[genome_id]:
            text += str(agent) + "\n"

        for line in other_lines:
            text += "\n" + line

        print(text)

        if stop is True:
            try:
                input()
            except KeyboardInterrupt:
                sys.exit(0)

        if erase is True:
            for i in range(len(self.agents[genome_id]) + len(other_lines)+2):
                sys.stdout.write("\033[F")
                sys.stdout.write("\033[K")
    
    def position_to_ring(self, size, center):
        """
        Casts the position to a ring grapical representation
        """

        positions = []
        for agent in self.agents[self.genome_to_show]:
            x = center[0] + .5 * size * math.cos(2 * math.pi * agent.position / self.ring_length)
            y = center[1] + .5 * size * math.sin(2 * math.pi * agent.position / self.ring_length)

            positions.append((x,y))

        return positions
                