from abc import ABCMeta, abstractmethod
from enum import Enum, auto
from gevent import Greenlet, joinall
from threading import Lock # Monkey patched to use gevent Locks

from ..grammar import a, s


LOWEST_ID = 0
ID_LOCK = Lock()


class CardType(Enum):
    TREASURE = auto()
    VICTORY = auto()
    CURSE = auto()
    ACTION = auto()
    REACTION = auto()
    ATTACK = auto()


class ReactionType(Enum):
    IMMUNITY = auto()


class Card(metaclass=ABCMeta):
    '''Base card class.

    Attributes:
        owner: the player who owns the card
        description: the card's description (default: '')

    Abstract properties:
        name:       the name of the card (str)
        cost:       the cost of the card (int)
        types:      the types of card (list[CardType])
        image_path: path to the card's image (str)
    '''
    description = ''

    def __init__(self, owner=None):
        global LOWEST_ID
        self._owner = owner
        with ID_LOCK:
            self.id = LOWEST_ID
            LOWEST_ID += 1

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, owner):
        self._owner = owner
        self.interactions = self.owner.interactions
        self.game = self.owner.game
        self.supply = self.owner.game.supply

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def cost(self):
        pass

    @property
    @abstractmethod
    def types(self):
        pass

    @property
    @abstractmethod
    def image_path(self):
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
            'type': ', '.join([t.name.capitalize() for t in self.types]),
            'id': self.id,
        }

    def __repr__(self):
        return self.name


class TreasureCard(Card):
    '''Base treasure card class.

    Abstract properties:
        value: the number of coppers this card is worth (int)

    Optional methods:
        play: a method to call when the card is played (function)
    '''
    @property
    @abstractmethod
    def value(self):
        pass


class ActionCard(Card):
    '''Base action card class.

    Abstract properties:
        extra_actions
        extra_coppers
        extra_buys
        extra_cards

    Abstract methods:
        play: complete the directions on the card
    '''
    def play(self):
        self.action()

    @property
    @abstractmethod
    def extra_cards(self):
        pass

    @property
    @abstractmethod
    def extra_actions(self):
        pass

    @property
    @abstractmethod
    def extra_buys(self):
        pass

    @property
    @abstractmethod
    def extra_coppers(self):
        pass

    @abstractmethod
    def action(self):
        pass


class AttackCard(ActionCard):
    '''Base attack card class.

    Attributes:
        attacking: whether the card is being used to attack (bool)

        allow_simultaneous_reactions:
            whether to allow simultaneous reactions (bool)

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

    Abstract methods:
        prompt: a description of the attack on other players
        attack_effect: the effect of an attack on a single other player
    '''
    attacking = True
    allow_simultaneous_reactions = False

    def attack(self):
        if self.prompt is not None:
            self.game.broadcast(self.prompt)
        # Simultaneous reactions are only allowed if the attack card allows it AND if simultaneous reactions are enabled for the game
        if self.allow_simultaneous_reactions and self.game.allow_simultaneous_reactions:
            greenlets = [Greenlet.spawn(self.attack_player, player) for player in self.owner.other_players]
            joinall(greenlets)
        else:
            for player in self.owner.other_players:
                self.game.broadcast(f"{player} must react to {self.owner}'s {self.name}.")
                self.attack_player(player)

    def attack_player(self, player):
        # First check if they have a reaction card in their hand
        immune = False
        if any(CardType.REACTION in card.types for card in player.hand):
            reaction_cards_in_hand = [card for card in player.hand if CardType.REACTION in card.types]
            reaction_card_classes_to_ignore = set() # We don't want to keep asking about reaction card classes that have already been played/ignored
            for reaction_card in reaction_cards_in_hand:
                if type(reaction_card) in reaction_card_classes_to_ignore or not reaction_card.can_react:
                    continue
                else:
                    prompt = f'{player}: You have a Reaction card ({reaction_card.name}) in your hand. Play it?'
                    if player.interactions.choose_yes_or_no(prompt=prompt):
                        self.game.broadcast(f'{player} revealed {a(reaction_card.name)}.')
                        reaction_type, ignore_again = reaction_card.react()
                        if reaction_type == ReactionType.IMMUNITY:
                            immune = True
                            self.game.broadcast(f"{player} is immune to the effects.")
                        if ignore_again:
                            reaction_card_classes_to_ignore.add(type(reaction_card))
        # If the player is not immune, they are forced to endure the attack effect
        if not immune:
            self.attack_effect(self.owner, player)

    def play(self):
        self.action()
        if self.attacking:
            self.attack()

    @property
    @abstractmethod
    def prompt(self):
        pass

    @abstractmethod
    def attack_effect(self, attacker, player):
        pass


class ReactionCard(ActionCard):
    '''Base reaction card class.

    Abstract methods:
        react (optional): complete the reactive directions on the card
    '''
    @property
    @abstractmethod
    def can_react(self):
        pass

    @abstractmethod
    def react(self):
        """
        Returns:
            reaction_type (ReactionType): the type of reaction
            ignore_again (bool): whether to ignore the reaction card again
        """
        pass


class VictoryCard(Card):
    '''Base victory card class.

    Abstract properties:
        points:  the number of victory points this card is worth (int)
    '''
    @property
    @abstractmethod
    def points(self):
        pass


class CurseCard(Card):
    '''Base curse card class.

    Abstract properties:
        points:  the number of victory points this card is worth (int)
    '''
    @property
    @abstractmethod
    def points(self):
        pass
