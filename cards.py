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
            card_to_discard = self.interactions.choose_card_from_hand(force=False)
            if card_to_discard is None:
                break
            else:
                discarded_card_count += 1
                self.owner.discard(card_to_discard)
        drawn_cards = self.owner.draw(discarded_card_count)
        print(f'+{discarded_card_count} cards --> {drawn_cards}\n')


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
            card_to_trash = self.interactions.choose_card_from_hand(force=False)
            if card_to_trash is None:
                break
            else:
                self.owner.trash(card_to_trash)

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

    def moat_action(self):
        pass

    def play(self):
        self.moat_action()

    def react(self):
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
        card = self.interactions.choose_card_from_discard_pile(force=False)
        if card is not None:
            self.owner.deck.append(card)
            self.owner.discard_pile.remove(card)

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
            'The first time you play a Silver this turn, +1 $.'
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
            '+2 $',
            "Discard the top card of your deck. If it's an Action card, you may play it."
        ]
    )
    
    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 2

    def vassal_action(self):
        card = self.owner.deck.pop()
        self.owner.discard_pile.append(card)
        if CardType.ACTION in card.types:
            print(f'You revealed a {card.name}. Would you like to play it?\n')
            if self.interactions.choose_yes_or_no():
                self.owner.turn.action_phase.play_without_side_effects(card)

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

    description = 'Gain a card costing up to 4 $.'

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def workshop_action(self):
        self.owner.turn.buy_phase.buy_without_side_effects(max_cost=4, force=True)

    def play(self):
        self.workshop_action()


class Bureaucrat(ActionCard):
    name = 'Bureaucrat'
    cost = 4
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = 'Gain a Silver onto your deck. Each other player reveals a Victory card from their hand and puts it onto their deck (or reveals a hand with no Victory cards).'

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def bureaucrat_action(self):
        # TODO: Implement Bureaucrat
        # Gain a Silver and put onto deck
        silver = self.supply.draw(Silver)
        silver.owner = self.owner
        self.owner.deck.append(silver)
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
        num_cards = len(self.owner.all_cards)
        return math.floor(num_cards / 10)


class Militia(ActionCard):
    name = 'Militia'
    cost = 4
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = '\n'.join(
        [
            '+2 $',
            'Each other player discards down to 3 cards in hand.'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 2

    def militia_action(self):
        other_players = [player for player in self.game.players if player is not self.owner]
        immune_players = set()
        print(f'Other players ({other_players}) must discard down to 3 cards in their hands.')
        for player in other_players:
            # First, check if they have a reaction card in their hand
            if any(CardType.REACTION in card.types for card in player.hand):
                reaction_cards_in_hand = [card for card in player.hand if CardType.REACTION in card.types]
                reaction_card_classes_to_ignore = set() # We don't want to keep asking about reaction card classes that have already been played/ignored
                for reaction_card in reaction_cards_in_hand:
                    if type(reaction_card) in reaction_card_classes_to_ignore:
                        continue
                    else:
                        print(f'{player}: You have a Reaction ({reaction_card.name}) in your hand. Play it?')
                        if player.interactions.choose_yes_or_no():
                            immune_players.add(player)
                        reaction_card_classes_to_ignore.add(type(reaction_card))
            # Now force non-immune players to discard down to three cards in their hand
            if player in immune_players:
                print(f'{player} is immune to the effects.')
                continue
            else:
                number_to_discard = len(player.hand) - 3
                print(f'{player} must discard {number_to_discard} cards.')
                for card_num in range(number_to_discard):
                    print(f'{player}: Choose card {card_num + 1}/{number_to_discard} to discard.')
                    card_to_discard = player.interactions.choose_card_from_hand(force=True)
                    player.discard(card_to_discard)

    def play(self):
        self.militia_action()


class Moneylender(ActionCard):
    name = 'Moneylender'
    cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = 'You may trash a Copper from your hand for +3 $.'

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def moneylender_action(self):
        print('You may trash a Copper from your hand.\n')
        copper_to_trash = self.interactions.choose_specific_card_class_from_hand(force=False, card_class=Copper)
        if copper_to_trash is not None:
            self.owner.turn.coppers_remaining += 3
            print(f'+3 $ --> {self.owner.turn.coppers_remaining}\n')
            self.owner.trash(copper_to_trash)

    def play(self):
        self.moneylender_action()


class Poacher(ActionCard):
    name = 'Poacher'
    cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Card',
            '+1 Action',
            '+1 $',
            'Discard a card per empty Supply pile.'
        ]
    )

    extra_cards = 1
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 1

    def poacher_action(self):
        number_to_discard = self.supply.num_empty_stacks
        if number_to_discard > 0:
            print(f'You must discard {number_to_discard} cards.\n')
            for num in range(number_to_discard):
                print(f'Choose card {num + 1}/{number_to_discard} to discard.\n')
                card_to_discard = self.interactions.choose_card_from_hand(force=True)
                if card_to_discard is not None:
                    self.owner.discard(card_to_discard)

    def play(self):
        self.poacher_action()


