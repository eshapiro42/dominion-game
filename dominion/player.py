import prettytable
import random
from collections import deque
from copy import deepcopy
from .cards import cards
from .supply import SupplyStackEmptyError


class Player:
    def __init__(self, game, name, interactions_class, socketio=None, sid=None):
        self.game = game
        self.name = name
        self.turn = None
        self.supply = self.game.supply
        self.interactions = interactions_class(player=self, socketio=socketio, sid=sid)
        self.deck = deque()
        self.discard_pile = deque()
        self.hand = deque()
        self.played_cards = deque()
        # Start with seven coppers and three estates
        self.gain(cards.Copper, quantity=7, from_supply=False)
        self.gain(cards.Estate, quantity=3, from_supply=False)
        self.shuffle()
        # Draw a hand of five cards
        self.draw(5)

    def gain(self, card_class, quantity: int = 1, from_supply: bool = True):
        for _ in range(quantity):
            if not from_supply:
                card = card_class()
            else:
                try:
                    card = self.supply.draw(card_class)
                except SupplyStackEmptyError:
                    self.game.broadcast(f'{self.name} could not gain a {card_class} since that supply pile is empty.')
                    return
            card.owner = self
            self.discard_pile.append(card)

    def gain_to_hand(self, card_class, quantity: int = 1, from_supply: bool = True):
        for _ in range(quantity):
            if not from_supply:
                card = card_class()
            else:
                try:
                    card = self.supply.draw(card_class)
                except SupplyStackEmptyError:
                    self.game.broadcast(f'{self.name} could not gain a {card_class} since that supply pile is empty.')
            card.owner = self
            self.hand.append(card)

    def shuffle(self):
        self.game.broadcast(f'{self.name} shuffled their deck.')
        self.deck.extend(self.discard_pile)
        self.discard_pile.clear()
        random.shuffle(self.deck)

    def take_from_deck(self):
        try:
            card = self.deck.pop()
        except IndexError: # If a card cannot be taken, shuffle
            self.shuffle()
            try:
                card = self.deck.pop()
            except IndexError: # If a card still cannot be drawn, there are none left
                card = None
        return card

    def draw(self, quantity: int = 1):
        drawn_cards = []
        for _ in range(quantity):
            card = self.take_from_deck()
            if card is not None:
                self.hand.append(card)
                drawn_cards.append(card)
        return drawn_cards

    def play(self, card):
        try:
            self.hand.remove(card)
            self.played_cards.append(card)
        except ValueError:
            pass

    def discard(self, card):
        self.discard_pile.append(card)
        self.hand.remove(card)

    def trash(self, card):
        self.supply.trash(card)
        self.hand.remove(card)

    def trash_played_card(self, card):
        self.supply.trash(card)
        try:
            self.played_cards.remove(card)
        except ValueError:
            pass

    def cleanup(self):
        # Discard hand from this turn
        self.discard_pile.extend(self.hand)
        self.hand.clear()
        # Discard cards played this turn
        self.discard_pile.extend(self.played_cards)
        self.played_cards.clear()
        # Draw a new hand of five cards
        self.draw(5)
 
    def __repr__(self):
        return f'Player({self.name})'

    def __str__(self):
        return self.name
        
    @property
    def all_cards(self):
        '''Concatenate all cards on the player mat (no side effects)'''
        return set(self.deck + self.discard_pile + self.hand + self.played_cards)

    @property
    def current_victory_points(self):
        victory_points = 0
        for card in self.all_cards:
            # Count only if it's a victory or curse card
            if cards.CardType.VICTORY in card.types or cards.CardType.CURSE in card.types:
                victory_points += card.points
        return victory_points
