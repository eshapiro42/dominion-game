from typing import TYPE_CHECKING, List

from .recommended_set import RecommendedSet
from ...expansions import BaseExpansion, ProsperityExpansion, GuildsExpansion
from ...cards import prosperity_cards, guilds_cards

if TYPE_CHECKING:
    from ...expansions.expansion import Expansion


class Quarrymen(RecommendedSet):
    name = "Quarrymen"
    expansions = [
        ProsperityExpansion,
        GuildsExpansion,
    ]
    card_classes = [
        prosperity_cards.Charlatan, # Not yet implemented (second edition of Prosperity)
        prosperity_cards.City,
        prosperity_cards.Expand,
        prosperity_cards.GrandMarket,
        prosperity_cards.Quarry,
        guilds_cards.Baker,
        guilds_cards.MerchantGuild,
        guilds_cards.Soothsayer,
        guilds_cards.Stonemason,
        guilds_cards.Taxman,
    ]
    additional_cards = [
        (prosperity_cards.Platinum, None),
        (prosperity_cards.Colony, None),
    ]

    @property
    def expansion_instances(self) -> List[Expansion] | None:
        # Add the Platinum and Colony
        if self._expansion_instances is None:
            self._expansion_instances = [
                BaseExpansion(self.game),
                ProsperityExpansion(self.game, platinum_and_colony=True),
                GuildsExpansion(self.game),
            ]
        return self._expansion_instances


RECOMMENDED_SETS = [Quarrymen]