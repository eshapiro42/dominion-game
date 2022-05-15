from .recommended_set import RecommendedSet
from ...expansions import IntrigueExpansion, ProsperityExpansion
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


RECOMMENDED_SETS = [
    PathsToVictory,
    AllAlongTheWatchtower,
    LuckySeven,
]