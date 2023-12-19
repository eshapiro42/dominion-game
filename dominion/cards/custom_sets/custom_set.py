from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Dict, List, Set, Tuple, Type

from ...cards import ALL_KINGDOM_CARDS_BY_EXPANSION
from ...expansions import BaseExpansion, CornucopiaExpansion

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
        self._expansion_instances = None

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
    def additional_cards(self) -> List[Tuple[Type[Card], str]]:
        """
        A list of additional card classes that are not part
        of the basic set of Kingdom cards.

        Override this method if there are any such cards in the
        custom set.

        E.g., Bane cards or Platinum and Colony cards.

        Returns:
            A list of tuples of the form (card_class, role),
            where card_class is the card class and role is a string
            describing the role of the card in the set.
        """
        return []

    @property
    def expansion_instances(self) -> List[Expansion] | None:
        """
        The expansion instances that this custom set adds into the game.

        The Base expansion instance is always included in this list.

        Override this method if the expansions being added into the game
        require specific options.
        """
        if self._expansion_instances is None:
            self._expansion_instances = [BaseExpansion(self.game)] + [expansion(self.game) for expansion in self.expansions]
        return self._expansion_instances

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
            if json["additional_cards"]:
                print(json["additional_cards"])
                for additional_card in json["additional_cards"]:
                    card_name = additional_card["card"]
                    card_role = additional_card["role"]
                    if card_role == "Bane":
                        for expansion, expansion_card_classes in ALL_KINGDOM_CARDS_BY_EXPANSION.items():
                            for expansion_card_class in expansion_card_classes:
                                if card_name == expansion_card_class.name:
                                    bane_card_class = expansion_card_class
                                    expansions.add(expansion)
                                    additional_cards = [(bane_card_class, "Bane")]
                        @property
                        def expansion_instances(self) -> List[Expansion] | None:
                            if self._expansion_instances is None:
                                self._expansion_instances = [
                                    BaseExpansion(self.game),
                                    *(expansion(self.game) for expansion in self.expansions if expansion != CornucopiaExpansion),
                                    CornucopiaExpansion(self.game, bane_card_class=self.bane_card_class),
                                ]
                            return self._expansion_instances
        return ConstructedCustomSet