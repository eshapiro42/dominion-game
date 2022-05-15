from .recommended_set import RecommendedSet
from ...expansions import ProsperityExpansion, CornucopiaExpansion
from ...cards import prosperity_cards, cornucopia_cards


class Detours(RecommendedSet):
    name = "Detours"
    expansions = [
        ProsperityExpansion,
        CornucopiaExpansion,
    ]
    card_classes = [
        prosperity_cards.Rabble,
        prosperity_cards.Peddler,
        prosperity_cards.Hoard,
        prosperity_cards.TradeRoute,
        prosperity_cards.Venture,
        cornucopia_cards.FarmingVillage,
        cornucopia_cards.HornOfPlenty,
        cornucopia_cards.Jester,
        cornucopia_cards.Remake,
        cornucopia_cards.Tournament,
    ]


RECOMMENDED_SETS = [Detours]