from .recommended_set import RecommendedSet
from ...expansions import HinterlandsExpansion, GuildsExpansion
from ...cards import hinterlands_cards, guilds_cards


class Exchanges(RecommendedSet):
    name = "Exchanges"
    expansions = [
        HinterlandsExpansion,
        GuildsExpansion,
    ]
    card_classes = [
        guilds_cards.Butcher,
        guilds_cards.Herald,
        guilds_cards.Masterpiece,
        guilds_cards.Soothsayer,
        guilds_cards.Stonemason,
        hinterlands_cards.BorderVillage,
        hinterlands_cards.Cauldron, # Not implemented yet (second edition of Hinterlands)
        hinterlands_cards.Develop,
        hinterlands_cards.Stables,
        hinterlands_cards.Trader,
    ]


RECOMMENDED_SETS = [Exchanges]
