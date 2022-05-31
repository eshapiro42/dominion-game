from .recommended_set import RecommendedSet
from ...expansions import DominionExpansion, HinterlandsExpansion
from ...cards import dominion_cards, hinterlands_cards


class HighwayRobbery(RecommendedSet):
    name = "Highway Robbery"
    expansions = [
        DominionExpansion,
        HinterlandsExpansion,
    ]
    card_classes = [
        dominion_cards.Cellar,
        dominion_cards.Library,
        dominion_cards.Moneylender,
        dominion_cards.ThroneRoom,
        dominion_cards.Workshop,
        hinterlands_cards.Highway,
        hinterlands_cards.Inn,
        hinterlands_cards.Margrave,
        hinterlands_cards.NobleBrigand,
        hinterlands_cards.Oasis,
    ]


class AdventuresAbroad(RecommendedSet):
    name = "Adventures Abroad"
    expansions = [
        DominionExpansion,
        HinterlandsExpansion,
    ]
    card_classes = [
        dominion_cards.Festival,
        dominion_cards.Laboratory,
        dominion_cards.Remodel,
        dominion_cards.Sentry,
        dominion_cards.Vassal,
        hinterlands_cards.Crossroads,
        hinterlands_cards.Farmland,
        hinterlands_cards.FoolsGold,
        hinterlands_cards.Oracle,
        hinterlands_cards.SpiceMerchant,
    ]


RECOMMENDED_SETS = [
    HighwayRobbery,
    AdventuresAbroad,
]