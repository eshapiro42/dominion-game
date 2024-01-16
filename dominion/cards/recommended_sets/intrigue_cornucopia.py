from __future__ import annotations

from typing import TYPE_CHECKING, List

from .recommended_set import RecommendedSet
from ...expansions import BaseExpansion, IntrigueExpansion, CornucopiaExpansion
from ...cards import intrigue_cards, cornucopia_cards

if TYPE_CHECKING:
    from ...expansions.expansion import Expansion


class LastLaughs(RecommendedSet):
    name = "Last Laughs"
    expansions = [
        IntrigueExpansion,
        CornucopiaExpansion,
    ]
    card_classes = [
        cornucopia_cards.FarmingVillage,
        cornucopia_cards.Harvest,
        cornucopia_cards.HorseTraders,
        cornucopia_cards.HuntingParty,
        cornucopia_cards.Jester,
        intrigue_cards.Minion,
        intrigue_cards.Nobles,
        intrigue_cards.Pawn,
        intrigue_cards.Steward,
        intrigue_cards.Swindler,
    ]


class TheSpiceOfLife(RecommendedSet):
    name = "The Spice of Life"
    expansions = [
        IntrigueExpansion,
        CornucopiaExpansion,
    ]
    card_classes = [
        cornucopia_cards.Fairgrounds,
        cornucopia_cards.HornOfPlenty,
        cornucopia_cards.Remake,
        cornucopia_cards.Tournament,
        cornucopia_cards.YoungWitch,
        intrigue_cards.Courtier,
        intrigue_cards.Courtyard,
        intrigue_cards.Diplomat,
        intrigue_cards.MiningVillage,
        intrigue_cards.Replace,
    ]
    additional_cards = [(intrigue_cards.WishingWell, "Bane")] + [(card_class, None) for card_class in cornucopia_cards.PRIZES]

    @property
    def expansion_instances(self) -> List[Expansion] | None:
        # Add the Wishing Well as the Bane card
        if self._expansion_instances is None:
            self._expansion_instances = [
                BaseExpansion(self.game),
                IntrigueExpansion(self.game),
                CornucopiaExpansion(self.game, bane_card_class=intrigue_cards.WishingWell),
            ]
        return self._expansion_instances


class SmallVictories(RecommendedSet):
    name = "Small Victories"
    expansions = [
        IntrigueExpansion,
        CornucopiaExpansion,
    ]
    card_classes = [
        cornucopia_cards.FortuneTeller,
        cornucopia_cards.Hamlet,
        cornucopia_cards.HuntingParty,
        cornucopia_cards.Remake,
        cornucopia_cards.Tournament,
        intrigue_cards.Conspirator,
        intrigue_cards.Duke,
        intrigue_cards.Harem,
        intrigue_cards.Pawn,
        intrigue_cards.SecretPassage,
    ]
    additional_cards = [(card_class, None) for card_class in cornucopia_cards.PRIZES]


RECOMMENDED_SETS = [
    LastLaughs,
    TheSpiceOfLife,
    SmallVictories,
]