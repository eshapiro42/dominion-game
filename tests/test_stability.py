import pytest
import random
from dominion.cards import base_cards, intrigue_cards, prosperity_cards
from dominion.expansions import IntrigueExpansion, ProsperityExpansion
from dominion.game import Game
from dominion.interactions import AutoInteraction


EXPANSIONS = [
    IntrigueExpansion,
    ProsperityExpansion,
]


CARD_SETS = [
    intrigue_cards,
    prosperity_cards,
]


def test_instantiate_cards():
    '''
    Test instantiation of all card classes.
    '''
    # Compile all cards across all expansions
    card_classes = []
    for card_set in CARD_SETS:
        if hasattr(card_set, 'BASIC_CARDS'):
            card_classes += card_set.BASIC_CARDS
        if hasattr(card_set, 'KINGDOM_CARDS'):
            card_classes += card_set.KINGDOM_CARDS
    # Try to instantiate every card class
    for card_class in card_classes:
        card = card_class()


@pytest.mark.repeat(1000)
def test_stability():
    '''
    Test completely CPU-driven games.

    Expansions, supply customizations and number of CPU players are randomly selected for each game.
    '''
    game = Game(test=True)
    # Add a randomly selected set of expansions into the game
    num_expansions = random.randint(1, len(EXPANSIONS))
    expansions_to_include = random.sample(EXPANSIONS, num_expansions)
    for expansion in expansions_to_include:
        game.add_expansion(expansion)
    # Add a randomly selected set of Supply customization options into the game
    options = [
        "allow_simultaneous_reactions",
        # "distribute_cost",
        "disable_attack_cards",
        "require_plus_two_action",
        "require_drawer",
        "require_buy",
        "require_trashing",
    ]
    num_options = random.randint(0, len(options))
    options_to_include = random.sample(options, num_options)
    for option in options_to_include:
        setattr(game, option, True)
    # Add a random number (2-4) players into the game
    num_players = random.randint(2, 4)
    for _ in range(num_players):
        game.add_player(interactions_class=AutoInteraction)
    game.start()