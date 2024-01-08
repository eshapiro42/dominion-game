import pytest

from typing import List, Type

from dominion.cards.cards import Card
from dominion.expansions.expansion import Expansion
from dominion.game import Game


def test_instantiate_cards(all_card_sets: List[Type[Card]]):
    '''
    Test instantiation of all card classes.
    '''
    # Compile all cards across all expansions
    card_classes = []
    for card_set in all_card_sets:
        if hasattr(card_set, 'BASIC_CARDS'):
            card_classes += card_set.BASIC_CARDS
        if hasattr(card_set, 'KINGDOM_CARDS'):
            card_classes += card_set.KINGDOM_CARDS
    # Try to instantiate every card class
    for card_class in card_classes:
        card = card_class()


def test_instantiate_expansions(all_expansions: List[Expansion], random_game: Game):
    '''
    Test instantiation of all expansion classes.
    '''
    for expansion_class in all_expansions:
        expansion_instance = expansion_class(random_game)


@pytest.mark.repeat(1000)
def test_stability(random_game: Game):
    '''
    Test completely CPU-driven games.

    Expansions, supply customizations and number of CPU players are randomly selected for each game.
    '''
    random_game.start()
