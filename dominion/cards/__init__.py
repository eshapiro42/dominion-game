from collections import defaultdict
from typing import DefaultDict, List, Type

from . import cards
from .cards import Card
from ..expansions import Expansion, ALL_EXPANSIONS

from .dominion_cards import (
    KINGDOM_CARDS as DOMINION_KINGDOM_CARDS,
)
from .cornucopia_cards import (
    KINGDOM_CARDS as CORNUCOPIA_KINGDOM_CARDS,
)
from .guilds_cards import (
    KINGDOM_CARDS as GUILDS_KINGDOM_CARDS,
)
from .hinterlands_cards import (
    KINGDOM_CARDS as HINTERLANDS_KINGDOM_CARDS,
)
from .intrigue_cards import (
    KINGDOM_CARDS as INTRIGUE_KINGDOM_CARDS,
)
from .prosperity_cards import (
    KINGDOM_CARDS as PROSPERITY_KINGDOM_CARDS,
)


ALL_KINGDOM_CARDS: List[Type[Card]] = \
    DOMINION_KINGDOM_CARDS + \
    CORNUCOPIA_KINGDOM_CARDS + \
    GUILDS_KINGDOM_CARDS + \
    HINTERLANDS_KINGDOM_CARDS + \
    INTRIGUE_KINGDOM_CARDS + \
    PROSPERITY_KINGDOM_CARDS


ALL_KINGDOM_CARDS_BY_EXPANSION: DefaultDict[Type[Expansion], List[Type[Card]]] = defaultdict(list)
for expansion in ALL_EXPANSIONS:
    for card_class in ALL_KINGDOM_CARDS:
        if card_class.expansion == expansion.name:
            ALL_KINGDOM_CARDS_BY_EXPANSION[expansion].append(card_class)