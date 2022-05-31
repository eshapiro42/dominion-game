from .recommended_set import RecommendedSet
from ...expansions import ProsperityExpansion, HinterlandsExpansion
from ...cards import prosperity_cards, hinterlands_cards


class InstantGratification(RecommendedSet):
    name = "Instant Gratification"
    expansions = [
        ProsperityExpansion,
        HinterlandsExpansion,
    ]
    card_classes = [
        prosperity_cards.Bishop,
        prosperity_cards.Expand,
        prosperity_cards.Hoard,
        prosperity_cards.Mint,
        prosperity_cards.Watchtower,
        hinterlands_cards.Farmland,
        hinterlands_cards.Haggler,
        hinterlands_cards.IllGottenGains,
        hinterlands_cards.NobleBrigand,
        hinterlands_cards.Trader,
    ]


class TreasureTrove(RecommendedSet):
    name = "Treasure Trove"
    expansions = [
        ProsperityExpansion,
        HinterlandsExpansion,
    ]
    card_classes = [
        prosperity_cards.Bank,
        prosperity_cards.Monument,
        prosperity_cards.RoyalSeal,
        prosperity_cards.TradeRoute,
        prosperity_cards.Venture,
        hinterlands_cards.Cache,
        hinterlands_cards.Develop,
        hinterlands_cards.FoolsGold,
        hinterlands_cards.IllGottenGains,
        hinterlands_cards.Mandarin,
    ]


RECOMMENDED_SETS = [
    InstantGratification,
    TreasureTrove,
]