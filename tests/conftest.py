from __future__ import annotations

import pytest
import random

from typing import Any, Dict, List, Type, TYPE_CHECKING

from dominion.cards import cards, base_cards, dominion_cards, intrigue_cards, prosperity_cards, cornucopia_cards, hinterlands_cards, guilds_cards
from dominion.expansions import BaseExpansion, DominionExpansion, IntrigueExpansion, ProsperityExpansion, CornucopiaExpansion, HinterlandsExpansion, GuildsExpansion
from dominion.expansions.expansion import Expansion
from dominion.game import Game


# Type Aliases
GameParams = Dict[str, List[Type[Expansion]] | List[str] | int]


@pytest.fixture
def all_expansions() -> List[Type[Expansion]]:
    return [
        # BaseExpansion,
        DominionExpansion,
        IntrigueExpansion,
        ProsperityExpansion,
        CornucopiaExpansion,
        HinterlandsExpansion,
        GuildsExpansion,
    ]


@pytest.fixture
def all_card_sets() -> List[Any]:
    return [
        base_cards,
        dominion_cards,
        intrigue_cards,
        prosperity_cards,
        cornucopia_cards,
        hinterlands_cards,
        guilds_cards,
    ]


@pytest.fixture
def all_options() -> List[str]:
    return [
        "allow_simultaneous_reactions",
        # "distribute_cost",
        "disable_attack_cards",
        "require_plus_two_action",
        "require_drawer",
        "require_buy",
        "require_trashing",
    ]


@pytest.fixture
def random_expansions(all_expansions: List[Type[Expansion]]) -> List[Type[Expansion]]:
    num_expansions = random.randint(1, len(all_expansions))
    return random.sample(all_expansions, num_expansions)


@pytest.fixture
def random_options(all_options: List[str]) -> List[str]:
    num_options = random.randint(0, len(all_options))
    return random.sample(all_options, num_options)


@pytest.fixture
def random_num_players() -> int:
    return random.randint(2, 4)


@pytest.fixture
def random_game_params(random_expansions: List[Type[Expansion]], random_options: List[str], random_num_players: int) -> GameParams:
    return {
        "expansions": random_expansions,
        "options": random_options,
        "num_players": random_num_players,
    }


@pytest.fixture
def random_game(random_game_params: GameParams) -> Game:
    game = Game(test=True)
    for expansion in random_game_params["expansions"]:
        game.add_expansion(expansion)
    for option in random_game_params["options"]:
        setattr(game, option, True)
    for _ in range(random_game_params["num_players"]):
        game.add_player()
    return game


@pytest.fixture
def game(request) -> Game:
    game = Game(test=True)
    expansions = request.param["expansions"]
    options = request.param["options"]
    num_players = request.param["num_players"]
    for expansion in expansions:
        game.add_expansion(expansion)
    for option in options:
        setattr(game, option, True)
    for _ in range(num_players):
        game.add_player()
    return game
