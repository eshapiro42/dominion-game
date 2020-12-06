import random
from .expansion import Expansion
from ..cards import prosperity_cards
from ..supply import Supply

class ProsperityExpansion(Expansion):
    platinum_and_colony = False

    @property
    def basic_card_piles(self):
        # The odds of using Platinum and Colony are equal to the proportion of Prosperity kingdom cards in the Supply
        num_prosperity_cards = len([card_class for card_class in self.supply.card_stacks if card_class in prosperity_cards.KINGDOM_CARDS])
        odds = num_prosperity_cards / 10
        print(f'Odds of using Platinum and Colony: {num_prosperity_cards}/10')
        choices = [True, False]
        weights = [odds, 1 - odds]
        choice = random.choices(choices, weights, k=1)[0]
        if choice:
            self.platinum_and_colony = True
            print('Using Platinum and Colony')
            # The Colony pile size depends on the number of players:
            if self.supply.num_players == 2:
                colony_pile_size = 8
            else:
                colony_pile_size = 12
            # The Platinum pile size is always 12
            platinum_pile_size = 12
            return [(prosperity_cards.Colony, colony_pile_size), ([prosperity_cards.Platinum, platinum_pile_size])]
        else:
            print('Not using Platinum or Colony')
            return []

    @property
    def kingdom_card_classes(self):
        return prosperity_cards.KINGDOM_CARDS

    def additional_setup(self):
        # Trade route mat starts off with no victory tokens
        self.supply.trade_route = 0
        # Each player starts off with no victory tokens
        for player in self.game.players:
            player.victory_tokens = 0

    
    @property
    def game_end_conditions(self):
        return [
            self.game_end_condition_colony_pile_empty
        ]

    def game_end_condition_colony_pile_empty(self):
        if self.platinum_and_colony and self.supply.card_stacks[prosperity_cards.Colony].is_empty:
            return True, 'All Colonies have been purchased.'
        else:
            return False, None