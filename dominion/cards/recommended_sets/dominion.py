from .recommended_set import RecommendedSet
from ...expansions import DominionExpansion
from ...cards import dominion_cards


class FirstGame(RecommendedSet):
    name = "First Game"
    expansions = [DominionExpansion]
    card_classes = [
        dominion_cards.Cellar,
        dominion_cards.Market,
        dominion_cards.Merchant,
        dominion_cards.Militia,
        dominion_cards.Mine,
        dominion_cards.Moat,
        dominion_cards.Remodel,
        dominion_cards.Smithy,
        dominion_cards.Village,
        dominion_cards.Workshop,
    ]


class SizeDistortion(RecommendedSet):
    name = "Size Distortion"
    expansions = [DominionExpansion]
    card_classes = [
        dominion_cards.Artisan,
        dominion_cards.Bandit,
        dominion_cards.Bureaucrat,
        dominion_cards.Chapel,
        dominion_cards.Festival,
        dominion_cards.Gardens,
        dominion_cards.Sentry,
        dominion_cards.ThroneRoom,
        dominion_cards.Witch,
        dominion_cards.Workshop,
    ]


class DeckTop(RecommendedSet):
    name = "Deck Top"
    expansions = [DominionExpansion]
    card_classes = [
        dominion_cards.Artisan,
        dominion_cards.Bureaucrat,
        dominion_cards.CouncilRoom,
        dominion_cards.Festival,
        dominion_cards.Harbinger,
        dominion_cards.Laboratory,
        dominion_cards.Moneylender,
        dominion_cards.Sentry,
        dominion_cards.Vassal,
        dominion_cards.Village,
    ]


class SleightOfHand(RecommendedSet):
    name = "Sleight of Hand"
    expansions = [DominionExpansion]
    card_classes = [
        dominion_cards.Cellar,
        dominion_cards.CouncilRoom,
        dominion_cards.Festival,
        dominion_cards.Gardens,
        dominion_cards.Library,
        dominion_cards.Harbinger,
        dominion_cards.Militia,
        dominion_cards.Poacher,
        dominion_cards.Smithy,
        dominion_cards.ThroneRoom,
    ]


class Improvements(RecommendedSet):
    name = "Improvements"
    expansions = [DominionExpansion]
    card_classes = [
        dominion_cards.Artisan,
        dominion_cards.Cellar,
        dominion_cards.Market,
        dominion_cards.Merchant,
        dominion_cards.Mine,
        dominion_cards.Moat,
        dominion_cards.Moneylender,
        dominion_cards.Poacher,
        dominion_cards.Remodel,
        dominion_cards.Witch,
    ]


class SilverAndGold(RecommendedSet):
    name = "Silver and Gold"
    expansions = [DominionExpansion]
    card_classes = [
        dominion_cards.Bandit,
        dominion_cards.Bureaucrat,
        dominion_cards.Chapel,
        dominion_cards.Harbinger,
        dominion_cards.Laboratory,
        dominion_cards.Merchant,
        dominion_cards.Mine,
        dominion_cards.Moneylender,
        dominion_cards.ThroneRoom,
        dominion_cards.Vassal,
    ]


RECOMMENDED_SETS = [
    FirstGame,
    SizeDistortion,
    DeckTop,
    SleightOfHand,
    Improvements,
    SilverAndGold,
]