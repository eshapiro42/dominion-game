from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

class Turn:
    def __init__(self, player):
        self.player = player
        print(f"{self.player}'s turn.")
        print(f"Hand: {self.player.player_mat.hand}")
        action = input('What would you like to do?')
        self.player.player_mat.cleanup()
        

class Phase(metaclass=ABCMeta):
    @abstractmethod
    def start(self):
        pass


class ActionPhase(Phase):
    def __init__(self):
        self.actions_remaining = 1


class BuyPhase(Phase):
    def __init__(self):
        self.buys_remaining = 1


class CleanupPhase(Phase):
    pass