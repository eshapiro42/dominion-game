import copy
from importlib.metadata import requires
import prettytable
import random
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from math import inf
from .cards import cards, base_cards, prosperity_cards, intrigue_cards


class SupplyStackEmptyError(Exception):
    '''Raised when a supply stack is empty.
    
    Attributes:
        card_class (:opt:`type(cards.Card)`): Class of card whose supply stack is empty
    '''
    def __init__(self, card_class):
        message = f'{card_class.name} supply stack is empty'
        super().__init__(message)


class Customization:
    '''
    Customization options for the Supply

    Attributes:
        expansions (:obj:`set` of :obj:`expansion.Expansion`): Set of Expansions to be chosen from in the Supply.
        required_card_classes (:obj:`set` of :obj:`type(card.Card)`): Set of card classes to require in the Supply.
        distribute_cost (:obj:`bool`): If :obj:`True`, ensures that there are at least two cards each of cost 2, 3, 4 and 5 in the Supply.
        distribute_attack_cards (:obj:`bool`): If :obj:`True`, Attack cards are not allowed in the Supply.
    '''
    def __init__(self):
        self.expansions = set([])
        self.required_card_classes = set([]) # If nonempty, ensures that each card in the list ends up in the supply
        self.distribute_cost = False # If toggled, ensures there are at least two cards each of cost {2, 3, 4, 5}
        self.disable_attack_cards = False # If toggled, Attack cards are not allowed
        self.require_plus_two_action = False # If toggled, ensures there is at least one card with '+2 Actions'
        self.require_drawer = False # If toggled, ensures there is at least one card with '>= +1 Cards'
        self.require_buy = False # If toggled, ensures there is at least one card with '>= +1 Buys'
        self.require_trashing = True # If toggled, ensures there is at least one card that allows trashing


