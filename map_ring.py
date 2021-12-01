from utils import *

from map import Map

class Ring(Map):
    """
    A ring around which agents can turn
    """

    def __init__(self, ring_length:int) -> None:
        super().__init__()

        self.ring_length = ring_length