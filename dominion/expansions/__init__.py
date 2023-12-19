from typing import List

from .expansion import Expansion
from .base import BaseExpansion
from .dominion import DominionExpansion
from .prosperity import ProsperityExpansion
from .intrigue import IntrigueExpansion
from .cornucopia import CornucopiaExpansion
from .hinterlands import HinterlandsExpansion
from .guilds import GuildsExpansion


ALL_EXPANSIONS: List[Expansion] = [
    BaseExpansion,
    DominionExpansion,
    IntrigueExpansion,
    ProsperityExpansion,
    CornucopiaExpansion,
    HinterlandsExpansion,
    GuildsExpansion,
]