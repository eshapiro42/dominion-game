from __future__ import annotations

from abc import ABCMeta, abstractmethod

from typing import TYPE_CHECKING, Callable, List, Optional, Tuple, Type

if TYPE_CHECKING:
    from ..cards.cards import Card, TreasureCard
    from ..game import Game
    from ..player import Player
    from ..supply import Supply


class Expansion(metaclass=ABCMeta):
    '''
    Base class for Dominion expansions.

    Args:
        game: The Game object to add the expansion into.
    '''
    def __init__(self, game: Game):
        self._game = game

    @property
    def game(self) -> Game:
        """
        The Game object to add the expansion into.
        """
        return self._game

    @property
    def supply(self) -> Supply:
        """
        The Supply for the Game this expansion is being added into.
        """
        return self.game.supply

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.name == other.name
        else:
            return NotImplemented
        
    @property
    @abstractmethod
    def name(self) -> str:
        """
        The name of this expansion. E.g., "Prosperity".
        """
        pass

    @property
    @abstractmethod
    def basic_card_piles(self) -> List[Tuple[Type[Card], int]]:
        """
        A list of tuples representing the basic card piles
        in this expansion and the quantities that should be
        included in the Game's Supply.

        The first element of each tuple is the Card's class
        and the second element is the quantity of that card
        to include.
        """
        pass

    @property
    @abstractmethod
    def kingdom_card_classes(self) -> List[Type[Card]]:
        """
        A list of Card classes that this expansion adds and
        which should be considered for inclusion in the
        Game's Supply.
        """
        pass

    @property
    @abstractmethod
    def game_end_conditions(self) -> List[Callable[[], Tuple[bool, Optional[str]]]]:
        """
        A list of functions that take no arguments and return
        a tuple of a boolean and an optional string. The boolean
        indicates whether the game has ended and the string is
        a message containing the reason why the game ended and
        which will be displayed to users.

        If the boolean returned is :obj:`False`, the game has
        not ended and so the second argument should be :obj:`None`.

        If the boolean returned is :obj:`True`, the second (string)
        argument must be provided.
        """
        pass

    def additional_setup(self):
        """
        If this expansion contains additional setup mechanisms
        that need to be performed before the Game starts, overload
        this method to perform the required actions.

        E.g., registering hooks to specific cards.
        """
        pass

    def heartbeat(self):
        """
        If this expansion contains additional information that
        needs to be sent with each heartbeat, overload this method.

        E.g., sending information about the Trade Route.
        """
        pass

    def order_treasures(self, player: Player, treasures: List[TreasureCard]) -> List[TreasureCard]:
        """
        If this expansion contains cards that care about the order
        in which Treasure cards are played, overload this method
        and use it to allow players to adjust the order of played
        Treasure cards.

        E.g., players will normally want to play the Horn of Plenty
        after their other Treasure cards.

        Args:
            player: The Player whose turn it is currently.
            treasures: A list of Treasure cards that have been played.
        """
        return treasures

    def scoring(self, player: Player) -> int:
        """
        If this expansion contains additional scoring mechanisms 
        beyond the base game, overload this method to return the
        expansion-specific score corresponding to a specific Player.
        This score will be added to their total score at the end of
        the Game.

        Args:
            player: The Player whose score is being calculated.

        Returns:
            The expansion-specific score for the Player.
        """
        return 0
