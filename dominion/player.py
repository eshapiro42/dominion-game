from __future__ import annotations

import random

from collections import deque
from typing import TYPE_CHECKING, Optional, Deque, List, Type

from .cards import base_cards, cornucopia_cards, prosperity_cards
from .expansions import ProsperityExpansion
from .grammar import a, s
from .supply import SupplyStackEmptyError

if TYPE_CHECKING:
    from flask_socketio import SocketIO
    from .cards.cards import Card
    from .game import Game
    from .interactions.interaction import Interaction
    from .supply import Supply
    from .turn import Turn


class Player:
    """
    Player object representing a player's state.

    Args:
        game: The game to which the Player belongs.
        name: The name of the Player.
        interactions_class: The class of interactions to use for the Player.
        socketio: The socketio object to use for the Player.
        sid: The socket ID of the Player.
    """
    def __init__(self, game: Game, name: str, interactions_class: Type[Interaction], socketio: Optional[SocketIO] = None, sid: Optional[str] = None):
        self._game = game
        self._name = name
        self._turn = None
        self._turns_played = 0
        self._sid = sid
        self._interactions = interactions_class(player=self, socketio=socketio, sid=sid)
        self._deck = deque()
        self._discard_pile = deque()
        self._hand = deque()
        self._played_cards = deque()
        # self.victory_tokens = 0
        # Start with seven coppers and three estates
        self.gain(base_cards.Copper, quantity=7, from_supply=False, message=False)
        self.gain(base_cards.Estate, quantity=3, from_supply=False, message=False)
        self.shuffle()
        # Draw a hand of five cards
        self.draw(5, message=False)

    @property
    def game(self) -> Game:
        """
        The game to which the Player belongs.
        """
        return self._game

    @property
    def name(self) -> str:
        """
        The name of the Player.
        """
        return self._name

    @property
    def turn(self) -> Optional[Turn]:
        """
        The Player's current Turn.
        """
        return self._turn

    @turn.setter
    def turn(self, turn: Turn):
        self._turn = turn

    @property
    def turns_played(self) -> int:
        """
        The number of turns this Player has taken so far.
        """
        return self._turns_played

    @turns_played.setter
    def turns_played(self, turns_played: int):
        self._turns_played = turns_played

    @property
    def supply(self) -> Supply:
        """
        The Supply belonging to this Player's Game.
        """
        return self.game.supply

    @property
    def interactions(self) -> Interaction:
        """
        The Interaction object for the Player.
        """
        return self._interactions

    @property
    def deck(self) -> Deque[Card]:
        """
        The Player's deck.
        """
        return self._deck

    @property
    def discard_pile(self) -> Deque[Card]:
        """
        The Player's discard pile.
        """
        return self._discard_pile

    @property
    def hand(self) -> Deque[Card]:
        """
        The Player's hand.
        """
        return self._hand

    @property
    def played_cards(self) -> Deque[Card]:
        """
        The Player's played cards from the current Turn.
        """
        return self._played_cards        

    def get_other_players(self) -> List[Player]:
        """
        Get a list of other players in the correct turn order.
        """
        # Find this player's position in the turn order
        idx = self.game.turn_order.index(self)
        # Get the order of players whose turns are before and after
        players_before = self.game.turn_order[:idx]
        players_after = self.game.turn_order[idx + 1:]
        # Other players are those after, then those before, in the correct turn order
        self.other_players = players_after + players_before

    def process_post_gain_hooks(self, card, where_it_went):
        """
        Process registered hooks after a card is gained.

        Args:
            card: The card that was gained.
            where_it_went: The deque to which the card was gained.
        """
        # Check if there are any game-wide post-gain hooks caused by gaining the card
        expired_hooks = []
        if type(card) in self.supply.post_gain_hooks:
            # Activate any post-gain hooks caused by gaining the card
            for post_gain_hook in self.supply.post_gain_hooks[type(card)]:
                post_gain_hook(self, card, where_it_went)
                if not post_gain_hook.persistent:
                    expired_hooks.append(post_gain_hook)
            # Remove any non-persistent hooks
            for hook in expired_hooks:
                self.supply.post_gain_hooks[type(card)].remove(hook)
        if self.turn is not None:
            # Check if there are any turn-wide post-gain hooks caused by gaining the card
            expired_hooks = []
            if type(card) in self.turn.post_gain_hooks:
                # Activate any post-gain hooks caused by gaining the card
                for post_gain_hook in self.turn.post_gain_hooks[type(card)]:
                    post_gain_hook(self, card, where_it_went)
                    if not post_gain_hook.persistent:
                        expired_hooks.append(post_gain_hook)
                # Remove any non-persistent hooks
                for hook in expired_hooks:
                    self.turn.post_gain_hooks[type(card)].remove(hook)

    def gain(self, card_class: Type[Card], quantity: int = 1, from_supply: bool = True, message: bool = True, ignore_hooks: bool = False):
        """
        Gain a card.

        Args:
            card_class: The class of the Card to gain.
            quantity: The number of Cards to gain.
            from_supply: Whether the Card is being gained from the Supply.
            message: Whether to broadcast a message to all Players saying that the card was gained.
            ignore_hooks: Whether to activate any post-gain Hooks registered to this card.
        """
        for _ in range(quantity):
            if not from_supply:
                card = card_class()
            else:
                try:
                    card = self.supply.draw(card_class)
                except SupplyStackEmptyError:
                    self.game.broadcast(f'{self.name} could not gain {a(card_class.name)} since that supply pile is empty.')
                    return
            card.owner = self
            self.discard_pile.append(card)
            if message:
                self.game.broadcast(f'{self.name} gained {a(card_class.name)}.')
            if not ignore_hooks:
                self.process_post_gain_hooks(card, self.discard_pile)

    def gain_without_hooks(self, card_class: Type[Card], quantity: int = 1, from_supply: bool = True, message: bool = True):
        """
        Gain a card without activating any post-gain Hooks registered to this card.

        Equivalent to calling 

        .. highlight:: python
        .. code-block:: python
            
            self.gain(..., ignore_hooks=True)

        Args:
            card_class: The class of the Card to gain.
            quantity: The number of Cards to gain.
            from_supply: Whether the Card is being gained from the Supply.
            message: Whether to broadcast a message to all Players saying that the card was gained.
        """
        self.gain(card_class, quantity, from_supply, message, ignore_hooks=True)

    def gain_to_hand(self, card_class: Type[Card], quantity: int = 1, from_supply: bool = True, message: bool = True):
        """
        Gain a card to the Player's hand.

        Args:
            card_class: The class of the Card to gain.
            quantity: The number of Cards to gain.
            from_supply: Whether the Card is being gained from the Supply.
            message: Whether to broadcast a message to all Players saying that the card was gained.
        """
        for _ in range(quantity):
            if not from_supply:
                card = card_class()
            else:
                try:
                    card = self.supply.draw(card_class)
                except SupplyStackEmptyError:
                    self.game.broadcast(f'{self.name} could not gain {a(card_class.name)} since that supply pile is empty.')
                    return
            card.owner = self
            self.hand.append(card)
            if message:
                self.game.broadcast(f'{self.name} gained {a(card_class.name)} into their hand.')
            self.process_post_gain_hooks(card, self.hand)

    def gain_to_deck(self, card_class: Type[Card], quantity: int = 1, from_supply: bool = True, message: bool = True):
        """
        Gain a card to the Player's deck.

        Args:
            card_class: The class of the Card to gain.
            quantity: The number of Cards to gain.
            from_supply: Whether the Card is being gained from the Supply.
            message: Whether to broadcast a message to all Players saying that the card was gained.
        """
        for _ in range(quantity):
            if not from_supply:
                card = card_class()
            else:
                try:
                    card = self.supply.draw(card_class)
                except SupplyStackEmptyError:
                    self.game.broadcast(f'{self.name} could not gain {a(card_class.name)} since that supply pile is empty.')
                    return
            card.owner = self
            self.deck.append(card)
            if message:
                self.game.broadcast(f'{self.name} gained {a(card_class.name)} onto their deck.')
            self.process_post_gain_hooks(card, self.deck)

    def shuffle(self):
        """
        Shuffle the Player's discard pile into their deck.
        """
        self.game.broadcast(f'{self.name} shuffled their deck.')
        self.deck.extend(self.discard_pile)
        self.discard_pile.clear()
        random.shuffle(self.deck)

    def take_from_deck(self) -> Card | None:
        """
        Take a Card from the Player's deck.

        This orphans the card and it must explicitly be added to another deque.

        Returns:
            card: The Card that was taken from the Player's deck, or :obj:`None`
                  if their deck is empty even after shuffling.
        """
        try:
            card = self.deck.pop()
        except IndexError: # If a card cannot be taken, shuffle
            self.shuffle()
            try:
                card = self.deck.pop()
            except IndexError: # If a card still cannot be drawn, there are none left
                card = None
        return card

    def draw(self, quantity: int = 1, message: bool = True) -> List[Card]:
        """
        Draw Cards from the Player's deck into their hand.

        Args:
            quantity: The number of Cards to draw.
            message: Whether to broadcast a message to all Players saying that Cards were drawn.

        Returns:
            A list of Cards that were drawn.
        """
        drawn_cards = []
        for _ in range(quantity):
            card = self.take_from_deck()
            if card is not None:
                self.hand.append(card)
                drawn_cards.append(card)
        if message:
            if quantity == 0:
                pass
            elif len(drawn_cards) == quantity:
                self.game.broadcast(f"+{s(quantity, 'card')} → {s(len(self.hand), 'card')} in hand.")
                self.interactions.send(f"You drew: {', '.join(map(str, drawn_cards))}.")
            elif 1 <= len(drawn_cards) < quantity:
                self.game.broadcast(f"{self} had only {s(len(drawn_cards), 'card')} left to draw from.")
                self.game.broadcast(f"+{s(len(drawn_cards), 'card')} → {s(len(self.hand), 'card')} in hand.")
                self.interactions.send(f"You drew: {', '.join(map(str, drawn_cards))}.")
            elif not drawn_cards:
                self.game.broadcast(f'{self} had no cards left to draw from.')
        return drawn_cards

    def play(self, card: Card):
        """
        Move a card from the Player's hand to the Player's played cards.

        If the card is not in the Player's hand, it is still added to 
        the Player's played cards, but care must be taken to ensure that
        the card is not being duplicated.

        Args:
            card: The Card to play.
        """
        try:
            self.hand.remove(card)
        except ValueError:
            pass
        self.played_cards.append(card)

    def discard(self, card: Card, message: bool = True):
        """
        Discard a card from the Player's hand.

        Args:
            card: The Card to discard.
            message: Whether to broadcast a message to all Players saying that the card was discarded.
        """
        self.discard_pile.append(card)
        self.hand.remove(card)
        if message:
            self.game.broadcast(f'{self.name} discarded {a(card)}.')

    def trash(self, card: Card, message: bool = True):
        """
        Trash a card from the Player's hand.

        Args:
            card: The Card to trash.
            message: Whether to broadcast a message to all Players saying that the card was trashed.
        """
        self.supply.trash(card)
        self.hand.remove(card)
        if message:
            self.game.broadcast(f'{self.name} trashed {a(card)}.')

    def trash_played_card(self, card: Card, message: bool = True):
        """
        Trash a card from the Player's played cards.

        Args:
            card: The Card to trash.
            message: Whether to broadcast a message to all Players saying that the card was trashed.
        """
        self.supply.trash(card)
        try:
            self.played_cards.remove(card)
            if message:
                self.game.broadcast(f'{self.name} trashed {a(card)}.')
        except ValueError:
            pass

    def take_from_trash(self, card_class: Type[Card]):
        """
        Take a card from the Trash and set its owner to the Player.

        This orphans the card and it must explicitly be added to another deque.

        Args:
            card_class: The class of the Card to take.
        """
        try:
            card = self.supply.trash_pile[card_class].pop()
            card.owner = self
        except IndexError: # If a card cannot be taken, there are none left
            card = None
        return card

    def gain_from_trash(self, card_class: Type[Card], message: bool = True):
        """
        Gain a card from the Trash.

        Args:
            card_class: The class of the Card to gain.
            message: Whether to broadcast a message to all Players saying that the card was gained.
        """
        card = self.take_from_trash(card_class)
        if card is not None:
            self.discard_pile.append(card)
            self.process_post_gain_hooks(card, self.discard_pile)
            if message:
                self.game.broadcast(f'{self.name} gained {a(card)} from the trash.')

    def cleanup(self):
        """
        Cleanup after the Player's turn has finished.

        Discards all cards from the Player's hand and played cards,
        then draws a new hand of five cards
        """
        # Discard hand from this turn
        self.discard_pile.extend(self.hand)
        self.hand.clear()
        # Discard cards played this turn
        self.discard_pile.extend(self.played_cards)
        self.played_cards.clear()
        # Draw a new hand of five cards
        self.draw(5, message=False)
 
    def __repr__(self):
        return f'Player({self.name})'

    def __str__(self):
        return self.name
        
    @property
    def all_cards(self) -> set[Card]:
        '''
        Concatenate all cards belonging to the Player (no side effects).

        Returns:
            A set of all the Player's cards.
        '''
        return set(self.deck + self.discard_pile + self.hand + self.played_cards)

    @property
    def current_victory_points(self) -> int:
        """
        The Player's current victory points.
        """
        victory_points = 0
        # Add up all different point methods across added expansions
        for expansion in self.supply.customization.expansions:
            victory_points += expansion.scoring(self)
        return victory_points

    @property
    def sid(self) -> str:
        """
        The Player's socket ID.
        """
        return self._sid

    @sid.setter
    def sid(self, new_sid):
        self._sid = new_sid
        self.interactions.sid = new_sid

    def get_info(self):
        info = {
            "name": self.name,
            "hand_size": len(self.hand),
            "discard_size": len(self.discard_pile),
            "deck_size": len(self.deck),
        }
        if ProsperityExpansion in self.game.expansions:
            info["victory_tokens"] = self.victory_tokens
        return info
