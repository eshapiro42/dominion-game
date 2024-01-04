from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Dict, List, Tuple, Type

from ...expansions.base import BaseExpansion

if TYPE_CHECKING:
    from ..cards import Card
    from ...expansions.expansion import Expansion
    from ...game import Game


class RecommendedSet(metaclass=ABCMeta):
    '''
    Base class for a recommended set of cards.

    Args:
        game: The game object with which to use the recommended set.
    '''
    def __init__(self, game: Game):
        self.game = game
        self._expansion_instances = None

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The name of this set, e.g. "First Game".
        """
        pass

    @property
    @abstractmethod
    def expansions(self) -> List[Type[Expansion]]:
        """
        The list of expansions classes whose cards are used in this set.
        """
        pass

    @property
    @abstractmethod
    def card_classes(self) -> List[Type[Card]]:
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
        recommended set.

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
        The expansion instances that this recommended set adds into the game.

        The Base expansion instance is always included in this list.

        Override this method if the expansions being added into the game
        require specific options.
        """
        if self._expansion_instances is None:
            self._expansion_instances = [BaseExpansion(self.game)] + [expansion(self.game) for expansion in self.expansions]
        return self._expansion_instances

    @property
    def json(self) -> Dict[List[str], List[str], List[Dict[str, str]]]:
        """
        A JSON representation of this recommended set.
        """
        # Construct JSON for additional cards separately
        # This is necessary for cards like Bane cards which require modifications
        additional_cards_json = []
        for card_class, role in self.additional_cards:
            if role == "Bane":
                card_instance_json = card_class().json
                if "bane" not in card_instance_json['types']:
                    card_instance_json['types'].insert(0, "bane")
                    card_instance_json['type'] = "Bane, " + card_instance_json['type']
            else:
                card_instance_json = card_class().json
            additional_cards_json.append(
                {
                    "card": card_instance_json,
                    "role": role
                }
            )
        return {
            "name": self.name,
            "expansions": [expansion.name for expansion in self.expansions],
            "cards": [card_class().json for card_class in self.card_classes],
            "additional_cards": additional_cards_json,
        }