import pytest

from unittest.mock import patch

from dominion.expansions import DominionExpansion
from dominion.interactions.interaction import Interaction
from dominion.game import Game


@pytest.mark.parametrize(
    "game",
    [
        {
            "expansions": [DominionExpansion],
            "options": [],
            "num_players": 2,
        },
    ],
    indirect=True,
)
def test_fixtures(game: Game):
    print(game.expansions, game.num_players)


def test_mock():
    with patch.object(Interaction, "choose_card_class_from_supply", return_value="meow") as mock_method:
        print(mock_method)
        # mock_interaction: Interaction = MockInteraction.return_value
        # mock_interaction.choose_card_class_from_supply.return_value = "meow"
        #     interaction = Interaction(None)
        #     x = interaction.choose_card_class_from_supply(),
        #     assert x == "meow"