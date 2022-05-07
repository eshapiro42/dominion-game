from __future__ import annotations

import copy
import prettytable
import random
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from math import inf
from typing import TYPE_CHECKING, Dict, List, Type

from .cards import cards, base_cards, prosperity_cards, intrigue_cards, cornucopia_cards

if TYPE_CHECKING:
    from .cards.cards import Card
    from .expansions.expansion import Expansion
    from .hooks import PostGainHook


class SupplyStackEmptyError(Exception):
    '''
    Raised when a supply stack is empty.
    
    Args:
        card_class: The class of the card whose supply stack is empty.
    '''
    def __init__(self, card_class: Type[Card]):
        message = f'{card_class.name} supply stack is empty'
        super().__init__(message)


class Customization:
    '''
    Customization options for the Supply.
    '''
    def __init__(self):
        self._expansions = set([])
        self._required_card_classes = set([]) # If nonempty, ensures that each card in the list ends up in the supply
        self._distribute_cost = False # If toggled, ensures there are at least two cards each of cost {2, 3, 4, 5}
        self._disable_attack_cards = False # If toggled, Attack cards are not allowed
        self._require_plus_two_action = False # If toggled, ensures there is at least one card with '>= +2 Actions'
        self._require_drawer = False # If toggled, ensures there is at least one card with '>= +1 Cards'
        self._require_buy = False # If toggled, ensures there is at least one card with '>= +1 Buys'
        self._require_trashing = True # If toggled, ensures there is at least one card that allows trashing

    @property
    def expansions(self) -> set[Expansion]:
        """
        A set of expansion classes to be chosen from in the supply.
        """
        return self._expansions

    @expansions.setter
    def expansions(self, expansions: set[Expansion]):
        self._expansions = expansions

    @property
    def required_card_classes(self) -> set[Type[Card]]:
        """
        A set of card classes to require in the supply.

        If this set is too large and enough other customization
        options are enabled, the supply may not be able to be
        generated (since it only has ten kingdom cards to choose).
        """
        return self._required_card_classes

    @required_card_classes.setter
    def required_card_classes(self, required_card_classes: set[Type[Card]]):
        self._required_card_classes = required_card_classes

    @property
    def distribute_cost(self) -> bool:
        """
        If :obj:`True`, ensures that there are at least two cards each of cost 2, 3, 4 and 5 in the supply.
        """
        return self._distribute_cost

    @distribute_cost.setter
    def distribute_cost(self, distribute_cost: bool):
        self._distribute_cost = distribute_cost

    @property
    def disable_attack_cards(self) -> bool:
        """
        If :obj:`True`, Attack cards are not allowed in the supply.
        """
        return self._disable_attack_cards

    @disable_attack_cards.setter
    def disable_attack_cards(self, disable_attack_cards: bool):
        self._disable_attack_cards = disable_attack_cards

    @property
    def require_plus_two_action(self) -> bool:
        """
        If :obj:`True`, ensures there is at least one card with '>= +2 Actions' in the supply.
        """
        return self._require_plus_two_action

    @require_plus_two_action.setter
    def require_plus_two_action(self, require_plus_two_action: bool):
        self._require_plus_two_action = require_plus_two_action

    @property
    def require_drawer(self) -> bool:
        """
        If :obj:`True`, ensures there is at least one card with '>= +1 Cards' in the supply.
        """
        return self._require_drawer

    @require_drawer.setter
    def require_drawer(self, require_drawer: bool):
        self._require_drawer = require_drawer

    @property
    def require_buy(self) -> bool:
        """
        If :obj:`True`, ensures there is at least one card with '>= +1 Buys' in the supply.
        """
        return self._require_buy

    @require_buy.setter
    def require_buy(self, require_buy: bool):
        self._require_buy = require_buy

    @property
    def require_trashing(self) -> bool:
        """
        If :obj:`True`, ensures there is at least one card that allows trashing in the supply.
        """
        return self._require_trashing

    @require_trashing.setter
    def require_trashing(self, require_trashing: bool):
        self._require_trashing = require_trashing

    @property
    def required_effects(self) -> Dict[str, bool]:
        """
        A dictionary whose keys are strings describing potentially required card
        effects and whose values are booleans indicating whether or not that effect
        is required.
        """
        return {
            "plus_two_action": self.require_plus_two_action,
            "drawer": self.require_drawer,
            "buy": self.require_buy,
            "trashing": self.require_trashing,
        }

    @staticmethod
    def card_has_effect(card_class: Type[Card], effect_string: str) -> bool:
        """
        TODO: This really belongs in the :obj:`Card` class itself as either multiple properties or a regular method that accepts an effect.
        Additionally, it would be better to have an enumeration of all the effects that can be checked for, rather than using strings.

        Return whether a given card class has a specific effect. Useful for dealing with customization options that require specific effects.

        For instance, :obj:`Customization.card_has_effect(base_cards.Festival, "buy")` would return :obj:`True`.

        Arguments:
            card_class: The card class to check.
            effect_string: The name of the effect to check for.

        Returns:
            Whether the card class has the effect.
        """
        return {
            "plus_two_action": hasattr(card_class, "extra_actions") and card_class.extra_actions >= 2,
            "drawer": hasattr(card_class, "extra_cards") and card_class.extra_cards >= 1,
            "buy": hasattr(card_class, "extra_buys") and card_class.extra_buys >= 1,
            "trashing": "trash" in card_class.description.lower(),
        }[effect_string]


