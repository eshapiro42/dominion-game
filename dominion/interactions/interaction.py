from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any, Optional, Deque, List, Type

if TYPE_CHECKING:
    from flask_socketio import SocketIO
    from ..cards.cards import Card, CardType
    from ..game import Game
    from ..player import Player
    from ..supply import Supply


class Interaction(metaclass=ABCMeta):
    """
    Base class for all interactions.

    Args:
        player: The :class:`Player` object corresponding to the player with whom to interact.
        socketio: The :class:`SocketIO` object to use for sending messages.
        sid: The socket ID of the player with whom to interact.

    """
    def __init__(self, player: Player, socketio: Optional[SocketIO] = None, sid: Optional[str] = None):
        self._player = player
        self._socketio = socketio
        self._sid = sid

    @property
    def player(self) -> Player:
        """
        The :class:`Player` object corresponding to the player with whom to interact.
        """
        return self._player

    @property
    def socketio(self) -> Optional[SocketIO]:
        """
        The :class:`SocketIO` object to use for sending messages.
        """
        return self._socketio

    @property
    def sid(self) -> Optional[str]:
        """
        The socket ID of the player with whom to interact.
        """
        return self._sid
    
    @sid.setter
    def sid(self, sid: Optional[str]):
        self._sid = sid

    def start(self):
        self._hand = self.player.hand
        self._played_cards = self.player.played_cards
        self._discard_pile = self.player.discard_pile
        self._deck = self.player.deck
        self._supply = self.player.game.supply
        self._game = self.player.game
        self._room = self.player.game.room

    @property
    def hand(self) -> Deque[Card]:
        """
        The player's hand.
        """
        return self._hand

    @property
    def played_cards(self) -> Deque[Card]:
        """
        The player's played cards from the current turn, if any.
        """
        return self._played_cards

    @property
    def discard_pile(self) -> Deque[Card]:
        """
        The player's discard pile.
        """
        return self._discard_pile

    @property
    def deck(self) -> Deque[Card]:
        """
        The player's deck.
        """
        return self._deck

    @property
    def supply(self) -> Supply:
        """
        The game's supply.
        """
        return self._supply

    @property
    def game(self) -> Game:
        """
        The game to which the player belongs.
        """
        return self._game

    @property
    def room(self) -> str:
        """
        The room to which the player belongs.
        """
        return self._room

    @abstractmethod
    def send(self, message: str):
        """
        Send a message to the player.
        """
        pass

    @abstractmethod
    def choose_card_from_hand(self, prompt: str, force: bool, invalid_cards: List[Card] | None = None) -> Card | None:
        """
        Request the player to choose a card from their hand.

        Args:
            prompt: The prompt to display to the player.
            force: Whether or not to force the player to choose a card.
            invalid_cards: Cards that are not allowed to be chosen. If None (the default), all cards of the specified type are allowed.
        """
        pass

    @abstractmethod
    def choose_cards_from_hand(self, prompt: str, force: bool, max_cards: int = 1, invalid_cards: List[Card] | None = None) -> List[Card]:
        """
        Request the player to choose cards from their hand.

        Args:
            prompt: The prompt to display to the player.
            force: Whether or not to force the player to choose the maximum number of cards. If False, the player may choose fewer or no cards.
            max_cards: The maximum number of cards to choose.
            invalid_cards: Cards that are not allowed to be chosen. If None (the default), all cards of the specified type are allowed.
        """
        pass

    @abstractmethod
    def choose_specific_card_class_from_hand(self, prompt: str, force: bool, card_class: Type[Card]) -> Card | None:
        """
        Request the player to choose a card of a specific card class from their hand.

        Args:
            prompt: The prompt to display to the player.
            force: Whether or not to force the player to choose a card.
            card_class: The card class to be chosen.
        """
        pass

    @abstractmethod
    def choose_specific_card_type_from_hand(self, prompt: str, card_type: CardType, force: bool = True) -> Card | None:
        """
        Request the player to choose a card of the specified type from their hand.

        Args:
            prompt: The prompt to display to the player.
            card_type: The card type to be chosen.
            force: Whether or not to force the player to choose a card.
        """
        pass

    @abstractmethod
    def choose_cards_of_specific_type_from_played_cards(self, prompt: str, force: bool, card_type: CardType, max_cards: int | None = 1, ordered: bool = False) -> List[Card]:
        """
        Request the player to choose cards of a specified type from their played cards.

        Args:
            prompt: The prompt to display to the player.
            force: Whether or not to force the player to choose the maximum number of cards. If False, the player may choose fewer or no cards.
            card_type: The card type to be chosen.
            max_cards: The maximum number of cards to choose. If None, all cards of the specified type are allowed.
            ordered: Whether or not the order of the cards matters (mainly for client-side display purposes).
        """
        pass

    @abstractmethod
    def choose_specific_card_type_from_played_cards(self, prompt: str, card_type: CardType) -> Card | None:
        """
        Request the player to choose a card of the specified type from their played cards.

        Args:
            prompt: The prompt to display to the player.
            card_type: The card type to be chosen.
        """
        pass

    @abstractmethod
    def choose_cards_of_specific_type_from_discard_pile(self, prompt: str, force: bool, card_type: CardType, max_cards: int | None = 1) -> List[Card]:
        """
        Request the player to choose cards of a specific type from their discard pile.

        Args:
            prompt: The prompt to display to the player.
            force: Whether or not to force the player to choose the maximum number of cards. If False, the player may choose fewer or no cards.
            card_type: The card type to be chosen.
            max_cards: The maximum number of cards to choose. If None, all cards of the specified type are allowed.
        """
        pass

    @abstractmethod
    def choose_card_from_discard_pile(self, prompt: str, force: bool) -> Card | None:
        """
        Request the player to choose a card from their discard pile.

        Args:
            prompt: The prompt to display to the player.
            force: Whether or not to force the player to choose a card.
        """
        pass

    @abstractmethod
    def choose_card_class_from_supply(self, prompt: str, max_cost, force: bool, invalid_card_classes: Optional[List[Type[Card]]] = None, exact_cost: bool = False) -> Optional[Type[Card]]:
        """
        Request the player to choose a card class from the supply.

        Args:
            prompt: The prompt to display to the player.
            max_cost: The maximum cost of the card class to be chosen.
            force: Whether or not to force the player to choose a card class.
            invalid_card_classes: A list of card classes that are not allowed to be chosen.
            exact_cost: Whether or not to choose a card class with the exact specified cost.
        """
        pass

    @abstractmethod
    def choose_specific_card_type_from_supply(self, prompt: str, max_cost: int, card_type: CardType, force: bool, exact_cost: bool = False) -> Optional[Type[Card]]:
        """
        Request the player to choose a card of the specified type from the supply.

        Args:
            prompt: The prompt to display to the player.
            max_cost: The maximum cost of the card class to be chosen.
            card_type: The card type to be chosen.
            force: Whether or not to force the player to choose a card class.
            exact_cost: Whether or not to choose a card class with the exact specified cost.
        """
        pass

    @abstractmethod
    def choose_specific_card_type_from_trash(self, prompt: str, max_cost: int, card_type: CardType, force: bool) -> Optional[Type[Card]]:
        """
        Request the player to choose a card of the specified type from the trash.

        Args:
            prompt: The prompt to display to the player.
            max_cost: The maximum cost of the card class to be chosen.
            card_type: The card type to be chosen.
            force: Whether or not to force the player to choose a card class.
        """
        pass

    @abstractmethod
    def choose_card_from_prizes(self, prompt: str) -> Optional[Card]:
        """
        Request the player to choose a prize. Only relevant for games using the
        Cornucopia expansion that include the Tournament in the supply.

        Args:
            prompt: The prompt to display to the player.
        """
        pass

    @abstractmethod
    def choose_yes_or_no(self, prompt: str) -> bool:
        """
        Request a yes or no response from the player.

        Args:
            prompt: The prompt to display to the player.

        Returns:
            :obj:`True` if the player chose yes, :obj:`False` if the player chose no.
        """
        pass

    @abstractmethod
    def choose_from_range(self, prompt: str, minimum: int, maximum: int, force: bool) -> int:
        """
        Request the player to choose from an inclusive range of integers.

        Args:
            prompt: The prompt to display to the player.
            minimum: The minimum value in the range.
            maximum: The maximum value in the range.
            force: Whether or not to force the player to choose a value.
        """
        pass

    @abstractmethod
    def choose_from_options(self, prompt: str, options: List[Any], force: bool) -> Any:
        """
        Request the player to choose from a list of options.

        Args:
            prompt: The prompt to display to the player.
            options: The list of options to choose from.
            force: Whether or not to force the player to choose an option.
        """
        pass

    @abstractmethod
    def choose_cards_from_list(self, prompt: str, cards: List[Card], force: bool, max_cards: int = 1, ordered: bool = False) -> List[Card]:
        """
        Request the player to choose cards from a list of cards.

        Args:
            prompt: The prompt to display to the player.
            cards: The list of cards to choose from.
            force: Whether or not to force the player to choose the maximum number of cards. If False, the player may choose fewer or no cards.
            max_cards: The maximum number of cards to choose.
            ordered: Whether or not the order of the cards matters (mainly for client-side display purposes).
        """
        pass

    @abstractmethod
    def new_turn(self):
        """
        Notify the player about the start of a new turn.
        """
        pass