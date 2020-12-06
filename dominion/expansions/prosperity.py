import random
from .expansion import Expansion
from ..cards import cards, prosperity_cards
from ..supply import PostGainHook

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
        # Each player starts off with no victory tokens
        for player in self.game.players:
            player.victory_tokens = 0
        # If the Trade Route is in the Supply, there's a lot of additional setup
        if prosperity_cards.TradeRoute in self.supply.card_stacks:
            # Trade route mat starts off with no coin tokens
            self.supply.trade_route = 0
            # Each Victory card pile in the Supply starts off with one coin token on top (implemented via non-persistent post-gain hooks)
            victory_card_classes = [card_class for card_class in self.supply.card_stacks if cards.CardType.VICTORY in card_class.types]
            for victory_card_class in victory_card_classes:
                post_gain_hook = self.TradeRoutePostGainHook(victory_card_class)
                self.supply.add_post_gain_hook(post_gain_hook, victory_card_class)
    

    @property
    def game_end_conditions(self):
        return [self.game_end_condition_colony_pile_empty]

    def game_end_condition_colony_pile_empty(self):
        # The game ends if Colonies are in the game and the Colony supply pile becomes empty
        if self.platinum_and_colony and self.supply.card_stacks[prosperity_cards.Colony].is_empty:
            return True, 'All Colonies have been purchased.'
        else:
            return False, None


    def scoring(self, player):
        return player.victory_tokens


    class TradeRoutePostGainHook(PostGainHook):
        persistent = False

        def __call__(self, player, card):
            game = player.game
            trade_route_before = game.supply.trade_route
            game.supply.trade_route += 1
            game.broadcast(f'{player} gained a {self.card_class.name} and moved a Coin token to the Trade Route mat ({trade_route_before} Coin tokens --> {game.supply.trade_route} Coin tokens).')