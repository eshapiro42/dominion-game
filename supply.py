import cards
import itertools
import random
from abc import ABCMeta, abstractmethod
from math import inf


class SupplyStackEmptyError(Exception):
    '''Raised when a supply stack is empty
    
    Attributes:
        card_class: class of card whose supply stack is empty
    '''
    def __init__(self, card_class):
        message = f'{card_class.name} supply stack is empty'
        super().__init__(message)


class Supply:
    def __init__(self, num_players):
        self.card_stacks = {}
        # Limitless stacks of treasure cards
        self.treasure_card_classes = [cards.Copper, cards.Silver, cards.Gold]
        for card_class in self.treasure_card_classes:
            self.card_stacks[card_class] = InfiniteSupplyStack(card_class)
        # Victory card stack sizes depend on number of players
        if num_players == 2:
            stack_size = 8
        else:
            stack_size = 12
        self.victory_card_classes = [cards.Estate, cards.Duchy, cards.Province]
        for card_class in self.victory_card_classes:
            self.card_stacks[card_class] = FiniteSupplyStack(card_class, stack_size)
        # 10 randomly selected stacks of 10 kingdom cards each
        self.kingdom_card_classes = random.sample(cards.KINGDOM_CARDS, 10)
        for card_class in self.kingdom_card_classes:
            self.card_stacks[card_class] = FiniteSupplyStack(card_class, 10)

    def draw(self, card_class):
        return self.card_stacks[card_class].draw()

    def __repr__(self):
        repr_lines = []
        for card_class in self.card_stacks:
            repr_lines.append(f'{card_class}: {self.card_stacks[card_class].cards_remaining}')
        return '\n'.join(repr_lines)

    @property
    def num_empty_stacks(self):
        return len(stack.is_empty for stack in self.card_stacks.values())


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