import math
from abc import ABCMeta, abstractmethod
from enum import Enum, auto


class CardType(Enum):
    TREASURE = auto()
    ACTION = auto()
    REACTION = auto()
    ATTACK = auto()
    VICTORY = auto()
    CURSE = auto()


class Card(metaclass=ABCMeta):
    '''Base card class.

    Attributes:
        player: the player who owns the card
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
    def play(self, turn):
        pass


class ReactionCard(ActionCard):
    '''Base reaction card class.

    Abstract methods:
        react: complete the reactive directions on the card
    '''
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


# BASIC CARDS


class Copper(TreasureCard):
    name = 'Copper'
    cost = 0
    types = [CardType.TREASURE]
    image_path = ''
    value = 1

class Silver(TreasureCard):
    name = 'Silver'
    cost = 3
    types = [CardType.TREASURE]
    image_path = ''
    value = 2

class Gold(TreasureCard):
    name = 'Gold'
    cost = 6
    types = [CardType.TREASURE]
    image_path = ''
    value = 3

class Estate(VictoryCard):
    name = 'Estate'
    cost = 2
    types = [CardType.VICTORY]
    image_path = ''
    points = 1

class Duchy(VictoryCard):
    name = 'Duchy'
    cost = 5
    types = [CardType.VICTORY]
    image_path = ''
    points = 3

class Province(VictoryCard):
    name = 'Province'
    cost = 8
    types = [CardType.VICTORY]
    image_path = ''
    points = 6

class Curse(CurseCard):
    name = 'Curse'
    cost = 0
    types = [CardType.CURSE]
    image_path = ''
    points = -1


BASIC_CARDS = [
    Copper,
    Silver,
    Gold,
    Estate,
    Duchy,
    Province,
    Curse
]


# KINGDOM CARDS # TODO: Implement card actions


class Cellar(ActionCard):
    name = 'Cellar'
    cost = 2
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Action',
            'Discard any number of cards, then draw that many.'
        ]
    )

    extra_cards = 0
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def cellar_action(self):
        discarded_card_count = 0
        while True:
            print('Choose a card to discard.\n')
            card_to_discard = self.owner.choose_card_from_hand(force=False)
            if card_to_discard is None:
                break
            else:
                discarded_card_count += 1
                self.owner.player_mat.discard(card_to_discard)
        self.owner.player_mat.draw(discarded_card_count)

    def play(self):
        self.cellar_action()


class Chapel(ActionCard):
    name = 'Chapel'
    cost = 2
    types = [CardType.ACTION]
    image_path = ''

    description = 'Trash up to 4 cards from your hand.'

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def chapel_action(self):
        for _ in range(4):
            print('Choose a card to trash.\n')
            card_to_trash = self.owner.choose_card_from_hand(force=False)
            if card_to_trash is None:
                break
            else:
                self.owner.player_mat.trash(card_to_trash)

    def play(self):
        self.chapel_action()


class Moat(ReactionCard):
    name = 'Moat'
    cost = 2
    types = [CardType.ACTION, CardType.REACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+2 Cards',
            'When another player plays an Attack card, you may first reveal this from your hand, to be unaffected by it.'
        ]
    )

    extra_cards = 2
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def play(self):
        # TODO: Implement Moat
        pass

    def react(self):
        # TODO: Implement Moat
        pass


class Harbinger(ActionCard):
    name = 'Harbinger'
    cost = 3
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Card',
            '+1 Action',
            'Look through your discard pile. You may put a card from it onto your deck.'
        ]
    )

    extra_cards = 1
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def harbinger_action(self):
        print('Choose a card from your discard pile.\n')
        card = self.owner.choose_card_from_discard_pile(force=False)
        if card is not None:
            self.owner.player_mat.deck.append(card)
            self.owner.player_mat.discard_pile.remove(card)

    def play(self):
        self.harbinger_action()


class Merchant(ActionCard):
    name = 'Merchant'
    cost = 3
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Card',
            '+1 Action',
            'The first time you play a Silver this turn, +1 Copper.'
        ]
    )
    
    extra_cards = 1
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def merchant_action(self):
        # TODO: Implement Merchant
        pass

    def play(self):
        self.merchant_action()


class Vassal(ActionCard):
    name = 'Vassal'
    cost = 3
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+2 Coppers',
            "Discard the top card of your deck. If it's an Action card, you may play it."
        ]
    )
    
    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 2

    def vassal_action(self):
        card = self.owner.player_mat.deck.pop()
        self.owner.player_mat.discard_pile.append(card)
        if CardType.ACTION in card.types:
            print(f'You revealed a {card.name}. Would you like to play it?')
            play_card = self.owner.choose_yes_or_no()
            if play_card:
                card.play()

    def play(self):
        self.vassal_action()


class Village(ActionCard):
    name = 'Village'
    cost = 3
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Card',
            '+2 Actions'
        ]
    )
    
    extra_cards = 1
    extra_actions = 2
    extra_buys = 0
    extra_coppers = 0

    def village_action(self):
        pass

    def play(self):
        self.village_action()


class Workshop(ActionCard):
    name = 'Workshop'
    cost = 3
    types = [CardType.ACTION]
    image_path = ''

    description = 'Gain a card costing up to 4 Coppers.'

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def workshop_action(self):
        # TODO: Implement Workshop
        pass

    def play(self):
        self.workshop_action()


class Bureaucrat(ActionCard):
    name = 'Bureaucrat'
    cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = ''

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def bureaucrat_action(self):
        # TODO: Implement Bureaucrat
        pass

    def play(self):
        self.bureaucrat_action()


class Gardens(VictoryCard):
    name = 'Gardens'
    cost = 4
    types = [CardType.VICTORY]
    image_path = ''

    description = 'Worth 1 victory point per 10 cards you have (round down).'

    @property
    def points(self):
        num_cards = len(self.owner.player_mat.all_cards)
        return math.floor(num_cards / 10)


class Militia(ActionCard):
    name = 'Militia'
    cost = 4
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = ''

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 2

    def militia_action(self):
        # TODO: Implement Militia
        pass

    def play(self):
        self.militia_action()


class Moneylender(ActionCard):
    name = 'Moneylender'
    cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = ''

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def moneylender_action(self):
        # TODO: Implement Moneylender
        pass

    def play(self):
        self.moneylender_action()


class Poacher(ActionCard):
    name = 'Poacher'
    cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = ''

    extra_cards = 1
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 1

    def poacher_action(self):
        # TODO: Implement Poacher
        pass

    def play(self):
        self.poacher_action()


class Remodel(ActionCard):
    name = 'Remodel'
    cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = ''

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def remodel_action(self):
        # TODO: Implement Remodel
        pass

    def play(self):
        self.remodel_action()







KINGDOM_CARDS = [
    Cellar,
    Chapel,
    # Moat,
    Harbinger,
    # Merchant,
    Vassal,
    Village,
    # Workshop,
    # Bureaucrat,
    Gardens,
    # Militia,
    # Moneylender,
    # Poacher,
    # Remodel,
    # Smithy,
    # ThroneRoom,
    # Bandit,
    # CouncilRoom,
    # Festival,
    # Laboratory,
    # Library,
    # Market,
    # Mine,
    # Sentry,
    # Witch,
    # Artisan,
    # Chancellor,
    # Woodcutter,
    # Feast,
    # Spy,
    # Thief,
    # Adventurer
]