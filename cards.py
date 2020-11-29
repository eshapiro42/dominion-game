import math
from abc import ABCMeta, abstractmethod
from enum import Enum, auto
from turn import PreBuyHook


class CardType(Enum):
    TREASURE = auto()
    VICTORY = auto()
    CURSE = auto()
    ACTION = auto()
    REACTION = auto()
    ATTACK = auto()


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
    def attack(self):
        other_players = [player for player in self.game.players if player is not self.owner]
        immune_players = set()
        for player in other_players:
            # First, check if they have a reaction card in their hand
            if any(CardType.REACTION in card.types for card in player.hand):
                reaction_cards_in_hand = [card for card in player.hand if CardType.REACTION in card.types]
                reaction_card_classes_to_ignore = set() # We don't want to keep asking about reaction card classes that have already been played/ignored
                for reaction_card in reaction_cards_in_hand:
                    if type(reaction_card) in reaction_card_classes_to_ignore:
                        continue
                    else:
                        prompt = f'{player}: You have a Reaction card ({reaction_card.name}) in your hand. Play it?'
                        if player.interactions.choose_yes_or_no(prompt=prompt):
                            immune_players.add(player)
                        reaction_card_classes_to_ignore.add(type(reaction_card))
            # Now force non-immune players to reveal the top 2 cards of their deck
            if player in immune_players:
                print(f'{player} is immune to the effects.')
                continue
            else:
                self.attack_effect(self.owner, player)

    def play(self):
        if self.prompt is not None:
            print(self.prompt)
            print()
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

    def action(self):
        discarded_card_count = 0
        while True:
            prompt = 'Choose a card from your hand to discard.'
            card_to_discard = self.interactions.choose_card_from_hand(prompt=prompt, force=False)
            if card_to_discard is None:
                break
            else:
                discarded_card_count += 1
                self.owner.discard(card_to_discard)
        drawn_cards = self.owner.draw(discarded_card_count)
        print(f'+{discarded_card_count} cards --> {drawn_cards}\n')


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

    def action(self):
        for _ in range(4):
            prompt = 'Choose a card from your hand to trash.'
            card_to_trash = self.interactions.choose_card_from_hand(prompt=prompt, force=False)
            if card_to_trash is None:
                break
            else:
                self.owner.trash(card_to_trash)


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

    def action(self):
        pass

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

    def action(self):
        prompt = 'Choose a card from your discard pile to put onto your deck.'
        card = self.interactions.choose_card_from_discard_pile(prompt=prompt, force=False)
        if card is not None:
            self.owner.deck.append(card)
            self.owner.discard_pile.remove(card)


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


    class MerchantPreBuyHook(PreBuyHook):
        persistent = False

        def __call__(self):
            print(f'{self.player} played a Silver and gets +1 $ from his Merchant.')
            self.player.turn.coppers_remaining += 1


    def action(self):
        pre_buy_hook = self.MerchantPreBuyHook(self.owner)
        self.owner.turn.pre_buy_hooks[Silver].append(pre_buy_hook)


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

    def action(self):
        card = self.owner.deck.pop()
        self.owner.discard_pile.append(card)
        if CardType.ACTION in card.types:
            prompt = f'You revealed a {card.name}. Would you like to play it?'
            if self.interactions.choose_yes_or_no(prompt=prompt):
                self.owner.turn.action_phase.play_without_side_effects(card)


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

    def action(self):
        pass


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

    def action(self):
        self.owner.turn.buy_phase.buy_without_side_effects(max_cost=4, force=True)


class Bureaucrat(AttackCard):
    name = 'Bureaucrat'
    cost = 4
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = 'Gain a Silver onto your deck. Each other player reveals a Victory card from their hand and puts it onto their deck (or reveals a hand with no Victory cards).'
    prompt = 'Other players must reveal a Victory card from their hand and put it onto their deck (or reveal a hand with no Victory cards).'

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def attack_effect(self, attacker, player):
        # Check if the player has a Victory card in their hand
        if any(CardType.VICTORY in card.types for card in player.hand):
            # Player must choose a Victory card to put back onto their deck
            victory_cards = [card for card in player.hand if CardType.VICTORY in card.types]
            if len(set([type(card) for card in victory_cards])) == 1:
                # If there is only one type of Victory card, just use any
                card = victory_cards[0]
            else: 
                # If there is more than one type of Victory card, player must choose one
                prompt = f'{player}: choose a Victory card to put back onto your deck.'
                card = player.interactions.choose_from_options(prompt=prompt, options=victory_cards, force=True)
            print(f'{player} puts a {card} on top of their deck.')
            player.hand.remove(card)
            player.deck.append(card)
        else:
            # Player reveals a hand with no Victory cards
            print(f'{player} reveals a hand with no Victory cards: {player.hand}.')

    def action(self):
        # Gain a Silver and put onto deck
        silver = self.supply.draw(Silver)
        silver.owner = self.owner
        self.owner.deck.append(silver)


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


