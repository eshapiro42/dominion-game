from __future__ import annotations

from typing import TYPE_CHECKING, List

from .recommended_set import RecommendedSet
from ...expansions import BaseExpansion, ProsperityExpansion
from ...cards import prosperity_cards

if TYPE_CHECKING:
    from ...expansions.expansion import Expansion


class Beginners(RecommendedSet):
    name = "Beginners"
    expansions = [ProsperityExpansion]
    card_classes = [
        prosperity_cards.Bank,
        prosperity_cards.CountingHouse,
        prosperity_cards.Expand,
        prosperity_cards.Goons,
        prosperity_cards.Monument,
        prosperity_cards.Rabble,
        prosperity_cards.RoyalSeal,
        prosperity_cards.Venture,
        prosperity_cards.Watchtower,
        prosperity_cards.WorkersVillage,
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
            ]
        return self._expansion_instances


class FriendlyInteractive(RecommendedSet):
    name = "Friendly Interactive"
    expansions = [ProsperityExpansion]
    card_classes = [
        prosperity_cards.Bishop,
        prosperity_cards.City,
        prosperity_cards.Contraband,
        prosperity_cards.Forge,
        prosperity_cards.Hoard,
        prosperity_cards.Peddler,
        prosperity_cards.RoyalSeal,
        prosperity_cards.TradeRoute,
        prosperity_cards.Vault,
        prosperity_cards.WorkersVillage,
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
            ]
        return self._expansion_instances


class BigActions(RecommendedSet):
    name = "Big Actions"
    expansions = [ProsperityExpansion]
    card_classes = [
        prosperity_cards.City,
        prosperity_cards.Expand,
        prosperity_cards.GrandMarket,
        prosperity_cards.KingsCourt,
        prosperity_cards.Loan,
        prosperity_cards.Mint,
        prosperity_cards.Quarry,
        prosperity_cards.Rabble,
        prosperity_cards.Talisman,
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
                ProsperityExpansion(self.game, platinum_and_colony=True),
            ]
        return self._expansion_instances


RECOMMENDED_SETS = [
    Beginners,
    FriendlyInteractive,
    BigActions,
]