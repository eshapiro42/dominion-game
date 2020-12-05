import copy
import itertools
import operator
import prettytable
import random
from abc import ABCMeta, abstractmethod
from math import inf
from .cards import cards, base_cards


class SupplyStackEmptyError(Exception):
    '''Raised when a supply stack is empty
    
    Attributes:
        card_class: class of card whose supply stack is empty
    '''
    def __init__(self, card_class):
        message = f'{card_class.name} supply stack is empty'
        super().__init__(message)


class Customization:
    required_card_classes = set() # If nonempty, ensures that each card in the list ends up in the supply
    distribute_cost = False # If toggled, ensures there are at least two cards each of cost {2, 3, 4, 5}
    disable_attack_cards = False # If toggled, Attack cards are not allowed
    # require_plus_two_action = False # If toggled, ensures there is at least one card with '+2 Actions'
    # require_drawer = False # If toggled, ensures there is at least one card with '>= +1 Cards'
    # require_buy = False # If toggled, ensures there is at least one card with '>= +1 Buys'
    # require_trashing = False # If toggled, ensures there is at least one card that allows trashing


class Supply:
    def __init__(self, num_players):
        self.num_players = num_players
        self.card_stacks = {}
        self.customization = Customization()
        # TODO: Remove these (they are for debugging specific cards)
        self.customization.required_card_classes.add(base_cards.Bandit)

    def setup(self):
        self.select_treasure_cards()
        self.select_victory_cards()
        self.select_curse_cards()
        self.select_kingdom_cards()
        self.create_trash_pile()

    def select_treasure_cards(self):
        # Limitless stacks of treasure cards
        self.treasure_card_classes = [base_cards.Copper, base_cards.Silver, base_cards.Gold]
        for card_class in self.treasure_card_classes:
            self.card_stacks[card_class] = InfiniteSupplyStack(card_class)

    def select_victory_cards(self):
        # Victory card stack sizes depend on number of players
        if self.num_players == 2:
            victory_stack_size = 8
        else:
            victory_stack_size = 12
        self.victory_card_classes = [base_cards.Estate, base_cards.Duchy, base_cards.Province]
        for card_class in self.victory_card_classes:
            self.card_stacks[card_class] = FiniteSupplyStack(card_class, victory_stack_size)

    def select_curse_cards(self):
        # Curse card stack size depends on number of players
        curse_stack_size = (self.num_players - 1) * 10
        self.card_stacks[base_cards.Curse] = FiniteSupplyStack(base_cards.Curse, curse_stack_size)

    def select_kingdom_cards(self):
        selected_kingdom_card_classes = []
        # Add in required cards
        for card_class in self.customization.required_card_classes:
            selected_kingdom_card_classes.append(card_class)
        if self.customization.disable_attack_cards:
            # Filter out attack cards
            possible_kingdom_card_classes = [card_class for card_class in copy.deepcopy(base_cards.KINGDOM_CARDS) if cards.CardType.ATTACK not in card_class.types]
        else:
            # All cards are viable
            possible_kingdom_card_classes = copy.deepcopy(base_cards.KINGDOM_CARDS)
        if self.customization.distribute_cost:
            # Make sure at least two cards each of cost {2, 3, 4, 5} (this totals 8 cards)
            possible_kingdom_card_classes_by_cost = {cost: [card_class for card_class in possible_kingdom_card_classes if card_class.cost == cost] for cost in range(2, 6)}
            for cost in range(2, 6):
                card_classes_of_cost = random.sample(possible_kingdom_card_classes_by_cost[cost], 2)
                for card_class in card_classes_of_cost:
                    selected_kingdom_card_classes.append(card_class)
                    possible_kingdom_card_classes.remove(card_class)
        # Select the remaining cards at random
        num_cards_remaining = 10 - len(selected_kingdom_card_classes)
        selected_kingdom_card_classes += random.sample(base_cards.KINGDOM_CARDS, num_cards_remaining)
        # Sort kingdom cards first by cost, then by name
        for card_class in sorted(selected_kingdom_card_classes, key=lambda card_class: (card_class.cost, card_class.name)):
            # Stacks of ten kingdom cards each
            self.card_stacks[card_class] = FiniteSupplyStack(card_class, 10)

    def create_trash_pile(self):
        self.trash_pile = {card_class: 0 for card_class in self.card_stacks}

    def draw(self, card_class):
        return self.card_stacks[card_class].draw()

    def trash(self, card):
        card_class = type(card)
        self.trash_pile[card_class] += 1

    def get_table(self):
        supply_table = prettytable.PrettyTable(hrules=prettytable.ALL)
        supply_table.field_names = ['Number', 'Card', 'Cost', 'Type', 'Quantity', 'Description']
        for idx, card_class in enumerate(sorted(self.card_stacks.keys(), key=lambda x: (x.types[0].value, x.cost))):
            quantity = self.card_stacks[card_class].cards_remaining
            types = ', '.join([type.name.lower().capitalize() for type in card_class.types])
            supply_table.add_row([idx + 1, card_class.name, card_class.cost, types, quantity, card_class.description])
        return supply_table

    def __str__(self):
        supply_table = self.get_table()
        return supply_table.get_string()

    @property
    def num_empty_stacks(self):
        return [stack.is_empty for stack in self.card_stacks.values()].count(True)


class SupplyStack(metaclass=ABCMeta):
    @abstractmethod
    def draw(self):
        pass

    @property
    @abstractmethod
    def cards_remaining(self):
        pass

    @property
    @abstractmethod
    def is_empty(self):
        pass


class InfiniteSupplyStack(SupplyStack):
    def __init__(self, card_class):
        self.card_class = card_class
        self._cards_remaining = inf

    def draw(self):
        card = self.card_class()
        return card

    @property
    def cards_remaining(self):
        return self._cards_remaining

    @property
    def is_empty(self):
        return False


class FiniteSupplyStack(SupplyStack):
    def __init__(self, card_class, size):
        self.card_class = card_class
        self._cards_remaining = size

    def draw(self):
        if not self.is_empty:
            card = self.card_class()
            self._cards_remaining -= 1
            return card
        else:
            raise SupplyStackEmptyError(self.card_class)

    @property
    def cards_remaining(self):
        return self._cards_remaining

    @property
    def is_empty(self):
        return self._cards_remaining == 0

    def __repr__(self):
        return self.card_class.name