from abc import ABCMeta, abstractmethod
from enum import Enum, auto
from ..grammar import a


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
        self._owner = owner

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

    def __repr__(self):
        return self.name


class TreasureCard(Card):
    '''Base treasure card class.

    Abstract properties:
        value:  the number of coppers this card is worth (int)
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

    Abstract methods:
        prompt: a description of the attack on other players
        attack_effect: the effect of an attack on a single other player
    '''
    attacking = True

    def attack(self):
        if self.attacking:
            if self.prompt is not None:
                self.game.broadcast(self.prompt)
            immune_players = set()
            self.game.broadcast('Checking if any other players have a Reaction card in their hand...')
            for player in self.owner.other_players:
                # First, check if they have a reaction card in their hand
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
                                    immune_players.add(player)
                                if ignore_again:
                                    reaction_card_classes_to_ignore.add(type(reaction_card))
                # Now force non-immune players to endure the attack effect
                if player in immune_players:
                    self.game.broadcast(f'{player} is immune to the effects.')
                    continue
                else:
                    self.attack_effect(self.owner, player)

    def play(self):
        self.action()
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
