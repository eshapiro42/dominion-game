import pytest

from dominion.game import Game
from dominion.interactions import BrowserInteraction
from tests.conftest import GameParams

@pytest.fixture
def random_browser_game(random_game_params: GameParams) -> Game:
    game = Game(test=True)
    for expansion in random_game_params["expansions"]:
        game.add_expansion(expansion)
    for option in random_game_params["options"]:
        setattr(game, option, True)
    for _ in range(random_game_params["num_players"]):
        game.add_player(interactions_class=BrowserInteraction)
    return game