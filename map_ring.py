import math
import random

from map import Map2D
from agents import Agent
from utils import Position


class MapRing(Map2D):
    """
    A ring around which agents can turn
    """

    def __init__(
        self,
        noise:float = .01,
        ring_length:int = 25,
    ) -> None:

        super().__init__()

        self.noise = noise
        self.ring_length = ring_length

        # A ring agent should have N=2 available directions,
        #   how do these translate in the map?
        self.a_to_m_dir = [-1, 1]        

    def _init_agent_position(self, new_agent:Agent) -> Position:
        """
        Initialize a new agent's position in the map, uniform distribution
        Returns its position
        """

        return random.random() * self.ring_length

    def _move_agent(self, agent:Agent, current_position:Position) -> Position:
        """
        Moves an agent on the map, adds noise to the new position
        Returns its position
        """
        
        position_shift = self.a_to_m_dir[agent.direction] * agent.speed
        position_shift += self.noise * random.choice([-1,1])
        
        return (current_position + position_shift) % self.ring_length
    
    def _detect_others(self, agent:Agent, position:Position, all_positions:list[Position]) -> None:
        """
        Updates the agent's sensor based on the others' positions
        """
            
        has_seen_my_position = False
        for other_pos in all_positions:

            # An agent shouldn't activate its own sensors
            if other_pos == position:
                if has_seen_my_position is False:
                    has_seen_my_position = True
                    continue

            # The ring loops on itself, we have to check the modulo of the ring
            other_pos_modulo = [
                other_pos - self.ring_length,
                other_pos,
                other_pos + self.ring_length
            ]

            for other_modulo in other_pos_modulo:
                diff_pos = agent.position - other_modulo

                for r, d, s in agent.sensors:
                    if abs(diff_pos) >= r[0] and abs(diff_pos) < r[1]:
                        s[diff_pos <= 0] = True
                        break

            # Check if all the sensors are activated (therefore nothing more can be done)
            if all([state for r, d, s in agent.sensors for state in s]):
                break
    
    def get_2D_positions(self, size:float, center:Position) -> Position:
        """
        Casts the position to a ring grapical representation
        """

        return [
            (
                center[0] + .5 * size * math.cos(2 * math.pi * pos / self.ring_length),
                center[1] + .5 * size * math.sin(2 * math.pi * pos / self.ring_length)
            ) for _, pos in self.all_agents.values()
        ]
