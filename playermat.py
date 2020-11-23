from collections import deque
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
            self.discard_pile.append(card)

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

    def discard(self, card):
        self.discard_pile.append(card)
        self.hand.remove(card)

    def cleanup(self):
        self.discard_pile.extend(self.hand)
        self.hand.clear()
        self.discard_pile.extend(self.played_cards)
        self.played_cards.clear()
        self.draw(5)

    def __repr__(self):
        pass
