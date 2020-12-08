from abc import ABCMeta, abstractmethod


class TreasureHook(metaclass=ABCMeta):
    def __init__(self, game):
        self.game = game

    @abstractmethod
    def __call__(self):
        pass

    @property
    @abstractmethod
    def persistent(self):
        pass


class PostGainHook(metaclass=ABCMeta):
    def __init__(self, card_class):
        self.card_class = card_class

    @abstractmethod
    def __call__(self, player, card, where_it_went):
        pass

    @property
    @abstractmethod
    def persistent(self):
        pass