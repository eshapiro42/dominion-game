from .recommended_set import RecommendedSet
from ...expansions import DominionExpansion, IntrigueExpansion
from ...cards import dominion_cards, intrigue_cards


class Underlings(RecommendedSet):
    name = "Underlings"
    expansions = [
        DominionExpansion,
        IntrigueExpansion,
    ]
    card_classes = [
        dominion_cards.Cellar,
        dominion_cards.Festival,
        dominion_cards.Library,
        dominion_cards.Sentry,
        dominion_cards.Vassal,
        intrigue_cards.Courtier,
        intrigue_cards.Diplomat,
        intrigue_cards.Minion,
        intrigue_cards.Nobles,
        intrigue_cards.Pawn,
    ]


class GrandScheme(RecommendedSet):
    name = "Grand Scheme"
    expansions = [
        DominionExpansion,
        IntrigueExpansion,
    ]
    card_classes = [
        dominion_cards.Artisan,
        dominion_cards.CouncilRoom,
        dominion_cards.Market,
        dominion_cards.Militia,
        dominion_cards.Workshop,
        intrigue_cards.Bridge,
        intrigue_cards.Mill,
        intrigue_cards.MiningVillage,
        intrigue_cards.Patrol,
        intrigue_cards.ShantyTown,
    ]


class Deconstruction(RecommendedSet):
    name = "Deconstruction"
    expansions = [
        DominionExpansion,
        IntrigueExpansion,
    ]
    card_classes = [
        dominion_cards.Bandit,
        dominion_cards.Mine,
        dominion_cards.Remodel,
        dominion_cards.ThroneRoom,
        dominion_cards.Village,
        intrigue_cards.Diplomat,
        intrigue_cards.Harem,
        intrigue_cards.Lurker,
        intrigue_cards.Replace,
        intrigue_cards.Swindler,
    ]


RECOMMENDED_SETS = [
    Underlings,
    GrandScheme,
    Deconstruction,
]