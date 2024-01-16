from .recommended_set import RecommendedSet
from ...expansions import CornucopiaExpansion, GuildsExpansion
from ...cards import cornucopia_cards, guilds_cards


class Misfortune(RecommendedSet):
    name = "Misfortune"
    expansions = [
        CornucopiaExpansion,
        GuildsExpansion,
    ]
    card_classes = [
        guilds_cards.Advisor,
        guilds_cards.CandlestickMaker,
        guilds_cards.Doctor,
        cornucopia_cards.Fairgrounds,
        cornucopia_cards.FarmingVillage,
        cornucopia_cards.FortuneTeller,
        cornucopia_cards.HorseTraders,
        cornucopia_cards.Jester,
        guilds_cards.Soothsayer,
        guilds_cards.Taxman,
    ]


class BakingContest(RecommendedSet):
    name = "Baking Contest"
    expansions = [
        CornucopiaExpansion,
        GuildsExpansion,
    ]
    card_classes = [
        guilds_cards.Baker,
        cornucopia_cards.FarmingVillage,
        cornucopia_cards.Harvest,
        guilds_cards.Herald,
        guilds_cards.Journeyman,
        guilds_cards.Masterpiece,
        cornucopia_cards.Menagerie,
        cornucopia_cards.Remake,
        guilds_cards.Stonemason,
        cornucopia_cards.Tournament,
    ]
    additional_cards = [(card_class, None) for card_class in cornucopia_cards.PRIZES]


RECOMMENDED_SETS = [
    Misfortune,
    BakingContest,
]