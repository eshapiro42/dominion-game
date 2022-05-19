from __future__ import annotations

from abc import ABCMeta, abstractmethod
# from enum import Enum, auto
from typing import TYPE_CHECKING, Deque, Type


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
    from .cards.cards import Card
    from .game import Game
    from .player import Player


class Hook(metaclass=ABCMeta):
    """
    Base class for all hooks.

    Args:
        game: The game to which the hook belongs
    """
    def __init__(self, game: Game):
        self._game = game

    @property
    def game(self) -> Game:
        """
        The game to which the hook belongs.
        """
        return self._game

    @abstractmethod
    def __call__(self, *args, **kwargs):
        """
        Logic to be executed when the hook is activated.
        """
        pass

    @property
    @abstractmethod
    def persistent(self) -> bool:
        """
        Whether the hook should be removed after it is
        activated once.

        If :obj:`False`, the hook will be removed after it
        is activated for the first time. If :obj:`True`, it
        will not be removed unless explicitly removed by
        some other means.
        """
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
    Hook to activate after a player is finished playing treasure cards.
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


class PreCleanupHook(Hook):
    """
    Hook to activate before a player cleans up their played cards.
    """
    @abstractmethod
    def __call__(self):
        pass


class PostGainHook(Hook):
    """
    Hook to activate after a player gains a card.

    Args:
        game: The game to which the hook belongs.
        card_class: The card class of the card that was gained.
    """
    def __init__(self, game: Game, card_class: Type[Card]):
        super().__init__(game)
        self._card_class = card_class

    @property
    def card_class(self) -> Type[Card]:
        """
        The card class of the card that was gained.
        """
        return self._card_class

    @abstractmethod
    def __call__(self, player: Player, card: Card, where_it_went: Deque[Card]):
        """
        Logic to be executed when the hook is activated.

        Args:
            player: The player who gained the card.
            card: The card that was gained.
            where_it_went: The deque where the card ended up.
        """
        pass


class PreTurnHook(Hook):
    """
    Hook to activate before a player's turn.

    Args:
        game: The game to which the hook belongs.
        player: The player whose turn on which the hook should be activated.
    """
    def __init__(self, game: Game, player: Player):
        super().__init__(game)
        self._player = player

    @property
    def player(self) -> Player:
        """
        The player whose turn on which the hook should be activated.
        """
        return self._player

    @abstractmethod
    def __call__(self):
        pass