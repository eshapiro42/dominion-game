from abc import ABCMeta, abstractmethod

class Expansion(metaclass=ABCMeta):
    def __init__(self, game):
        self.game = game
        self.supply = self.game.supply
        
    @property
    @abstractmethod
    def basic_card_piles(self):
        pass

    @property
    @abstractmethod
    def kingdom_card_classes(self):
        pass

    @property
    @abstractmethod
    def game_end_conditions(self):
        pass

    def additional_setup(self):
        pass
