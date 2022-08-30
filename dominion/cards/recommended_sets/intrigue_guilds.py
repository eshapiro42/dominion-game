from .recommended_set import RecommendedSet
from ...expansions import IntrigueExpansion, GuildsExpansion
from ...cards import intrigue_cards, guilds_cards


class NameThatCard(RecommendedSet):
    name = "Name That Card"
    expansions = [
        IntrigueExpansion,
        GuildsExpansion,
    ]
    card_classes = [
        guilds_cards.Baker,
        guilds_cards.Doctor,
        guilds_cards.Plaza,
        guilds_cards.Advisor,
        guilds_cards.Masterpiece,
        intrigue_cards.Courtyard,
        intrigue_cards.Harem,
        intrigue_cards.Nobles,
        intrigue_cards.Replace,
        intrigue_cards.WishingWell,
    ]


class TricksOfTheTrade(RecommendedSet):
    name = "Tricks of the Trade"
    expansions = [
        IntrigueExpansion,
        GuildsExpansion,
    ]
    card_classes = [
        guilds_cards.Stonemason,
        guilds_cards.Herald,
        guilds_cards.Soothsayer,
        guilds_cards.Journeyman,
        guilds_cards.Butcher,
        intrigue_cards.Conspirator,
        intrigue_cards.Masquerade,
        intrigue_cards.Mill,
        intrigue_cards.Nobles,
        intrigue_cards.SecretPassage,
    ]


class DecisionsDecisions(RecommendedSet):
    name = "Decisions, Decisions"
    expansions = [
        IntrigueExpansion,
        GuildsExpansion,
    ]
    card_classes = [
        guilds_cards.MerchantGuild,
        guilds_cards.CandlestickMaker,
        guilds_cards.Masterpiece,
        guilds_cards.Taxman,
        guilds_cards.Butcher,
        intrigue_cards.Bridge,
        intrigue_cards.Pawn,
        intrigue_cards.MiningVillage,
        intrigue_cards.Upgrade,
        intrigue_cards.Duke,
    ]


RECOMMENDED_SETS = [
    NameThatCard,
    TricksOfTheTrade,
    DecisionsDecisions,
]