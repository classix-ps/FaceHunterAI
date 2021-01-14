import time
import numpy
import random
import pyautogui
from pyclick import HumanClicker

class Execute:
    hc = None
    
    def __init__(self):
        self.hc = HumanClicker()
    
    def _get_random_think(self, divisor, term):
        rng = random.betavariate(1, 2) / divisor + term
        return rng
        
    def _get_random_move(self):
        rng = random.betavariate(1, 4) / 16 + 0.02
        return rng
        
    def execute_command(self, to_execute):
        for pos in to_execute:
            self.hc.move(pos, self._get_random_move())
            time.sleep(self._get_random_think(32, 0))
            self.hc.click()
            time.sleep(self._get_random_think(32, 0))