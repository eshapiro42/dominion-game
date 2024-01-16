from .recommended_set import RecommendedSet
from ...expansions import CornucopiaExpansion, HinterlandsExpansion
from ...cards import cornucopia_cards, hinterlands_cards


class BlueHarvest(RecommendedSet):
    name = "Blue Harvest"
    expansions = [
        CornucopiaExpansion,
        HinterlandsExpansion,
    ]
    card_classes = [
        cornucopia_cards.Hamlet,
        cornucopia_cards.HornOfPlenty,
        cornucopia_cards.HorseTraders,
        cornucopia_cards.Jester,
        cornucopia_cards.Tournament,
        hinterlands_cards.FoolsGold,
        hinterlands_cards.Mandarin,
        hinterlands_cards.NobleBrigand,
        hinterlands_cards.Trader,
        hinterlands_cards.Tunnel,
    ]
    additional_cards = [(card_class, None) for card_class in cornucopia_cards.PRIZES]


class TravelingCircus(RecommendedSet):
    name = "Traveling Circus"
    expansions = [
        CornucopiaExpansion,
        HinterlandsExpansion,
    ]
    card_classes = [
        cornucopia_cards.Fairgrounds,
        cornucopia_cards.FarmingVillage,
        cornucopia_cards.HuntingParty,
        cornucopia_cards.Jester,
        cornucopia_cards.Menagerie,
        hinterlands_cards.BorderVillage,
        hinterlands_cards.Embassy,
        hinterlands_cards.FoolsGold,
        hinterlands_cards.NomadCamp,
        hinterlands_cards.Oasis,
    ]


RECOMMENDED_SETS = [
    BlueHarvest,
    TravelingCircus,
]