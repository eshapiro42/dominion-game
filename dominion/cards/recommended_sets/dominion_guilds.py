from .recommended_set import RecommendedSet
from ...expansions import DominionExpansion, GuildsExpansion
from ...cards import dominion_cards, guilds_cards


class ArtsAndCrafts(RecommendedSet):
    name = "Arts and Crafts"
    expansions = [
        DominionExpansion,
        GuildsExpansion,
    ]
    card_classes = [
        dominion_cards.Laboratory,
        dominion_cards.Cellar,
        dominion_cards.Workshop,
        dominion_cards.Festival,
        dominion_cards.Moneylender,
        guilds_cards.Stonemason,
        guilds_cards.Advisor,
        guilds_cards.Baker,
        guilds_cards.Journeyman,
        guilds_cards.MerchantGuild,
    ]


class CleanLiving(RecommendedSet):
    name = "Clean Living"
    expansions = [
        DominionExpansion,
        GuildsExpansion,
    ]
    card_classes = [
        dominion_cards.Bandit,
        dominion_cards.Militia,
        dominion_cards.Moneylender,
        dominion_cards.Gardens,
        dominion_cards.Village,
        guilds_cards.Butcher,
        guilds_cards.Baker,
        guilds_cards.CandlestickMaker,
        guilds_cards.Taxman,
        guilds_cards.Herald,
    ]


class GildingTheLily(RecommendedSet):
    name = "Gilding the Lily"
    expansions = [
        DominionExpansion,
        GuildsExpansion,
    ]
    card_classes = [
        dominion_cards.Library,
        dominion_cards.Merchant,
        dominion_cards.Remodel,
        dominion_cards.Market,
        dominion_cards.Sentry,
        guilds_cards.Plaza,
        guilds_cards.Masterpiece,
        guilds_cards.CandlestickMaker,
        guilds_cards.Taxman,
        guilds_cards.Herald,
    ]


RECOMMENDED_SETS = [
    ArtsAndCrafts,
    CleanLiving,
    GildingTheLily,
]