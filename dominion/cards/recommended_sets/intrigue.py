from .recommended_set import RecommendedSet
from ...expansions import IntrigueExpansion
from ...cards import intrigue_cards


class VictoryDance(RecommendedSet):
    name = "Victory Dance"
    expansions = [IntrigueExpansion]
    card_classes = [
        intrigue_cards.Baron,
        intrigue_cards.Courtier,
        intrigue_cards.Duke,
        intrigue_cards.Harem,
        intrigue_cards.Ironworks,
        intrigue_cards.Masquerade,
        intrigue_cards.Mill,
        intrigue_cards.Nobles,
        intrigue_cards.Patrol,
        intrigue_cards.Replace,
    ]


class ThePlotThickens(RecommendedSet):
    name = "The Plot Thickens"
    expansions = [IntrigueExpansion]
    card_classes = [
        intrigue_cards.Conspirator,
        intrigue_cards.Ironworks,
        intrigue_cards.Lurker,
        intrigue_cards.Pawn,
        intrigue_cards.MiningVillage,
        intrigue_cards.SecretPassage,
        intrigue_cards.Steward,
        intrigue_cards.Swindler,
        intrigue_cards.Torturer,
        intrigue_cards.TradingPost,
    ]


class BestWishes(RecommendedSet):
    name = "Best Wishes"
    expansions = [IntrigueExpansion]
    card_classes = [
        intrigue_cards.Baron,
        intrigue_cards.Conspirator,
        intrigue_cards.Courtyard,
        intrigue_cards.Diplomat,
        intrigue_cards.Duke,
        intrigue_cards.SecretPassage,
        intrigue_cards.ShantyTown,
        intrigue_cards.Torturer,
        intrigue_cards.Upgrade,
        intrigue_cards.WishingWell,
    ]


RECOMMENDED_SETS = [
    VictoryDance,
    ThePlotThickens,
    BestWishes,
]