class Remodel(ActionCard):
    name = 'Remodel'
    cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = 'Trash a card from your hand. Gain a card costing up to 2 $ more than it.'

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def remodel_action(self):
        card_to_trash = self.interactions.choose_card_from_hand(force=True)
        if card_to_trash is not None:
            self.owner.trash(card_to_trash)
            max_cost = card_to_trash.cost + 2
            self.owner.turn.buy_phase.buy_without_side_effects(max_cost=max_cost, force=True)

    def play(self):
        self.remodel_action()


class Smithy(ActionCard):
    name = 'Smithy'
    cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '+3 Cards'

    extra_cards = 3
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def smithy_action(self):
        pass

    def play(self):
        self.smithy_action()


class ThroneRoom(ActionCard):
    name = 'Throne Room'
    cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = 'You may play an Action card from your hand twice.'

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def throne_room_action(self):
        print('Select an action card to play twice.\n')
        card = self.interactions.choose_action_card_from_hand()
        if card is not None:
            # Playing the card should not use any actions, so we use a special method
            # The first time, add the card to the played cards area
            self.owner.play(card)
            print(f'Playing {card.name} for the first time.\n')
            self.owner.turn.action_phase.play_without_side_effects(card)
            print(f'Playing {card.name} for the second time.\n')
            self.owner.turn.action_phase.play_without_side_effects(card)

    def play(self):
        self.throne_room_action()


class Bandit(ActionCard):
    name = 'Bandit'
    cost = 5
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = 'Gain a Gold. Each other player reveals the top 2 cards of their deck, trashes a revealed Treasure other than Copper, and discards the rest.'

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def bandit_action(self):
        # TODO: Implement Bandit
        pass

    def play(self):
        self.bandit_action()


class CouncilRoom(ActionCard):
    name = 'Council Room'
    cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+4 Cards',
            '+1 Buy',
            'Each other player draws a card.'
        ]
    )

    extra_cards = 4
    extra_actions = 0
    extra_buys = 1
    extra_coppers = 0

    def council_room_action(self):
        other_players = [player for player in self.game.players if player is not self.owner]
        print(f'Other players ({other_players}) each draw a card.')
        for player in other_players:
            player.draw(1)

    def play(self):
        self.council_room_action()


class Festival(ActionCard):
    name = 'Festival'
    cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+2 Actions',
            '+1 Buy',
            '+2 $'
        ]
    )

    extra_cards = 0
    extra_actions = 2
    extra_buys = 1
    extra_coppers = 2

    def festival_action(self):
        pass

    def play(self):
        self.festival_action()


class Laboratory(ActionCard):
    name = 'Laboratory'
    cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+2 Cards',
            '+1 Action',
        ]
    )

    extra_cards = 2
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def laboratory_action(self):
        pass

    def play(self):
        self.laboratory_action()


class Library(ActionCard):
    name = 'Library'
    cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = 'Draw until you have 7 cards in hand, skipping any Action cards you choose to; set those aside, discarding them afterwards.'

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def library_action(self):
        # TODO: Implement Library
        pass

    def play(self):
        self.library_action()


class Market(ActionCard):
    name = 'Market'
    cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Card',
            '+1 Action',
            '+1 Buy',
            '+1 $'
        ]
    )

    extra_cards = 1
    extra_actions = 1
    extra_buys = 1
    extra_coppers = 1

    def market_action(self):
        pass

    def play(self):
        self.market_action()


class Mine(ActionCard):
    name = 'Mine'
    cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = 'You may trash a Treasure from your hand. Gain a Treasure to your hand costing up to $3 more than it.'

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def mine_action(self):
        # TODO: Implement Mine
        pass

    def play(self):
        self.mine_action()


