from .recommended_set import RecommendedSet
from ...expansions import HinterlandsExpansion
from ...cards import hinterlands_cards


class Introduction(RecommendedSet):
    name = "Introduction"
    expansions = [HinterlandsExpansion]
    card_classes = [
        hinterlands_cards.Cache,
        hinterlands_cards.Crossroads,
        hinterlands_cards.Develop,
        hinterlands_cards.Haggler,
        hinterlands_cards.JackOfAllTrades,
        hinterlands_cards.Margrave,
        hinterlands_cards.NomadCamp,
        hinterlands_cards.Oasis,
        hinterlands_cards.SpiceMerchant,
        hinterlands_cards.Stables,
    ]


class FairTrades(RecommendedSet):
    name = "Fair Trades"
    expansions = [HinterlandsExpansion]
    card_classes = [
        hinterlands_cards.BorderVillage,
        hinterlands_cards.Cartographer,
        hinterlands_cards.Develop,
        hinterlands_cards.Duchess,
        hinterlands_cards.Farmland,
        hinterlands_cards.IllGottenGains,
        hinterlands_cards.NobleBrigand,
        hinterlands_cards.SilkRoad,
        hinterlands_cards.Stables,
        hinterlands_cards.Trader,
    ]


class Bargains(RecommendedSet):
    name = "Bargains"
    expansions = [HinterlandsExpansion]
    card_classes = [
        hinterlands_cards.BorderVillage,
        hinterlands_cards.Cache,
        hinterlands_cards.Duchess,
        hinterlands_cards.FoolsGold,
        hinterlands_cards.Haggler,
        hinterlands_cards.Highway,
        hinterlands_cards.NomadCamp,
        hinterlands_cards.Scheme,
        hinterlands_cards.SpiceMerchant,
        hinterlands_cards.Trader,
    ]


class Gambits(RecommendedSet):
    name = "Gambits"
    expansions = [HinterlandsExpansion]
    card_classes = [
        hinterlands_cards.Cartographer,
        hinterlands_cards.Crossroads,
        hinterlands_cards.Embassy,
        hinterlands_cards.Inn,
        hinterlands_cards.JackOfAllTrades,
        hinterlands_cards.Mandarin,
        hinterlands_cards.NomadCamp,
        hinterlands_cards.Oasis,
        hinterlands_cards.Oracle,
        hinterlands_cards.Tunnel,
    ]


RECOMMENDED_SETS = [
    Introduction,
    FairTrades,
    Bargains,
    Gambits,
]