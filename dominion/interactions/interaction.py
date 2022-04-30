from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any, Optional, Deque, List

if TYPE_CHECKING:
    from collections import deque
    from flask_socketio import SocketIO
    from ..cards.cards import Card, CardMeta, CardType
    from ..game import Game
    from ..player import Player
    from ..supply import Supply


class InteractionMeta(ABCMeta):
    """
    Metaclass for :class:`Interaction`.

    Mainly for typing purposes. An object of type :class:`InteractionMeta`
    will be an Interaction class itself, not an instance of it.
    """
    pass


class Interaction(metaclass=InteractionMeta):
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
    def display_supply(self):
        """
        Display the player's supply.
        """
        pass

    @abstractmethod
    def display_hand(self):
        """
        Display the player's hand.
        """
        pass

    @abstractmethod
    def display_discard_pile(self):
        """
        Display the player's discard pile.
        """
        pass

    @abstractmethod
    def choose_card_from_hand(self, prompt: str, force: bool) -> Optional[Card]:
        """
        Request the player to choose a card from their hand.

        Args:
            prompt: The prompt to display to the player.
            force: Whether or not to force the player to choose a card.
        """
        pass

    @abstractmethod
    def choose_specific_card_class_from_hand(self, prompt: str, force: bool, card_class: CardMeta) -> Optional[Card]:
        """
        Request the player to choose a card of a specific card class from their hand.

        Args:
            prompt: The prompt to display to the player.
            force: Whether or not to force the player to choose a card.
            card_class: The card class to be chosen.
        """
        pass

    @abstractmethod
    def choose_specific_card_type_from_hand(self, prompt: str, card_type: CardType) -> Optional[Card]:
        """
        Request the player to choose a card of the specified type from their hand.

        Args:
            prompt: The prompt to display to the player.
            card_type: The card type to be chosen.
        """
        pass

    @abstractmethod
    def choose_card_from_discard_pile(self, prompt: str, force: bool) -> Optional[Card]:
        """
        Request the player to choose a card from their discard pile.

        Args:
            prompt: The prompt to display to the player.
            force: Whether or not to force the player to choose a card.
        """
        pass

    @abstractmethod
    def choose_card_class_from_supply(self, prompt: str, max_cost, force: bool, invalid_card_classes: Optional[List[CardMeta]] = None, exact_cost: bool = False) -> Optional[CardMeta]:
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
    def choose_specific_card_type_from_supply(self, prompt: str, max_cost: int, card_type: CardType, force: bool) -> Optional[CardMeta]:
        """
        Request the player to choose a card of the specified type from the supply.

        Args:
            prompt: The prompt to display to the player.
            max_cost: The maximum cost of the card class to be chosen.
            card_type: The card type to be chosen.
            force: Whether or not to force the player to choose a card class.
        """
        pass

    @abstractmethod
    def choose_specific_card_type_from_trash(self, prompt: str, max_cost: int, card_type: CardType, force: bool) -> Optional[CardMeta]:
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
    def new_turn(self):
        """
        Notify the player about the start of a new turn.
        """
        pass