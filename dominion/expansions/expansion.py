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

    def add_additional_kingdom_cards(self):
        """
        If this expansion needs to add additional Kingdom cards to
        the Supply, overload this method to perform the required
        actions.

        This occurs after the initial 10 Kingdom cards are added to
        the Supply.

        E.g., Young Witch.
        """
        pass

    def additional_setup(self):
        """
        If this expansion contains additional setup mechanisms
        that need to be performed before the Game starts, overload
        this method to perform the required actions.

        This occurs after all Kingdom cards are added to the Supply.

        E.g., registering hooks to specific cards.
        """
        pass

    def additional_pre_buy_phase_actions(self):
        """
        If this expansion contains additional logic that
        needs to be performed before a player's Buy phase,
        overload this method to perform the required actions.
        
        E.g., using Coffers in the Guilds expansion.        
        """
        pass

    def heartbeat(self):
        """
        If this expansion contains additional information that
        needs to be sent with each heartbeat, overload this method.

        E.g., sending information about the Trade Route.

        Each expansion should handle caching of its own data.
        """
        pass

    def refresh_heartbeat(self):
        """
        Clear any cached heartbeat data.
        """
        pass

    def should_order_treasures(self, treasures: List[TreasureCard]) -> bool:
        """
        If this expansion contains cards that care about the order
        in which Treasure cards are played, overload this method
        and have it return True if a list of treasures should be
        ordered.

        This will usually be False except when playing with specific cards
        such as Horn of Plenty or Bank.
        """
        return False

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
