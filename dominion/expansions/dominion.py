from math import inf
from .expansion import Expansion
from ..cards import dominion_cards

class DominionExpansion(Expansion):
    name = 'Dominion'
    
    @property
    def basic_card_piles(self):
        return []

    @property
    def kingdom_card_classes(self):
        return dominion_cards.KINGDOM_CARDS

    @property
    def game_end_conditions(self):
        return []

    def additional_setup(self):
        pass

    def scoring(self, player):
        return 0