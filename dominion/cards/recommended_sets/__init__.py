from __future__ import annotations

from typing import TYPE_CHECKING, List, Type

from .dominion import RECOMMENDED_SETS as dominion_recommended_sets
from .dominion_intrigue import RECOMMENDED_SETS as dominion_intrigue_recommended_sets
from .dominion_prosperity import RECOMMENDED_SETS as dominion_prosperity_recommended_sets
from .dominion_cornucopia import RECOMMENDED_SETS as dominion_cornucopia_recommended_sets
from .dominion_hinterlands import RECOMMENDED_SETS as dominion_hinterlands_recommended_sets
from .dominion_guilds import RECOMMENDED_SETS as dominion_guilds_recommended_sets
from .intrigue import RECOMMENDED_SETS as intrigue_recommended_sets
from .intrigue_prosperity import RECOMMENDED_SETS as intrigue_prosperity_recommended_sets
from .intrigue_cornucopia import RECOMMENDED_SETS as intrigue_cornucopia_recommended_sets
from .intrigue_hinterlands import RECOMMENDED_SETS as intrigue_hinterlands_recommended_sets
from .intrigue_guilds import RECOMMENDED_SETS as intrigue_guilds_recommended_sets
from .prosperity import RECOMMENDED_SETS as prosperity_recommended_sets
from .prosperity_cornucopia import RECOMMENDED_SETS as prosperity_cornucopia_recommended_sets
from .prosperity_hinterlands import RECOMMENDED_SETS as prosperity_hinterlands_recommended_sets
from .cornucopia_hinterlands import RECOMMENDED_SETS as cornucopia_hinterlands_recommended_sets
from .cornucopia_guilds import RECOMMENDED_SETS as cornucopia_guilds_recommended_sets
from .hinterlands import RECOMMENDED_SETS as hinterlands_recommended_sets

if TYPE_CHECKING:
    from .recommended_set import RecommendedSet
    from ...expansions.expansion import Expansion


ALL_RECOMMENDED_SETS = (
    dominion_recommended_sets
    + dominion_intrigue_recommended_sets
    + dominion_prosperity_recommended_sets
    + dominion_cornucopia_recommended_sets
    + dominion_hinterlands_recommended_sets
    + dominion_guilds_recommended_sets
    + intrigue_recommended_sets
    + intrigue_prosperity_recommended_sets
    + intrigue_cornucopia_recommended_sets
    + intrigue_hinterlands_recommended_sets
    + intrigue_guilds_recommended_sets
    + prosperity_recommended_sets
    + prosperity_cornucopia_recommended_sets
    + prosperity_hinterlands_recommended_sets
    + cornucopia_hinterlands_recommended_sets
    + cornucopia_guilds_recommended_sets
    + hinterlands_recommended_sets
)


def find_recommended_sets(expansions: List[Type[Expansion]]) -> List[RecommendedSet]:
    """
    Find recommended sets matching the given expansions.

    Args:
        expansions: List of expansions to find recommended sets for.

    Returns:
        List of recommended sets matching the given expansions.
    """
    recommended_sets = []
    recommended_set: RecommendedSet
    for recommended_set in ALL_RECOMMENDED_SETS:
        if recommended_set.expansions == expansions:
            recommended_sets.append(recommended_set)
    return recommended_sets