class Supply:
    """
    The supply of cards in a game.

    Args:
        num_players: The number of players in the game.
    """
    def __init__(self, num_players):
        self._num_players = num_players
        self._card_stacks = {}
        self._post_gain_hooks = defaultdict(list)
        self._customization = Customization()
        # TODO: Remove these (they are for debugging specific cards)
        # self.customization.required_card_classes.add(cornucopia_cards.Tournament)

    @property
    def num_players(self) -> int:
        """
        The number of players in the game.
        """
        return self._num_players

    @property
    def card_stacks(self) -> Dict[Type[Card], SupplyStack]:
        """
        A dictionary whose keys are card classes and whose values are
        :obj:`SupplyStack` objects.

        These objects are used to create and track the number of cards
        of a given class in the supply.
        """
        return self._card_stacks

    @card_stacks.setter
    def card_stacks(self, card_stacks: Dict[Type[Card], SupplyStack]):
        self._card_stacks = card_stacks

    @property
    def post_gain_hooks(self) -> Dict[Type[Card], List[PostGainHook]]:
        """
        A dictionary whose keys are card classes and whose values are
        lists of post-gain hooks.

        These hooks are called after a card of the specified class is
        gained from the supply.
        """
        return self._post_gain_hooks

    @post_gain_hooks.setter
    def post_gain_hooks(self, post_gain_hooks: Dict[Type[Card], List[PostGainHook]]):
        self._post_gain_hooks = post_gain_hooks

    @property
    def customization(self) -> Customization:
        """
        The customization options for the supply.

        This object is used to determine which cards are allowed/required
        in the supply and which effects are required.
        """
        return self._customization

    def setup(self):
        """
        Create the supply stacks and add cards to them, and perform any
        additional setup needed by expansions.

        Called after the game is started (but before the game loop begins).
        Supply customization options must be specified before calling this
        method.
        """
        self._select_kingdom_cards()
        self._select_basic_cards()
        self._create_trash_pile()
        self._additional_setup()

    def _select_kingdom_cards(self):
        """
        Choose kingdom cards from the selected expansions and add them into
        the Supply. Also ensure that any other customization options are
        honored.        
        """
        selected_kingdom_card_classes = []
        # Get all possible kingdom cards from the selected expansions
        possible_kingdom_card_classes = []
        for expansion in self.customization.expansions:
            possible_kingdom_card_classes += expansion.kingdom_card_classes
        # Add in any required cards. Note that this will break things is a required card's expansion is not selected.
        for required_card_class in self.customization.required_card_classes:
            if required_card_class not in possible_kingdom_card_classes:
                raise ValueError(f"Required card class {required_card_class.name} is not in the selected expansions.")
            print(f"Adding required card class {required_card_class.name}.")
            selected_kingdom_card_classes.append(required_card_class)
            possible_kingdom_card_classes.remove(required_card_class)
        # All filtering and disabling should be done prior to fulfilling requirements!
        if self.customization.disable_attack_cards:
            # Filter out attack cards
            print("Disabling attack cards.")
            possible_kingdom_card_classes = [card_class for card_class in copy.deepcopy(possible_kingdom_card_classes) if cards.CardType.ATTACK not in card_class.types]
        # Find and add in kingdom cards satisfying the required effects
        required_effects = [effect for effect, required in self.customization.required_effects.items() if required]
        random.shuffle(required_effects) # Shuffle the list of required effects so some cards don't get preferential treatment every game
        for required_effect in required_effects:
            # First check if the required effect already happens to be satisfied by a previously required card
            if any(self.customization.card_has_effect(card_class, required_effect) for card_class in selected_kingdom_card_classes):
                print(f"{required_effect} is already satisfied by a previously selected card.")
                continue
            # Otherwise, find a card that has the required effect
            possible_kingdom_card_classes_with_required_effect = [card_class for card_class in possible_kingdom_card_classes if self.customization.card_has_effect(card_class, required_effect)]
            card_class_with_required_effect = random.choice(possible_kingdom_card_classes_with_required_effect)
            print(f"Adding {card_class_with_required_effect.name} to satisfy {required_effect}.")
            # Add the card to the list of selected kingdom cards
            selected_kingdom_card_classes.append(card_class_with_required_effect)
            # Remove the card from the list of possible remaining kingdom cards
            possible_kingdom_card_classes.remove(card_class_with_required_effect)
        if self.customization.distribute_cost:
            # Make sure there are at least two kingdom cards each of cost {2, 3, 4, 5} (this leaves 2 cards of any cost if no other customizations are chosen)
            print("Distributing costs")
            selected_kingdom_card_classes_by_cost = {cost: [card_class for card_class in selected_kingdom_card_classes if card_class.cost == cost] for cost in range(2, 6)}
            possible_kingdom_card_classes_by_cost = {cost: [card_class for card_class in possible_kingdom_card_classes if card_class.cost == cost] for cost in range(2, 6)}
            for cost in range(2, 6):
                num_still_needed = max(0, 2 - len(selected_kingdom_card_classes_by_cost[cost]))
                card_classes_of_cost = random.sample(possible_kingdom_card_classes_by_cost[cost], num_still_needed)
                print(f"Adding {num_still_needed} cards of cost {cost}: {' and '.join(card_class.name for card_class in card_classes_of_cost)}")
                for card_class in card_classes_of_cost:
                    selected_kingdom_card_classes.append(card_class)
                    possible_kingdom_card_classes.remove(card_class)
        # Select the remaining cards at random
        num_cards_remaining = max(0, 10 - len(selected_kingdom_card_classes))
        selected_kingdom_card_classes += random.sample(possible_kingdom_card_classes, num_cards_remaining)
        # Sort kingdom cards first by cost, then by name
        for card_class in sorted(selected_kingdom_card_classes, key=lambda card_class: (card_class.cost, card_class.name)):
            # Stacks of ten kingdom cards each
            self.card_stacks[card_class] = FiniteSupplyStack(card_class, 10)

    def _select_basic_cards(self):
        """
        Add basic cards from the selected expansions into the supply.
        """
        basic_card_piles = []
        for expansion in self.customization.expansions:
            basic_card_piles += expansion.basic_card_piles
        for card_class, pile_size in basic_card_piles:
            self.card_stacks[card_class] = FiniteSupplyStack(card_class, pile_size)

    def _create_trash_pile(self):
        """
        Create an empty trash pile.
        """
        self.trash_pile = defaultdict(list)

    def _additional_setup(self):
        """
        Perform all additional setup actions from the selected expansions.
        """
        for expansion in self.customization.expansions:
            expansion.additional_setup()

    def add_post_gain_hook(self, post_gain_hook: PostGainHook, card_class: Type[Card]):
        """
        Add a post-gain hook to the specified card class.

        Args:
            post_gain_hook: The post-gain hook to add.
            card_class: The card class to add the hook to.
        """
        self.post_gain_hooks[card_class].append(post_gain_hook)

    def draw(self, card_class: Type[Card]):
        """
        Draw a card of the specified card class from the supply.
        In the case of a :obj:`FiniteSupplyStack`, the quantity
        of cards in the stack will be automatically decremented.

        Args:
            card_class: The card class to draw.
        """
        return self.card_stacks[card_class].draw()

    def trash(self, card: Card):
        """
        Add a card to the trash pile.

        The card must be explicitly removed from its deque before
        being trashed or else a duplicate will be created.

        Args:
            card: The card to add to the trash pile.
        """
        card_class = type(card)
        self.trash_pile[card_class].append(card)

    def modify_cost(self, card_class: Type[Card], increment: int):
        """
        Temporarily modify a card's cost. (A card's cost cannot ever
        be less than 0.)

        Once the cost modification is no longer relevant, this needs
        to be undone by calling :meth:`reset_costs`.

        Args:
            card_class: The card class whose cost to modify.
            increment: The amount to add to the card's cost.
        """
        self.card_stacks[card_class].modified_cost += increment
        # Don't ever let the cost go below zero
        if self.card_stacks[card_class].modified_cost < 0:
            self.card_stacks[card_class].modified_cost = 0

    def reset_costs(self):
        """
        Reset the costs of all cards in the supply to their default.
        """
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

    def card_name_to_card_class(self, card_name: str) -> Type[Card]:
        '''Convert a card name to a card class. If you need to use this function, you're almost definitely doing something wrong.

        Args:
            card_name: the name of the card

        Returns:
            The card class
        '''
        for card_class in self.card_stacks:
            if card_class.name == card_name:
                return card_class

    @property
    def num_empty_stacks(self):
        """
        The number of empty supply piles in the supply.
        """
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
    """
    Base class for a pile of cards of a single class in the supply.

    Args:
        card_class: The card class of the cards in the stack.
    """
    def __init__(self, card_class: Type[Card]):
        self._card_class = card_class
        self._example = self.card_class()

    @property
    def card_class(self):
        """
        The class of card in this stack.
        """
        return self._card_class

    @property
    def example(self):
        """
        An orphaned example card that data can be pulled from.
        This card is not in the supply.
        """
        return self._example

    @abstractmethod
    def draw(self) -> Card:
        """
        Draw a card from the stack.
        """
        pass

    @property
    @abstractmethod
    def cards_remaining(self) -> int:
        """
        The quantity of cards remaining in the stack.
        """
        pass

    @property
    @abstractmethod
    def is_empty(self) -> bool:
        """
        Whether the stack is empty.
        """
        pass

    @property
    def json(self):
        quantity = "inf" if self.cards_remaining == inf else self.cards_remaining
        card_stack_json = self.example.json
        card_stack_json["cost"] = self.modified_cost
        card_stack_json["quantity"] = quantity
        return card_stack_json


