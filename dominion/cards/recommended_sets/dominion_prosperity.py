from typing import List

from .recommended_set import RecommendedSet
from ...expansions import Expansion, BaseExpansion, DominionExpansion, ProsperityExpansion
from ...cards import dominion_cards, prosperity_cards


class BiggestMoney(RecommendedSet):
    name = "Biggest Money"
    expansions = [
        DominionExpansion,
        ProsperityExpansion,
    ]
    card_classes = [
        dominion_cards.Artisan,
        dominion_cards.Harbinger,
        dominion_cards.Laboratory,
        dominion_cards.Mine,
        dominion_cards.Moneylender,
        prosperity_cards.Bank,
        prosperity_cards.GrandMarket,
        prosperity_cards.Mint,
        prosperity_cards.RoyalSeal,
        prosperity_cards.Venture,
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
                DominionExpansion(self.game),
                ProsperityExpansion(self.game, platinum_and_colony=True),
            ]
        return self._expansion_instances


class TheKingsArmy(RecommendedSet):
    name = "The King's Army"
    expansions = [
        DominionExpansion,
        ProsperityExpansion,
    ]
    card_classes = [
        dominion_cards.Bureaucrat,
        dominion_cards.CouncilRoom,
        dominion_cards.Merchant,
        dominion_cards.Moat,
        dominion_cards.Village,
        prosperity_cards.Expand,
        prosperity_cards.Goons,
        prosperity_cards.KingsCourt,
        prosperity_cards.Rabble,
        prosperity_cards.Vault,
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
                DominionExpansion(self.game),
                ProsperityExpansion(self.game, platinum_and_colony=True),
            ]
        return self._expansion_instances


class TheGoodLife(RecommendedSet):
    name = "The Good Life"
    expansions = [
        DominionExpansion,
        ProsperityExpansion,
    ]
    card_classes = [
        dominion_cards.Artisan,
        dominion_cards.Bureaucrat,
        dominion_cards.Cellar,
        dominion_cards.Gardens,
        dominion_cards.Village,
        prosperity_cards.Contraband,
        prosperity_cards.CountingHouse,
        prosperity_cards.Hoard,
        prosperity_cards.Monument,
        prosperity_cards.Mountebank,
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
                DominionExpansion(self.game),
                ProsperityExpansion(self.game, platinum_and_colony=True),
            ]
        return self._expansion_instances


RECOMMENDED_SETS = [
    BiggestMoney,
    TheKingsArmy,
    TheGoodLife,
]