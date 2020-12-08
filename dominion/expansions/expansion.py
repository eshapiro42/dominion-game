from abc import ABCMeta, abstractmethod

class Expansion(metaclass=ABCMeta):
    def __init__(self, game):
        self.game = game
        self.supply = self.game.supply

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.name == other.name
        else:
            return NotImplemented
        
    @property
    @abstractmethod
    def name(self):
        pass

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

    def scoring(self):
        return 0
