from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Dict, List, Set, Tuple, Type

from ...cards import ALL_KINGDOM_CARDS_BY_EXPANSION
from ...expansions import BaseExpansion, CornucopiaExpansion, ProsperityExpansion

if TYPE_CHECKING:
    from ..cards import Card
    from ...expansions.expansion import Expansion
    from ...game import Game


CustomSetJSON = Dict[str, List[str] | List[Dict[str, str]]]


class CustomSet(metaclass=ABCMeta):
    '''
    Base class for a custom set of cards.

    Args:
        game: The game object with which to use the custom set.
    '''
    def __init__(self, game: Game):
        self.game = game

    @property
    @abstractmethod
    def expansions(self) -> Set[Type[Expansion]]:
        """
        The set of expansions classes whose cards are used in this set.
        """
        pass

    @property
    @abstractmethod
    def card_classes(self) -> Set[Type[Card]]:
        """
        The list of card classes that comprise this set.
        """
        pass

    @property
    def card_names(self) -> List[str]:
        """
        A list of names of the cards that comprise this set.
        """
        return [card_class.name for card_class in self.card_classes]
    
    @property
    def bane_card_name(self) -> str | None:
        """
        The name of the card to use as Bane (when playing with Young Witch)
        or None.
        """
        return None
    
    @property
    def use_platinum_and_colony(self) -> bool | None:
        """
        Whether to use Platinum and Colony.
        
        If True, they will both be used even in no Kingdom cards from
        Prosperity are in play.

        If False, they will not be used.

        If None, whether they are used is determined randomly based on
        the number of Prosperity Kingdom cards in play.
        """
        return None

    @property
    def expansion_instances(self) -> List[Expansion] | None:
        """
        The expansion instances that this custom set adds into the game.

        The Base expansion instance is always included in this list.

        Override this method if the expansions being added into the game
        require specific options.
        """
        instances = [BaseExpansion(self.game)]
        if CornucopiaExpansion in self.expansions:
            if self.bane_card_name is None:
                instances.append(CornucopiaExpansion(self.game))
            else:
                for expansion, expansion_card_classes in ALL_KINGDOM_CARDS_BY_EXPANSION.items():
                    for expansion_card_class in expansion_card_classes:
                        if self.bane_card_name == expansion_card_class.name:
                            bane_card_class = expansion_card_class
                            self.expansions.add(expansion)
                instances.append(CornucopiaExpansion(self.game, bane_card_class=bane_card_class))
        if self.use_platinum_and_colony:
            instances.append(ProsperityExpansion(self.game, platinum_and_colony=True))
        elif ProsperityExpansion in self.expansions:
            if self.use_platinum_and_colony == False:
                instances.append(ProsperityExpansion(self.game, platinum_and_colony=False))
            elif self.use_platinum_and_colony is None:
                instances.append(ProsperityExpansion(self.game))
        instances += [expansion(self.game) for expansion in self.expansions if expansion not in [CornucopiaExpansion, ProsperityExpansion]]
        return instances

    @property
    def json(self) -> CustomSetJSON:
        """
        A JSON representation of this custom set.

        This is essentially reversed by the `from_json` method.
        """
        return {
            "cards": [card_class.name for card_class in self.card_classes],
            "additional_cards": [
                {
                    "card": card_class.name,
                    "role": role,
                }
                for card_class, role in self.additional_cards
            ],
        }
    
    @classmethod
    def from_json(cls, json: CustomSetJSON) -> Type[CustomSet]:
        class ConstructedCustomSet(cls):
            card_classes: Set[Type[Card]] = set()
            expansions: Set[Type[Expansion]] = set()
            card_names: List[str] = json["cards"]
            for card_name in card_names:
                for expansion, expansion_card_classes in ALL_KINGDOM_CARDS_BY_EXPANSION.items():
                    for expansion_card_class in expansion_card_classes:
                        if card_name == expansion_card_class.name:
                            card_classes.add(expansion_card_class)
                            expansions.add(expansion)
            if json.get("bane_card_name", None) is not None:
                @property
                def bane_card_name(self):
                    return json.get("bane_card_name", None)
            if json.get("use_platinum_and_colony", None) is not None:
                @property
                def use_platinum_and_colony(self):
                    return json.get("use_platinum_and_colony", None)
        return ConstructedCustomSet