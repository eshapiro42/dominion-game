from typing import List

from .recommended_set import RecommendedSet
from ...expansions import Expansion, BaseExpansion, ProsperityExpansion, CornucopiaExpansion
from ...cards import prosperity_cards, cornucopia_cards


class Detours(RecommendedSet):
    name = "Detours"
    expansions = [
        ProsperityExpansion,
        CornucopiaExpansion,
    ]
    card_classes = [
        prosperity_cards.Rabble,
        prosperity_cards.Peddler,
        prosperity_cards.Hoard,
        prosperity_cards.TradeRoute,
        prosperity_cards.Venture,
        cornucopia_cards.FarmingVillage,
        cornucopia_cards.HornOfPlenty,
        cornucopia_cards.Jester,
        cornucopia_cards.Remake,
        cornucopia_cards.Tournament,
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
                CornucopiaExpansion(self.game),
            ]
        return self._expansion_instances


RECOMMENDED_SETS = [Detours]