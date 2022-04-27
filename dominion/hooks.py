from __future__ import annotations

from abc import ABCMeta, abstractmethod
# from enum import Enum, auto
from typing import TYPE_CHECKING


# Might use these later to expand the hooks system
# 
# 
# class HookScope(Enum):
#     PLAYER = auto()
#     GAME = auto()
# 
# 
# class HookPersistence(Enum):
#     ONCE = auto()
#     TURN = auto()
#     FOREVER = auto()


if TYPE_CHECKING:
    from collections import deque
    from .cards.cards import Card
    from .game import Game
    from .player import Player


class Hook(metaclass=ABCMeta):
    """
    Base class for all hooks.

    Args:
        game: the game to which the hook belongs
    """
    def __init__(self, game: Game):
        self.game= game

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass

    @abstractmethod
    def persistent(self):
        pass


# class PreAttackHook(Hook):
# Might use this later for Reactions instead of the current attack/reaction system


class TreasureHook(Hook):
    """
    Hook to activate when a player plays a treasure card.
    """
    @abstractmethod
    def __call__(self):
        pass


class PostTreasureHook(Hook):
    """
    Hook to activate after a players plays treasure cards.
    """

    @abstractmethod
    def __call__(self):
        pass


class PreBuyHook(Hook):
    """
    Hook to activate before a player buys a card.
    """
    @abstractmethod
    def __call__(self):
        pass


class PostGainHook(Hook):
    """
    Hook to activate after a player gains a card.
    """
    def __init__(self, game: Game, card_class: type[Card]):
        super().__init__(game)
        self.card_class = card_class

    @abstractmethod
    def __call__(self, player: Player, card: Card, where_it_went: deque):
        pass