class Militia(AttackCard):
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
    prompt = 'Other players must discard down to 3 cards in their hands.'


    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 2

    def attack_effect(self, attacker, player):
        number_to_discard = len(player.hand) - 3
        print(f'{player} must discard {number_to_discard} cards.')
        for card_num in range(number_to_discard):
            prompt = f'{player}: Choose card {card_num + 1}/{number_to_discard} to discard.'
            card_to_discard = player.interactions.choose_card_from_hand(prompt=prompt, force=True)
            player.discard(card_to_discard)

    def action(self):
        pass


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

    def action(self):
        prompt = 'You may trash a Copper from your hand.'
        copper_to_trash = self.interactions.choose_specific_card_class_from_hand(prompt=prompt, force=False, card_class=Copper)
        if copper_to_trash is not None:
            self.owner.turn.coppers_remaining += 3
            print(f'+3 $ --> {self.owner.turn.coppers_remaining}\n')
            self.owner.trash(copper_to_trash)


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

    def action(self):
        number_to_discard = self.supply.num_empty_stacks
        if number_to_discard > 0:
            print(f'You must discard {number_to_discard} cards.\n')
            for num in range(number_to_discard):
                prompt = f'Choose card {num + 1}/{number_to_discard} to discard.'
                card_to_discard = self.interactions.choose_card_from_hand(prompt=prompt, force=True)
                if card_to_discard is not None:
                    self.owner.discard(card_to_discard)


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

    def action(self):
        prompt = 'Choose a card from your hand to trash.'
        card_to_trash = self.interactions.choose_card_from_hand(prompt=prompt, force=True)
        if card_to_trash is not None:
            self.owner.trash(card_to_trash)
            max_cost = card_to_trash.cost + 2
            self.owner.turn.buy_phase.buy_without_side_effects(max_cost=max_cost, force=True)


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

    def action(self):
        pass


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

    def action(self):
        prompt = 'Select an action card to play twice.'
        card = self.interactions.choose_specific_card_type_from_hand(prompt=prompt, card_type=CardType.ACTION)
        if card is not None:
            # Playing the card should not use any actions, so we use a special method
            # The first time, add the card to the played cards area
            self.owner.play(card)
            print(f'Playing {card.name} for the first time.\n')
            self.owner.turn.action_phase.play_without_side_effects(card)
            print(f'Playing {card.name} for the second time.\n')
            self.owner.turn.action_phase.play_without_side_effects(card)


