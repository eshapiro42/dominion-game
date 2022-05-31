from .recommended_set import RecommendedSet
from ...expansions import IntrigueExpansion, HinterlandsExpansion
from ...cards import intrigue_cards, hinterlands_cards


class MoneyForNothing(RecommendedSet):
    name = "Money for Nothing"
    expansions = [
        IntrigueExpansion,
        HinterlandsExpansion,
    ]
    card_classes = [
        intrigue_cards.Replace,
        intrigue_cards.Patrol,
        intrigue_cards.Pawn,
        intrigue_cards.ShantyTown,
        intrigue_cards.Torturer,
        hinterlands_cards.Cache,
        hinterlands_cards.Cartographer,
        hinterlands_cards.JackOfAllTrades,
        hinterlands_cards.SilkRoad,
        hinterlands_cards.Tunnel,
    ]


class TheDukesBall(RecommendedSet):
    name = "The Duke's Ball"
    expansions = [
        IntrigueExpansion,
        HinterlandsExpansion,
    ]
    card_classes = [
        intrigue_cards.Conspirator,
        intrigue_cards.Duke,
        intrigue_cards.Harem,
        intrigue_cards.Masquerade,
        intrigue_cards.Upgrade,
        hinterlands_cards.Duchess,
        hinterlands_cards.Haggler,
        hinterlands_cards.Inn,
        hinterlands_cards.NobleBrigand,
        hinterlands_cards.Scheme,
    ]


RECOMMENDED_SETS = [
    MoneyForNothing,
    TheDukesBall,
]