class Sentry(ActionCard):
    name = 'Sentry'
    cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Card',
            '+1 Action',
            'Look at the top 2 cards of your deck. Trash and/or discard any number of them. Put the rest back on top in any order.'
        ]
    )

    extra_cards = 1
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def sentry_action(self):
        # TODO: Implement Sentry
        pass

    def play(self):
        self.sentry_action()


class Witch(ActionCard):
    name = 'Witch'
    cost = 5
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = '\n'.join(
        [
            '+2 Cards',
            'Each other player gains a Curse.'
        ]
    )

    extra_cards = 2
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def witch_action(self):
        # TODO: Implement Witch
        pass

    def play(self):
        self.witch_action()


class Artisan(ActionCard):
    name = 'Artisan'
    cost = 6
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            'Gain a card to your hand costing up to 5 $.',
            'Put a card from your hand onto your deck.'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def artisan_action(self):
        # TODO: Implement Artisan
        pass

    def play(self):
        self.artisan_action()


class Chancellor(ActionCard):
    name = 'Chancellor'
    cost = 3
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+2 $',
            'You may immediately put your deck into your discard pile.'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 2

    def chancellor_action(self):
        # TODO: Implement Chancellor
        pass

    def play(self):
        self.chancellor_action()


class Woodcutter(ActionCard):
    name = 'Woodcutter'
    cost = 3
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Buy',
            '+2 $'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 1
    extra_coppers = 2

    def woodcutter_action(self):
        pass

    def play(self):
        self.woodcutter_action()


class Feast(ActionCard):
    name = 'Feast'
    cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            'Trash this card.',
            'Gain a card costing up to 5 $.'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def feast_action(self):
        # TODO: Implement Feast
        self.owner.trash_played_card(self)
        self.owner.turn.buy_phase.buy_without_side_effects(max_cost=5, force=True)

    def play(self):
        self.feast_action()


class Spy(ActionCard):
    name = 'Spy'
    cost = 4
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Card',
            '+1 Action',
            'Each player (including you) reveals the top card of his deck and either discards it or puts it back, your choice.'
        ]
    )

    extra_cards = 1
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def spy_action(self):
        # TODO: Implement Spy
        pass

    def play(self):
        self.spy_action()


class Thief(ActionCard):
    name = 'Thief'
    cost = 4
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = 'Each other player reveals the top 2 cards of his deck. If they revealed any Treasure cards, they trash one of them that you choose. You may gain any or all of these trashed cards. They discard the other revealed cards.'

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def thief_action(self):
        # TODO: Implement Thief
        pass

    def play(self):
        self.thief_action()


class Adventurer(ActionCard):
    name = 'Adventurer'
    cost = 6
    types = [CardType.ACTION]
    image_path = ''

    description = 'Reveal cards from your deck until you reveal 2 Treasure cards. Put those Treasure cards into your hand and discard the other revealed cards.'
    
    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def adventurer_action(self):
        revealed_treasures = []
        revealed_other_cards = []
        while len(revealed_treasures) < 2:
            card = self.owner.take_from_deck()
            if card is None:
                print('No cards left in deck.')
                break
            else:
                if CardType.TREASURE in card.types:
                    revealed_treasures.append(card)
                else:
                    revealed_other_cards.append(card)
        print(f'Revealed treasures: {revealed_treasures}. Putting these on top of deck.')
        self.owner.hand.extend(revealed_treasures)
        print(f'Other revealed cards: {revealed_other_cards}. Discarding these.')
        self.owner.discard_pile.extend(revealed_other_cards)

    def play(self):
        self.adventurer_action()


KINGDOM_CARDS = [
    Cellar,
    Chapel,
    Moat,
    Harbinger,
    # Merchant,
    Vassal,
    Village,
    Workshop,
    # Bureaucrat,
    Gardens,
    Militia,
    Moneylender,
    Poacher,
    Remodel,
    Smithy,
    ThroneRoom,
    # Bandit,
    CouncilRoom,
    Festival,
    Laboratory,
    # Library,
    Market,
    # Mine,
    # Sentry,
    # Witch,
    # Artisan,
    # Chancellor,
    Woodcutter,
    Feast,
    # Spy,
    # Thief,
    Adventurer
]