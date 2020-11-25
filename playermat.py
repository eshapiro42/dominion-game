from collections import deque
from copy import deepcopy
import cards
import random

class PlayerMat:
    def __init__(self, player):
        self.player = player
        self.game = self.player.game
        self.supply = self.player.game.supply
        self.deck = deque()
        self.discard_pile = deque()
        self.hand = deque()
        self.played_cards = deque()
        # Start with seven coppers and three estates
        self.gain(cards.Copper, quantity=7, from_supply=False)
        self.gain(cards.Estate, quantity=3, from_supply=False)
        self.shuffle()
        self.draw(5)

    def gain(self, card_class, quantity: int = 1, from_supply: bool = True):
        for _ in range(quantity):
            if not from_supply:
                card = card_class()
            else:
                card = self.supply.draw(card_class)
            card.owner = self.player
            self.discard_pile.append(card)

    def trash(self, card):
        self.supply.trash(card)

    def shuffle(self):
        self.deck.extend(self.discard_pile)
        self.discard_pile.clear()
        random.shuffle(self.deck)

    def draw(self, quantity: int = 1):
        for _ in range(quantity):
            try:
                card = self.deck.pop()
            except IndexError:
                self.shuffle()
                card = self.deck.pop()
            self.hand.append(card)

    def play(self, card):
        self.played_cards.append(card)
        self.hand.remove(card)

    def discard(self, card):
        self.discard_pile.append(card)
        self.hand.remove(card)

    def cleanup(self):
        # Discard hand from this turn
        self.discard_pile.extend(self.hand)
        self.hand.clear()
        # Discard cards played this turn
        self.discard_pile.extend(self.played_cards)
        self.played_cards.clear()
        # Draw a new hand of five cards
        self.draw(5)
 
    # TODO: Implement __repr__ method for PlayerMat
    # def __repr__(self):
    #     pass

    @property
    def all_cards(self):
        '''Concatenate all cards on the player mat (no side effects)'''
        return deepcopy(self.deck + self.discard_pile + self.hand + self.played_cards)

    @property
    def current_victory_points(self):
        victory_points = 0
        for card in self.all_cards:
            # Count only if it's a victory or curse card
            if cards.CardType.VICTORY in card.types or cards.CardType.CURSE in card.types:
                victory_points += card.points
        return victory_points
