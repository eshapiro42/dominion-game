from __future__ import annotations

from typing import TYPE_CHECKING, List

from .recommended_set import RecommendedSet
from ...expansions import BaseExpansion, DominionExpansion, CornucopiaExpansion
from ...cards import dominion_cards, cornucopia_cards

if TYPE_CHECKING:
    from ...expansions.expansion import Expansion

class BountyOfTheHunt(RecommendedSet):
    name = "Bounty of the Hunt"
    expansions = [
        DominionExpansion,
        CornucopiaExpansion,
    ]
    card_classes = [
        dominion_cards.Cellar,
        dominion_cards.Festival,
        dominion_cards.Militia,
        dominion_cards.Moneylender,
        dominion_cards.Smithy,
        cornucopia_cards.Harvest,
        cornucopia_cards.HornOfPlenty,
        cornucopia_cards.HuntingParty,
        cornucopia_cards.Menagerie,
        cornucopia_cards.Tournament,
    ]


class BadOmens(RecommendedSet):
    name = "Bad Omens"
    expansions = [
        DominionExpansion,
        CornucopiaExpansion,
    ]
    card_classes = [
        dominion_cards.Bureaucrat,
        dominion_cards.Laboratory,
        dominion_cards.Merchant,
        dominion_cards.Poacher,
        dominion_cards.ThroneRoom,
        cornucopia_cards.FortuneTeller,
        cornucopia_cards.Hamlet,
        cornucopia_cards.HornOfPlenty,
        cornucopia_cards.Jester,
        cornucopia_cards.Remake,
    ]


class TheJestersWorkshop(RecommendedSet):
    name = "The Jester's Workshop"
    expansions = [
        DominionExpansion,
        CornucopiaExpansion,
    ]
    card_classes = [
        dominion_cards.Artisan,
        dominion_cards.Laboratory,
        dominion_cards.Market,
        dominion_cards.Remodel,
        dominion_cards.Workshop,
        cornucopia_cards.Fairgrounds,
        cornucopia_cards.FarmingVillage,
        cornucopia_cards.HorseTraders,
        cornucopia_cards.Jester,
        cornucopia_cards.YoungWitch
    ]
    additional_cards = [(dominion_cards.Merchant, "Bane")]

    @property
    def expansion_instances(self) -> List[Expansion] | None:
        # Add the Merchant as the Bane card
        if self._expansion_instances is None:
            self._expansion_instances = [
                BaseExpansion(self.game),
                DominionExpansion(self.game),
                CornucopiaExpansion(self.game, bane_card_class=dominion_cards.Merchant),
            ]
        return self._expansion_instances


RECOMMENDED_SETS = [
    BountyOfTheHunt,
    BadOmens,
    TheJestersWorkshop,
]