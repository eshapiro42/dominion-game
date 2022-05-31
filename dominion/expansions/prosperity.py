import random
from .expansion import Expansion
from ..cards import cards, base_cards, prosperity_cards

class ProsperityExpansion(Expansion):
    name = 'Prosperity'

    def __init__(self, game, platinum_and_colony: bool | None = None):
        super().__init__(game)
        self.platinum_and_colony = platinum_and_colony

    @property
    def basic_card_piles(self):
        # If the expansion is configured to include Platinum and Colonies (e.g. via a recommended set), add the Platinum and Colonies piles to the basic piles
        if self.platinum_and_colony is not None:
            choice = True
        # Otherwise, the odds of using Platinum and Colony are equal to the proportion of Prosperity kingdom cards in the Supply
        else:
            num_prosperity_cards = len([card_class for card_class in self.supply.card_stacks if card_class in prosperity_cards.KINGDOM_CARDS])
            odds = num_prosperity_cards / 10
            print(f'Odds of using Platinum and Colony: {num_prosperity_cards}/10')
            choices = [True, False]
            weights = [odds, 1 - odds]
            choice = random.choices(choices, weights, k=1)[0]
        if choice:
            self.platinum_and_colony = True
            self.game.broadcast("Platinum and Colony are in play this game.")
            # The Colony pile size depends on the number of players:
            if self.supply.num_players == 2:
                colony_pile_size = 8
            else:
                colony_pile_size = 12
            # The Platinum pile size is always 12
            platinum_pile_size = 12
            return [(prosperity_cards.Colony, colony_pile_size), ([prosperity_cards.Platinum, platinum_pile_size])]
        else:
            self.platinum_and_colony = False
            print('Not using Platinum or Colony')
            return []

    @property
    def kingdom_card_classes(self):
        return prosperity_cards.KINGDOM_CARDS

    def additional_setup(self):
        # Each player starts off with no victory tokens
        for player in self.game.players:
            player.victory_tokens = 0
        # If the Trade Route is in the Supply, it requires additional setup of the Trade Route mat and Coin tokens
        if prosperity_cards.TradeRoute in self.supply.card_stacks:
            self.game.broadcast("The Trade Route is in play this game.")
            # Trade route mat starts off with no coin tokens
            self.supply.trade_route = 0
            # Each Victory card pile in the Supply starts off with one coin token on top (implemented via non-persistent post-gain hooks)
            victory_card_classes = [card_class for card_class in self.supply.card_stacks if cards.CardType.VICTORY in card_class.types]
            for victory_card_class in victory_card_classes:
                post_gain_hook = prosperity_cards.TradeRoute.TradeRoutePostGainHook(self.game, victory_card_class)
                self.supply.add_post_gain_hook(post_gain_hook, victory_card_class)  
        # If the Grand Market is in the Supply, add its Treasure hook
        if prosperity_cards.GrandMarket in self.supply.card_stacks:
            treasure_hook = prosperity_cards.GrandMarket.GrandMarketTreasureHook(self.game)
            self.game.add_treasure_hook(treasure_hook, base_cards.Copper)
        # If the Mint is in the Supply, add its post-gain hook
        if prosperity_cards.Mint in self.supply.card_stacks:
            post_gain_hook = prosperity_cards.Mint.MintPostGainHook(self.game, prosperity_cards.Mint)
            self.supply.add_post_gain_hook(post_gain_hook, prosperity_cards.Mint)
        # If the Peddler is in the Supply, add its pre-buy hook
        if prosperity_cards.Peddler in self.supply.card_stacks:
            pre_buy_hook = prosperity_cards.Peddler.PeddlerPreBuyHook(self.game)
            self.game.add_pre_buy_hook(pre_buy_hook, prosperity_cards.Peddler)
        # If the Talisman is in the Supply, add its post-buy hook to all cards in the Supply
        if prosperity_cards.Talisman in self.supply.card_stacks:
            post_buy_hook = prosperity_cards.Talisman.TalismanPostBuyHook(self.game)
            for card_class in self.supply.card_stacks:
                self.game.add_post_buy_hook(post_buy_hook, card_class)

    def heartbeat(self):
        # Display Trade Route info
        if prosperity_cards.TradeRoute in self.game.supply.card_stacks:
            # Find remaining Trade Route post gain hooks to see which Victory cards still have coin tokens
            victory_card_classes = [card_class for card_class in self.game.supply.card_stacks if cards.CardType.VICTORY in card_class.types]
            victory_card_classes_with_coin_tokens = []
            for victory_card_class in victory_card_classes:
                for post_gain_hook in self.game.supply.post_gain_hooks[victory_card_class]:
                    if isinstance(post_gain_hook, prosperity_cards.TradeRoute.TradeRoutePostGainHook):
                        victory_card_classes_with_coin_tokens.append(victory_card_class)
                        break
            sorted_victory_card_classes_with_coin_tokens = sorted(victory_card_classes_with_coin_tokens, key=lambda card_class: self.game.current_turn.get_cost(card_class))
            victory_card_names_with_coin_tokens = [card_class.name for card_class in sorted_victory_card_classes_with_coin_tokens]
            self.game.socketio.emit(
                "trade route",
                {
                    "victory_cards": victory_card_names_with_coin_tokens,
                    "tokens": self.game.supply.trade_route,
                },
                room=self.game.room
            )

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