class InfiniteSupplyStack(SupplyStack):
    """
    A supply stack containing infinite copies of a card.

    Useful for basic treasure cards and other cards that
    have unlimited quantities.

    Args:
        card_class: The card class of the cards in the stack.
    """
    def __init__(self, card_class: Type[Card]):
        super().__init__(card_class)
        self._cards_remaining = inf

    def draw(self) -> Card:
        card = self.card_class()
        return card

    @property
    def cards_remaining(self) -> int:
        return self._cards_remaining

    @property
    def is_empty(self) -> bool:
        return False


class FiniteSupplyStack(SupplyStack):
    """
    A supply stack containing a finite number of copies of a card.
    
    Args:
        card_class: The card class of the cards in the stack.
        size: The number of cards in the stack.
    """
    def __init__(self, card_class: Type[Card], size: int):
        super().__init__(card_class)
        self._base_cost = card_class.cost
        self._modified_cost = card_class.cost
        self._cards_remaining = size

    @property
    def base_cost(self) -> int:
        """
        The base cost of the card.
        """
        return self._base_cost

    @property
    def modified_cost(self) -> int:
        """
        The cost of the card, including any modifications.
        """
        return self._modified_cost

    @modified_cost.setter
    def modified_cost(self, value: int):
        self._modified_cost = value

    def draw(self) -> Card:
        """
        Draw a card from the stack and decrement its number of cards
        remaining by one.

        Raises a :obj:`SupplyStackEmptyError` if there are no cards
        remaining.
        """
        if not self.is_empty:
            card = self.card_class()
            self._cards_remaining -= 1
            return card
        else:
            raise SupplyStackEmptyError(self.card_class)

    @property
    def cards_remaining(self) -> int:
        return self._cards_remaining

    @property
    def is_empty(self) -> bool:
        """
        Whether the stack is empty.
        """
        return self._cards_remaining == 0

    def __repr__(self):
        return self.card_class.name