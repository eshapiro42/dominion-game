from __future__ import annotations

from abc import ABCMeta, abstractmethod
from collections import defaultdict
from enum import Enum, auto
from gevent import Greenlet, joinall
from typing import TYPE_CHECKING, Any, Optional, Deque, Dict, List, Tuple, Type

from ..grammar import a, s, Word

if TYPE_CHECKING:
    from ..game import Game
    from ..interactions.interaction import Interaction
    from ..player import Player
    from ..supply import Supply


class CardType(Enum):
    """
    Enumeration of all card types.
    """
    TREASURE = auto()
    VICTORY = auto()
    CURSE = auto()
    ACTION = auto()
    REACTION = auto()
    ATTACK = auto()
    PRIZE = auto()
    BANE = auto()


class ReactionType(Enum):
    """
    Emumeration of all reaction types.
    """
    ATTACK = auto()
    GAIN = auto()


class Card(Word, metaclass=ABCMeta):
    '''
    Base card class.

    Args:
        owner: The owner of the card.
    '''
    __lowest_id = 0

    description = ''

    def __init__(self, owner: Player | None = None):
        self._owner = owner
        self._id = Card.__lowest_id
        Card.__lowest_id += 1

    @property
    def owner(self) -> Player | None:
        """
        The owner of the card.
        """
        return self._owner

    @owner.setter
    def owner(self, owner: Player | None):
        self._owner: Player = owner
        if owner is not None:
            self.interactions: Interaction = self.owner.interactions
            self.game: Game = self.owner.game
            self.supply: Supply = self.owner.game.supply

    @property
    def id(self) -> int:
        """
        The unique ID of the card.
        """
        return self._id

    @classmethod
    @property
    def singular(cls) -> str:
        """
        The singular name of the card.

        E.g., "Copper".
        """
        return cls.name

    @classmethod
    @property
    def pluralized(cls) -> str:
        """
        Standard pluralized name of the card (i.e., add an "s").

        E.g., "Coppers".
        
        Override this for cards with non-standard pluralization, like Library.
        """
        return f"{cls.name}s"

    @classmethod
    @property
    def can_overpay(cls) -> bool:
        """
        Whether the card can be overpaid for.

        Defaults to False. Override this for any card that can be overpaid for.

        Specific to Guilds expansion.
        """
        return False

    @classmethod
    def overpay(cls, amount_overpaid: int):
        """
        Action to perform when a card is overpaid for.

        Does nothing by default. Override this for any card that can be overpaid for.

        Args:
            amount_overpaid: The amount of coppers by which the card was overpaid.

        Specific to Guilds expansion.
        """
        pass

    @property
    def overpay_description(self) -> Optional[str]:
        """
        A string describing the effect of overpaying for this card, which
        should start with a lower-case letter.

        Defaults to None. Override this for any card that can be overpaid for.

        Specific to Guilds expansion.
        """
        pass

    @property
    def cost(self) -> int:
        """
        The cost of the card.
        """
        return self._cost if not hasattr(self, "game") else self.game.current_turn.get_cost(self)

    @property
    def gain_to(self) -> Deque[Card]:
        """
        The deque to which the card is being added.

        Defaults to the player's discard pile. Override this for
        cards that are gained to other locations, e.g., Nomad Camp.
        """
        return self.owner.discard_pile
    
    @classmethod
    @property
    def has_plus_two_actions(self) -> bool:
        """
        Whether the card gives >= +2 Actions.

        By default, this is calculated from the `extra_actions` property. However,
        since only Action cards have this property and not all cards that give
        >= +2 Actions have that property set, this should be overridden for any
        cards that need explicit handling.
        """
        return hasattr(self, "extra_actions") and self.extra_actions >= 2
    
    @classmethod
    @property
    def has_plus_one_card(self) -> bool:
        """
        Whether the card gives >= +1 Cards.

        By default, this is calculated from the `extra_cards` property. However,
        since only Action cards have this property and not all cards that give
        >= +1 Cards have that property set, this should be overridden for any
        cards that need explicit handling.
        """
        return hasattr(self, "extra_cards") and self.extra_cards >= 1
    
    @classmethod
    @property
    def has_plus_one_buy(self) -> bool:
        """
        Whether the card gives >= +1 Buys.

        By default, this is calculated from the `extra_buys` property. However,
        since only Action cards have this property and not all cards that give
        >= +1 Buys have that property set, this should be overridden for any
        cards that need explicit handling.
        """
        return hasattr(self, "extra_buys") and self.extra_buys >= 1
    
    @classmethod
    @property
    def has_trashing(self) -> bool:
        """
        Whether the card allows Trashing.

        TODO: This is currently calculated from the card description. This
        implementation may not be totally accurate if a card mentions Trashing
        but does not itself allow Trashing of cards.
        """
        return "trash" in self.description.lower()

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The name of the card.
        """
        pass

    @property
    @abstractmethod
    def _cost(self) -> int:
        """
        The cost of the card.
        """
        pass

    @property
    @abstractmethod
    def types(self) -> List[CardType]:
        """
        A list of the cards types.

        E.g.:
        
        .. highlight:: python
        .. code-block:: python
            
            prosperity_cards.Goons.types = [CardType.ACTION, CardType.ATTACK]
        """
        pass

    @property
    @abstractmethod
    def image_path(self) -> str:
        """
        A path to the card's background image.

        This is not currently used.
        """
        pass

    @property
    def json(self):
        extra_cards = self.extra_cards if hasattr(self, 'extra_cards') else 0
        extra_actions = self.extra_actions if hasattr(self, 'extra_actions') else 0
        extra_buys = self.extra_buys if hasattr(self, 'extra_buys') else 0
        extra_coppers = self.extra_coppers if hasattr(self, 'extra_coppers') else 0
        effects = []
        if extra_cards:
            effects.append(f"+{s(extra_cards, 'Card')}")
        if extra_actions:
            effects.append(f"+{s(extra_actions, 'Action')}")
        if extra_buys:
            effects.append(f"+{s(extra_buys, 'Buy')}")
        if extra_coppers:
            effects.append(f"+{extra_coppers} $")
        return {
            'name': self.name,
            'effects': effects,
            # 'description': self.description.replace("\n", "<br>"),
            'description': self.description.split("\n"),
            'cost': self.cost,
            'types': [t.name.lower() for t in self.types], # List of types (all lowercase)
            'type': ', '.join([t.name.capitalize() for t in self.types]), # String of types
            'id': self.id,
            'expansion': self.expansion,
        }

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    @staticmethod
    def group_and_sort_by_cost(cards: list[Card]) -> str:
        """
        Given a list of cards, return a comma-separated string of
        the cards with their quantities and ordered by cost.

        Args:
            cards: A list of Cards.
        """
        card_class_counts: Dict[Type[Card], int] = defaultdict(int) # compute as a dict first since that's easier
        for card in cards:
            card_class_counts[type(card)] += 1
        card_class_counts: List[Tuple[Type[Card], int]] = list(card_class_counts.items()) # convert from dict[card_class, count] into list[tuple(card_class, count)]
        # Sort the cards by cost (sorting by value would be tricky because of cards like Bank)
        sorted_card_class_counts = sorted(card_class_counts, key=lambda card_tuple: card_tuple[0]._cost, reverse=True)
        card_strings = [s(quantity, card_class) for card_class, quantity in sorted_card_class_counts]
        return ", ".join(card_strings)


class TreasureCard(Card):
    '''
    Base treasure card class.
    '''
    @property
    @abstractmethod
    def value(self) -> int:
        """
        The number of coppers this card is worth.
        """
        pass

    def play(self):
        """
        An optional method to call when the card is played.
        """
        pass


class ActionCard(Card):
    '''
    Base action card class.
    '''
    def play(self):
        """
        Just calls :meth:`action`.
        """
        self.action()

    @property
    @abstractmethod
    def extra_cards(self) -> int:
        """
        The number of cards to draw when this card is played.
        """
        pass

    @property
    @abstractmethod
    def extra_actions(self) -> int:
        """
        The number of extra actions granted when this card is played.
        """
        pass

    @property
    @abstractmethod
    def extra_buys(self) -> int:
        """
        The number of extra buys granted when this card is played.
        """
        pass

    @property
    @abstractmethod
    def extra_coppers(self) -> int:
        """
        The number of extra coppers granted when this card is played.
        """
        pass

    @abstractmethod
    def action(self):
        """
        Complete the directions on the card.

        This method should not move the played card between
        deques, although it might need to move other cards
        (e.g., if playing it causes the player to gain a card).
        """
        pass


class AttackCard(ActionCard):
    '''
    Base attack card class.
    '''

    def __init__(self):
        super().__init__()
        self._attacking = True

    @property
    def attacking(self) -> bool:
        """
        Whether the card is being used to attack.
        """
        return self._attacking

    @attacking.setter
    def attacking(self, attacking: bool):
        self._attacking = attacking

    @property
    def allow_simultaneous_reactions(self) -> bool:
        """
        Whether to allow simultaneous reactions for this card.

        If simultaneous reactions are not allowed for the game,
        then this has no effect.

        This currently only works for attack effects where the
        only required input is from the players being attacked,
        such as  with the Militia. If the attack requires feedback
        from the attacker, like with Spy, Thief, Swindler, etc,
        the frontend is not currently equipped to deal with
        simultaneous reactions.

        This also cannot be used for attacks that require the
        attacked players to gain cards from the Supply, such as Witch,
        Swindler, Torturer, Replace, etc. That's because there may be
        only one of a given card left in the Supply, and therefore the
        effect must be resolved in turn order.
        """
        return False

    def attack(self, attack_parameter: Any = None):
        if self.prompt is not None:
            self.game.broadcast(self.prompt)
        # Simultaneous reactions are only allowed if the attack card allows it AND if simultaneous reactions are enabled for the game
        if self.allow_simultaneous_reactions and self.game.allow_simultaneous_reactions:
            greenlets = [Greenlet.spawn(self.attack_player, player, attack_parameter) for player in self.owner.other_players]
            joinall(greenlets)
        else:
            for player in self.owner.other_players:
                self.game.broadcast(f"{player} must react to {self.owner}'s {self.name}.")
                self.attack_player(player, attack_parameter)

    def attack_player(self, player: Player, attack_parameter: Any = None):
        def get_reaction_cards_in_hand():
            # Get all reaction cards in the player's hand that can react to an attack
            return set(card for card in player.hand if CardType.REACTION in card.types and ReactionType.ATTACK in card.reacts_to)

        # First check if they have a reaction card in their hand
        immune = False
        # Allow the player to play reaction cards
        reaction_cards_in_hand = get_reaction_cards_in_hand()
        reaction_cards_to_ignore = set()
        while (reaction_cards_remaining := reaction_cards_in_hand - reaction_cards_to_ignore):
            invalid_cards = [card for card in player.hand if card not in reaction_cards_remaining]
            prompt = f"{self.owner} played {a(self.name)} (an Attack card). You have {s(len(reaction_cards_remaining), 'playable Reaction card', print_number=False)} in your hand. You may play any or all of them, one at a time."
            reaction_card = player.interactions.choose_card_from_hand(prompt=prompt, force=False, invalid_cards=invalid_cards)
            if reaction_card is None:
                # The player is forfeiting their chance to react
                player.interactions.send('You forfeited your opportunity to react.')
                break
            self.game.broadcast(f"{player} revealed {a(reaction_card.name)} in reaction to {self.owner}'s {self.name}.")
            immune, ignore_card_class_next_time = reaction_card.react_to_attack()
            if ignore_card_class_next_time:
                reaction_cards_to_ignore = reaction_cards_to_ignore.union(set(card for card in player.hand if isinstance(card, type(reaction_card))))
            reaction_cards_in_hand = get_reaction_cards_in_hand()
        # If the player is not immune, they are forced to endure the attack effect
        if immune:
            self.game.broadcast(f"{player} is immune to the effects of {self.owner}'s {self.name}.")
        else:
            try:
                self.attack_effect(self.owner, player, attack_parameter)
            except TypeError:
                from .guilds_cards import Taxman
                if isinstance(self, Taxman):
                    raise
                # The attack_effect method need not take an attack_parameter argument
                self.attack_effect(self.owner, player)

    def play(self):
        """
        Complete the directions on the card and perform the attack,
        if applicable.
        """
        attack_parameter = self.action()
        if self.attacking:
            self.attack(attack_parameter)
            try:
                self.post_attack_action(attack_parameter)
            except TypeError:
                # The post_attack_action method need not take an attack_parameter argument
                self.post_attack_action()

    @property
    @abstractmethod
    def prompt(self):
        """
        A description of the attack on other players.
        """
        pass

    @abstractmethod
    def attack_effect(self, attacker: Player, player: Player, attack_parameter: Any):
        """
        The effect of the attack on a single other player.

        Args:
            attacker: The player who played the attack card.
            player: The player being attacked.
            attack_parameters: An optional parameter returned by the :meth:`action` method.
        """
        pass

    def post_attack_action(self, attack_parameter: Any):
        """
        An optional method to call after the attack is complete.

        Overload for specific attack cards that require something
        to be done after the results of the attack are resolved.

        Args:
            attack_parameters: An optional parameter returned by the :meth:`action` method.
        """
        pass


class ReactionCard(ActionCard):
    '''
    Base reaction card class.
    '''
    @property
    @abstractmethod
    def reacts_to(self) -> List[ReactionType]:
        """
        When the card can react.
        """
        pass

    def react_to_attack(self) -> Tuple[bool, bool]:
        """
        How to react to attack cards if this card is in a player's hand.

        Overload for any reaction card that reacts to attacks.

        Returns a tuple containing:

            immune (:class:`ReactionType`): 
                Whether the reaction makes the player immune to the attack.

            ignore_card_class_next_time (:class:`bool`): 
                Whether this class of reaction card can only be played once in
                response to an attack.

                If False, this class of reaction card can be played multiple times
                in response to an attack.
        """
        pass

    def react_to_gain(self, gained_card: Card, where_it_went: Deque, gained_from_trash: bool = False) -> Tuple[Deque, bool]:
        """
        How to react to gaining cards if this card is in a player's hand.

        Overload for any reaction card that reacts to gaining cards.

        Args:
            gained_card: The card that was gained.
            where_it_went: The location where the card was gained.
            gained_from_trash: Whether the card was gained from the trash (otherwise it was gained from the Supply).

        Returns a tuple containing:

            where_it_went (:class:`Deque`):
                The location where the card was gained.

            ignore_card_class_next_time (:class:`bool`):
                Whether this class of reaction card only be played once in
                response to gaining a card.

                If False, this class of reaction card can be played multiple times
                in response to gaining a card.
        """
        pass


class VictoryCard(Card):
    '''
    Base victory card class.
    '''
    @property
    @abstractmethod
    def points(self) -> int:
        """
        The number of victory points this card is worth.
        """
        pass


class CurseCard(VictoryCard):
    '''
    Base curse card class.
    '''