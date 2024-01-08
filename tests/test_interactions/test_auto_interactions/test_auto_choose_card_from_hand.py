import pytest
from copy import copy

from dominion.game import Game
from dominion.player import Player


# Function signature:
#   choose_card_from_hand(self, prompt, force, invalid_cards=None) -> Optional[Card]


@pytest.fixture
def player(random_game: Game):
    random_game.start(debug=True)
    player = random_game.players[0]
    return player

@pytest.mark.repeat(100)
def test_standard(player: Player):
    """
    With force=False, the returned card should either be None or in the player's hand
    """
    chosen_card = player.interactions.choose_card_from_hand(prompt="", force=False)
    assert chosen_card is None or chosen_card in player.hand

@pytest.mark.repeat(100)
def test_force(player: Player):
    """
    With force=True and 5 cards in hand, the returned card should never be None and should be in the player's hand
    """
    chosen_card = player.interactions.choose_card_from_hand(prompt="", force=True)
    assert chosen_card in player.hand

def test_force_with_empty_hand(player: Player):
    """
    With force=True and 0 cards in hand, the returned card is allowed to be (and must be) None
    """
    for card in copy(player.hand): # Need to make a copy or else player.hand will mutate while iterating
        player.discard_from_hand(card)
    chosen_card = player.interactions.choose_card_from_hand(prompt="", force=True)
    assert chosen_card is None

@pytest.mark.repeat(100)
def test_invalid_cards(player: Player):
    """
    With one invalid card and 5 cards in hand, the returned card should never be invalid and should be in the player's hand
    """
    invalid_cards = [player.hand[0]]
    chosen_card = player.interactions.choose_card_from_hand(prompt="", force=True, invalid_cards=invalid_cards)
    assert chosen_card not in invalid_cards and chosen_card in player.hand

def test_only_invalid_cards(player: Player):
    """
    With only invalid cards in hand, the returned card must be None
    """
    invalid_cards = player.hand
    chosen_card = player.interactions.choose_card_from_hand(prompt="", force=True, invalid_cards=invalid_cards)
    assert chosen_card is None