class Supply:
    def __init__(self, num_players):
        self.num_players = num_players
        self.card_stacks = {}
        self.post_gain_hooks = defaultdict(list)
        self.customization = Customization()
        # TODO: Remove these (they are for debugging specific cards)
        # self.customization.required_card_classes.add(intrigue_cards.Diplomat)

    def setup(self):
        self.select_kingdom_cards()
        self.select_basic_cards()
        self.create_trash_pile()
        self.additional_setup()

    def select_kingdom_cards(self):
        selected_kingdom_card_classes = []
        # Get all possible kingdom cards from the selected expansions
        possible_kingdom_card_classes = []
        for expansion in self.customization.expansions:
            possible_kingdom_card_classes += expansion.kingdom_card_classes
        if self.customization.require_plus_two_action:
            # Require a card with +2 Actions
            plus_two_action_card_classes = [card_class for card_class in possible_kingdom_card_classes if hasattr(card_class, "extra_actions") and card_class.extra_actions >= 2]
            plus_two_action_card_class = random.choice(plus_two_action_card_classes)
            self.customization.required_card_classes.add(plus_two_action_card_class)
        if self.customization.require_drawer:
            # Require a card with +1 Card
            draw_card_classes = [card_class for card_class in possible_kingdom_card_classes if hasattr(card_class, "extra_cards") and card_class.extra_cards >= 1]
            draw_card_class = random.choice(draw_card_classes)
            self.customization.required_card_classes.add(draw_card_class)
        if self.customization.require_buy:
            # Require a card with +1 Buy
            buy_card_classes = [card_class for card_class in possible_kingdom_card_classes if hasattr(card_class, "extra_buys") and card_class.extra_buys >= 1]
            buy_card_class = random.choice(buy_card_classes)
            self.customization.required_card_classes.add(buy_card_class)
        if self.customization.require_trashing:
            # Require a card that allows trashing
            trash_card_classes = [card_class for card_class in possible_kingdom_card_classes if "trash" in card_class.description.lower()]
            trash_card_class = random.choice(trash_card_classes)
            self.customization.required_card_classes.add(trash_card_class)
        # Add in required cards
        for card_class in self.customization.required_card_classes:
            selected_kingdom_card_classes.append(card_class)
            possible_kingdom_card_classes.remove(card_class)
        if self.customization.disable_attack_cards:
            # Filter out attack cards
            possible_kingdom_card_classes = [card_class for card_class in copy.deepcopy(possible_kingdom_card_classes) if cards.CardType.ATTACK not in card_class.types]
        if self.customization.distribute_cost:
            # Make sure there are at least two kingdom cards each of cost {2, 3, 4, 5} (this leaves 2 cards of any cost)
            selected_kingdom_card_classes_by_cost = {cost: [card_class for card_class in selected_kingdom_card_classes if card_class.cost == cost] for cost in range(2, 6)}
            possible_kingdom_card_classes_by_cost = {cost: [card_class for card_class in possible_kingdom_card_classes if card_class.cost == cost] for cost in range(2, 6)}
            for cost in range(2, 6):
                num_still_needed = max(0, 2 - len(selected_kingdom_card_classes_by_cost[cost]))
                card_classes_of_cost = random.sample(possible_kingdom_card_classes_by_cost[cost], num_still_needed)
                for card_class in card_classes_of_cost:
                    selected_kingdom_card_classes.append(card_class)
                    possible_kingdom_card_classes.remove(card_class)
        # Select the remaining cards at random
        num_cards_remaining = 10 - len(selected_kingdom_card_classes)
        selected_kingdom_card_classes += random.sample(possible_kingdom_card_classes, num_cards_remaining)
        # Sort kingdom cards first by cost, then by name
        for card_class in sorted(selected_kingdom_card_classes, key=lambda card_class: (card_class.cost, card_class.name)):
            # Stacks of ten kingdom cards each
            self.card_stacks[card_class] = FiniteSupplyStack(card_class, 10)

    def select_basic_cards(self):
        # Get all possible basic cards from the selected expansions
        basic_card_piles = []
        for expansion in self.customization.expansions:
            basic_card_piles += expansion.basic_card_piles
        for card_class, pile_size in basic_card_piles:
            self.card_stacks[card_class] = FiniteSupplyStack(card_class, pile_size)

    def create_trash_pile(self):
        self.trash_pile = {card_class: [] for card_class in self.card_stacks}

    def additional_setup(self):
        # Perform all additional setup actions from the selected expansions
        for expansion in self.customization.expansions:
            expansion.additional_setup()

    def add_post_gain_hook(self, post_gain_hook, card_class):
        self.post_gain_hooks[card_class].append(post_gain_hook)

    def draw(self, card_class):
        return self.card_stacks[card_class].draw()

    def trash(self, card):
        card_class = type(card)
        self.trash_pile[card_class].append(card)

    def modify_cost(self, card_class, increment):
        self.card_stacks[card_class].modified_cost += increment
        # Don't ever let the cost go below zero
        if self.card_stacks[card_class].modified_cost < 0:
            self.card_stacks[card_class].modified_cost = 0

    def reset_costs(self):
        for card_class in self.card_stacks:
            self.card_stacks[card_class].modified_cost = self.card_stacks[card_class].base_cost

    def get_table(self):
        supply_table = prettytable.PrettyTable(hrules=prettytable.ALL)
        supply_table.field_names = ['Number', 'Card', 'Cost', 'Type', 'Quantity', 'Description']
        for idx, card_class in enumerate(sorted(self.card_stacks.keys(), key=lambda x: (x.types[0].value, x.cost))):
            quantity = self.card_stacks[card_class].cards_remaining
            types = ', '.join([type.name.lower().capitalize() for type in card_class.types])
            supply_table.add_row([idx + 1, card_class.name, self.card_stacks[card_class].modified_cost, types, quantity, card_class.description])
        return supply_table

    def __str__(self):
        supply_table = self.get_table()
        return supply_table.get_string()

    def card_name_to_card_class(self, card_name):
        '''Convert a card name to a card class. If you need to use this function, you're almost definitely doing something wrong.

        Args:
            card_name (str): the name of the card

        Returns:
            Card: the card class
        '''
        for card_class in self.card_stacks:
            if card_class.name == card_name:
                return card_class

    @property
    def num_empty_stacks(self):
        return [stack.is_empty for stack in self.card_stacks.values()].count(True)

    @property
    def trash_pile_json(self):
        json = []
        for card_class in self.trash_pile:
            quantity = len(self.trash_pile[card_class])
            try:
                card_json = self.trash_pile[card_class][0].json
                card_json["quantity"] = quantity
                json.append(card_json)
            except IndexError:
                pass
        return json


class SupplyStack(metaclass=ABCMeta):
    def __init__(self):
        self._example = self.card_class()

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

    @property
    def json(self):
        quantity = "inf" if self.cards_remaining == inf else self.cards_remaining
        card_stack_json = self.example.json
        card_stack_json["cost"] = self.modified_cost
        card_stack_json["quantity"] = quantity
        return card_stack_json

    @property
    def example(self):
        # An orphaned example card that data can be pulled from
        return self._example


class InfiniteSupplyStack(SupplyStack):
    def __init__(self, card_class):
        self.card_class = card_class
        self._cards_remaining = inf
        super().__init__()

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
        self.base_cost = card_class.cost
        self.modified_cost = card_class.cost
        self._cards_remaining = size
        super().__init__()

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