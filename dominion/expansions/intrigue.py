import random
from .expansion import Expansion
from ..cards import cards, base_cards, intrigue_cards
from ..hooks import PostGainHook

class IntrigueExpansion(Expansion):
    name = 'Intrigue'

    @property
    def basic_card_piles(self):
        '''Intrigue does not add any new basic cards.'''
        return []

    @property
    def kingdom_card_classes(self):
        '''Intrigue adds new possible kingdom cards.'''
        return intrigue_cards.KINGDOM_CARDS

    def additional_setup(self):
        '''Intrigue does not require any additional setup.'''
        pass

    @property
    def game_end_conditions(self):
        '''Intrigue does not add any new game end conditions.'''
        return []

    def scoring(self, player):
        '''Intrigue does not add any new scoring mechanisms.'''
        return 0