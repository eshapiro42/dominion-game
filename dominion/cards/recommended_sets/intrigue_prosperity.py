from typing import List

from .recommended_set import RecommendedSet
from ...expansions import Expansion, BaseExpansion, IntrigueExpansion, ProsperityExpansion
from ...cards import intrigue_cards, prosperity_cards


class PathsToVictory(RecommendedSet):
    name = "Paths to Victory"
    expansions = [
        IntrigueExpansion,
        ProsperityExpansion,
    ]
    card_classes = [
        prosperity_cards.Bishop,
        prosperity_cards.CountingHouse,
        prosperity_cards.Goons,
        prosperity_cards.Monument,
        prosperity_cards.Peddler,
        intrigue_cards.Baron,
        intrigue_cards.Harem,
        intrigue_cards.Pawn,
        intrigue_cards.ShantyTown,
        intrigue_cards.Upgrade,
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
                IntrigueExpansion(self.game),
                ProsperityExpansion(self.game, platinum_and_colony=True),
            ]
        return self._expansion_instances


class AllAlongTheWatchtower(RecommendedSet):
    name = "All Along the Watchtower"
    expansions = [
        IntrigueExpansion,
        ProsperityExpansion,
    ]
    card_classes = [
        prosperity_cards.Hoard,
        prosperity_cards.Talisman,
        prosperity_cards.TradeRoute,
        prosperity_cards.Vault,
        prosperity_cards.Watchtower,
        intrigue_cards.Bridge,
        intrigue_cards.Mill,
        intrigue_cards.MiningVillage,
        intrigue_cards.Pawn,
        intrigue_cards.Torturer,
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
                IntrigueExpansion(self.game),
                ProsperityExpansion(self.game, platinum_and_colony=True),
            ]
        return self._expansion_instances


class LuckySeven(RecommendedSet):
    name = "Lucky Seven"
    expansions = [
        IntrigueExpansion,
        ProsperityExpansion,
    ]
    card_classes = [
        prosperity_cards.Bank,
        prosperity_cards.Expand,
        prosperity_cards.Forge,
        prosperity_cards.KingsCourt,
        prosperity_cards.Vault,
        intrigue_cards.Bridge,
        intrigue_cards.Lurker,
        intrigue_cards.Patrol,
        intrigue_cards.Swindler,
        intrigue_cards.WishingWell,
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
                IntrigueExpansion(self.game),
                ProsperityExpansion(self.game, platinum_and_colony=True),
            ]
        return self._expansion_instances


RECOMMENDED_SETS = [
    PathsToVictory,
    AllAlongTheWatchtower,
    LuckySeven,
]