class Bandit(AttackCard):
    name = 'Bandit'
    cost = 5
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = 'Gain a Gold. Each other player reveals the top 2 cards of their deck, trashes a revealed Treasure other than Copper, and discards the rest.'
    prompt = 'Each other player must reveal the top 2 cards of their deck, trash a revealed Treasure other than Copper, and discard the rest.'

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def attack_effect(self, attacker, player):
        trashable_cards = []
        other_cards = []
        for _ in range(2):
            card = player.take_from_deck()
            if CardType.TREASURE in card.types and type(card) != Copper:
                trashable_cards.append(card)
            else:
                other_cards.append(card)
        revealed_cards = trashable_cards + other_cards
        print(f'{player} revealed a {revealed_cards[0]} and a {revealed_cards[1]}.')
        if not trashable_cards:
            # The player discards both cards
            print(f'{player} discards a {other_cards[0]} and a {other_cards[1]}.')
            player.discard_pile.extend(other_cards)
        elif len(trashable_cards) == 1:
            # The player trashes the only possible card
            card_to_trash = trashable_cards[0]
            card_to_discard = other_cards[0]
            print(f'{player} trashes a {card_to_trash} and discards a {card_to_discard}.')
            self.supply.trash(card_to_trash)
            player.discard_pile.append(card_to_discard)
        elif len(trashable_cards) == 2 and type(trashable_cards[0]) == type(trashable_cards[1]):
            # The player trashes either card since they're the same
            card_to_trash = trashable_cards[0]
            card_to_discard = trashable_cards[1]
            print(f'{player} trashes a {card_to_trash} and discards a {card_to_discard}.')
            self.supply.trash(card_to_trash)
            player.discard_pile.append(card_to_discard)
        else:
            # The player must choose a card to trash
            prompt = f'{player}: You must choose a card to trash.'
            card_to_trash = player.interactions.choose_from_options(prompt=prompt, options=trashable_cards, force=True)
            trashable_cards.remove(card_to_trash)
            card_to_discard = trashable_cards[0]
            print(f'{player} trashes a {card_to_trash} and discards a {card_to_discard}.')
            self.supply.trash(card_to_trash)
            player.discard_pile.append(card_to_discard)

    def action(self):
        print(f'{self.owner} gained a Gold.')
        self.owner.gain(Gold)


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

    def action(self):
        other_players = [player for player in self.game.players if player is not self.owner]
        print(f'Other players ({other_players}) each draw a card.')
        for player in other_players:
            player.draw(1)


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

    def action(self):
        pass


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

    def action(self):
        pass


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

    def action(self):
        while len(self.owner.hand) < 7:
            card_drawn = self.owner.take_from_deck()
            print(f'You drew a {card_drawn}.')
            if CardType.ACTION in card_drawn.types:
                prompt = "It's an action card. Would you like to skip and discard it?"
                if self.interactions.choose_yes_or_no(prompt=prompt):
                    self.owner.discard_pile.append(card_drawn)
                else:
                    print('Adding it to your hand.')
                    self.owner.hand.append(card_drawn)
            else:
                print('Adding it to your hand.')
                self.owner.hand.append(card_drawn)


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

    def action(self):
        pass


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

    def action(self):
        prompt = 'You may choose a Treasure card from your hand to trash.'
        card_to_trash = self.interactions.choose_specific_card_type_from_hand(prompt=prompt, card_type=CardType.TREASURE)
        if card_to_trash is None:
            print('You did not trash anything.')
        else:
            self.owner.trash(card_to_trash)
            max_cost = card_to_trash.cost + 3
            prompt = f'Choose a Treasure card costing up to {max_cost} $ to gain to your hand.'
            card_to_gain = self.interactions.choose_specific_card_type_from_supply(prompt=prompt, max_cost=max_cost, card_type=CardType.TREASURE, force=True)
            self.owner.gain_to_hand(card_to_gain)
            print(f'{self.owner} bought a {card_to_gain.name}')


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

    def action(self):
        cards_kept = []
        # Look at the top 2 cards of the deck and decide what to do with them
        for card_num in range(2):
            card = self.owner.take_from_deck()
            prompt = f'You revealed a {card}. What would you like to do with it?'
            options = ['Trash', 'Discard', 'Return to deck']
            choice = self.interactions.choose_from_options(prompt=prompt, options=list(options), force=True)
            print(f'You chose {choice}')
            if choice == 'Trash':
                print('Trashing it.')
                self.supply.trash(card)
            elif choice == 'Discard':
                print('Discarding it.')
                self.owner.discard_pile.append(card)
            elif choice == 'Return to deck':
                print('Setting aside to return to deck.')
                cards_kept.append(card)
        print(f'Cards kept: {cards_kept}.')
        if len(cards_kept) == 1:
            # If one card was kept, put it back on top of the deck
            card_kept = cards_kept[0]
            self.owner.deck.append(card_kept)
        elif len(cards_kept) == 2:
            # If more than Put the kept cards back on top in the desired order
            prompt = 'You must return these cards to the top of your deck. Which card would you like to be on top?'
            top_card = self.interactions.choose_from_options(prompt=prompt, options=cards_kept, force=True)
            cards_kept.remove(top_card)
            bottom_card = cards_kept[0]
            self.owner.deck.append(bottom_card)
            self.owner.deck.append(top_card)


class Witch(AttackCard):
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
    prompt = 'Each other player gains a Curse.'

    extra_cards = 2
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def effect(self, attacker, player):
        player.gain(Curse)
        print(f'{player} gained a Curse')


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

    def action(self):
        card_class = choose_card_class_from_supply(max_cost=5, force=True)
        self.owner.gain_to_hand(card_class)


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

    def action(self):
        prompt = 'Would you like to put your deck onto your discard pile?'
        if self.interactions.choose_yes_or_no(prompt):
            self.owner.deck.extend(self.owner.discard_pile)


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

    def action(self):
        pass


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

    def action(self):
        self.owner.trash_played_card(self)
        self.owner.turn.buy_phase.buy_without_side_effects(max_cost=5, force=True)


