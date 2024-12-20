from math import inf
from .expansion import Expansion
from ..cards import cards, base_cards

class BaseExpansion(Expansion):
    name = 'Base'

    @property
    def basic_card_piles(self):
        basic_card_piles = []
        # Limitless piles of treasure cards
        treasure_card_classes = [base_cards.Copper, base_cards.Silver, base_cards.Gold]
        for treasure_card_class in treasure_card_classes:
            basic_card_piles.append((treasure_card_class, inf))
        # Victory card pile sizes depend on number of players
        victory_card_classes = [base_cards.Estate, base_cards.Duchy, base_cards.Province]
        if self.supply.num_players == 2:
            victory_pile_size = 8
        else:
            victory_pile_size = 12
        for victory_card_class in victory_card_classes:
            basic_card_piles.append((victory_card_class, victory_pile_size))
        # Curse card pile size depends on number of players
        curse_pile_size = (self.supply.num_players - 1) * 10
        basic_card_piles.append((base_cards.Curse, curse_pile_size))
        return basic_card_piles

    @property
    def kingdom_card_classes(self):
        return []

    @property
    def game_end_conditions(self):
        return [
            self.game_end_condition_province_pile_empty,
            self.game_end_condition_supply_piles_empty,
        ]

    def game_end_condition_province_pile_empty(self):
        if self.supply.card_stacks[base_cards.Province].is_empty:
            return True, 'All Provinces have been purchased.'
        else:
            return False, None

    def game_end_condition_supply_piles_empty(self):
        empty_stack_threshold = 3 if self.game.num_players <= 4 else 4
        if self.supply.num_empty_stacks >= empty_stack_threshold:
            empty_piles = [stack for stack in self.supply.card_stacks.values() if stack.is_empty]
            return True, f"Three Supply piles are empty:  {', '.join(map(str, empty_piles))}."
        else:
            return False, None

    def additional_setup(self):
        pass

    def scoring(self, player):
        victory_points = 0
        for card in player.all_cards:
            # Count only if it's a victory or curse card
            if cards.CardType.VICTORY in card.types or cards.CardType.CURSE in card.types:
                victory_points += card.points
        return victory_points