class Spy(AttackCard):
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

    def reveal_top_card_and_discard_or_replace(self, revealer, chooser):
        # Revealer reveals a card
        card = revealer.take_from_deck()
        # Then the chooser makes a choice
        options = ['Discard', 'Return to deck']
        if revealer == chooser:
            prompt = f'{chooser}: You revealed a {card}. What would you to do with it?'
        else:
            prompt = f'{chooser}: {revealer} revealed a {card}. What would you like them to do with it?'
        choice = chooser.interactions.choose_from_options(prompt=prompt, options=options, force=True)
        if choice == 'Discard':
            revealer.discard_pile.append(card)
            print(f'{revealer} discarded a {card}.')
        elif choice == 'Return to deck':
            revealer.deck.append(card)
            print(f'{revealer} returned the {card} to his deck.')

    def attack_effect(self, attacker, player):
        self.reveal_top_card_and_discard_or_replace(revealer=player, chooser=attacker)

    def action(self):
        self.reveal_top_card_and_discard_or_replace(revealer=self.owner, chooser=self.owner)

    @property
    def prompt(self):
         return f"Each other player reveals the top card of his deck and either discards it or puts it back, {self.owner}'s choice."


class Thief(AttackCard):
    name = 'Thief'
    cost = 4
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = '\n'.join(
        [
            'Each other player reveals the top 2 cards of his deck. If they revealed any Treasure cards, they trash one of them that you choose.',
            'You may gain any or all of these trashed cards. They discard the other revealed cards.'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def attack_effect(self, attacker, player):
        # Player reveals two cards
        revealed_cards = []
        for _ in range(2):
            card = player.take_from_deck()
            revealed_cards.append(card)
        print(f'{player} revealed a {revealed_cards[0]} and a {revealed_cards[1]}.')
        # Check if they revealed any treasure cards
        if any(CardType.TREASURE in card.types for card in revealed_cards):
            treasures = [card for card in revealed_cards if CardType.TREASURE in card.types]
            if len(set(type(card) for card in treasures)) == 1:
                # If there's only one type of treasure, just trash it automatically
                if len(treasures) == 1:
                    card_to_trash = treasures[0]
                    revealed_cards.remove(card_to_trash)
                    card_to_discard = revealed_cards[0]
                elif len(treasures) == 2:
                    card_to_trash = treasures[0]
                    card_to_discard = treasures[1]
            else:
                # Otherwise, the attacker chooses which treasure to trash
                prompt = f'{attacker}: Choose a Treasure that {player} revealed to trash.'
                card_to_trash = player.interactions.choose_from_options(prompt=prompt, options=treasures, force=True)
                treasures.remove(card_to_trash)
                card_to_discard = treasures[0]
            print(f'{player} trashed a {card_to_trash} and discarded a {card_to_discard}')
            # Allow the attacker to gain the trashed card
            prompt = f'{attacker}: Would you like to gain the trashed {card_to_trash}?'
            if attacker.interactions.choose_yes_or_no(prompt=prompt):
                attacker.discard_pile.append(card_to_trash)
                print(f'{attacker} gained the trashed {card_to_trash}.')
            else:
                self.supply.trash(card_to_trash)
        else:
            # If no Treasures were revealed, they discard both revealed cards
            player.discard_pile.extend(revealed_cards)

    @property
    def prompt(self):
        return f'Each other player reveals the top 2 cards of his deck. If they revealed any Treasure cards, they trash one of them that {self.owner} chooses. {self.owner} may gain any or all of these trashed cards. They discard the other revealed cards.'

    def action(self):
        pass


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

    def action(self):
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


KINGDOM_CARDS = [
    Cellar,
    Chapel,
    Moat,
    Harbinger,
    Merchant,
    Vassal,
    Village,
    Workshop,
    Bureaucrat,
    Gardens,
    Militia,
    Moneylender,
    Poacher,
    Remodel,
    Smithy,
    ThroneRoom,
    Bandit,
    CouncilRoom,
    Festival,
    Laboratory,
    Library,
    Market,
    Mine,
    Sentry,
    Witch,
    Artisan,
    Chancellor,
    Woodcutter,
    Feast,
    Spy,
    Thief,
    Adventurer
]