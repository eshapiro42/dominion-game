import math

from gevent import Greenlet, joinall

from .cards import CardType, Card, TreasureCard, ActionCard, AttackCard, ReactionCard, VictoryCard, CurseCard, ReactionType
from . import base_cards
from ..hooks import PreTurnHook
from ..grammar import a, s


# KINGDOM CARDS


class Hamlet(ActionCard):
    name = 'Hamlet'
    cost = 2
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # '+1 Card',
            # '+1 Action',
            'You may discard a card for +1 Action.',
            'You may discard a card for +1 Buy.',
        ]
    )

    extra_cards = 1
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        # You may discard a card for +1 Action
        prompt = f'Would you like to discard a card for +1 Action?'
        if self.owner.interactions.choose_yes_or_no(prompt):
            prompt = f'Which card would you like to discard for +1 Action?'
            if (card := self.owner.interactions.choose_card_from_hand(prompt, force=False)) is not None:
                self.owner.discard(card)
                self.owner.turn.plus_actions(1)
                self.game.broadcast(f"{self.owner.name} discarded {card.name} for +1 Action.")
        # You may discard a card for +1 Buy
        prompt = f'Would you like to discard a card for +1 Buy?'
        if self.owner.interactions.choose_yes_or_no(prompt):
            prompt = f'Which card would you like to discard for +1 Buy?'
            if (card := self.owner.interactions.choose_card_from_hand(prompt, force=False)) is not None:
                self.owner.discard(card)
                self.owner.turn.plus_buys(1)
                self.game.broadcast(f"{self.owner.name} discarded {card.name} for +1 Buy.")


class FortuneTeller(AttackCard):
    name = 'Fortune Teller'
    cost = 3
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = '\n'.join(
        [
            # '+2 $',
            'Each other player reveals cards from the top of their deck until they reveal a Victory card or a Curse. They put it on top and discard the rest.',
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 2

    allow_simultaneous_reactions = True

    @property
    def prompt(self):
        return f'Each other player reveals cards from the top of their deck until they reveal a Victory card or a Curse. They put it on top and discard the rest.'

    def attack_effect(self, attacker, player):
        cards_to_discard = []
        revealed_victory_or_curse = None
        # Reveal cards from the top of your deck until you reveal a Victory card or a Curse
        while True:
            if (card := player.take_from_deck()) is None:
                self.game.broadcast(f'{player} has no more cards to draw from.')
                break
            if CardType.VICTORY in card.types or CardType.CURSE in card.types:
                revealed_victory_or_curse = card
                break
            cards_to_discard.append(card)
        # Put it on top of your deck
        if revealed_victory_or_curse is not None:
            player.deck.append(revealed_victory_or_curse)
            self.game.broadcast(f"{player} put {a(revealed_victory_or_curse.name)} on top of their deck.")
        # Discard the rest
        if cards_to_discard:
            player.discard_pile.extend(cards_to_discard)
            self.game.broadcast(f"{player} discarded {Card.group_and_sort_by_cost(cards_to_discard)}.")

    def action(self):
        pass


class Menagerie(ActionCard):
    name = 'Menagerie'
    cost = 3
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # '+1 Action',
            'Reveal your hand. If the revealed cards all have different names, +3 Cards. Otherwise, +1 Card.',
        ]
    )

    extra_cards = 0
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        # Reveal your hand
        self.game.broadcast(f"{self.owner.name} revealed their hand: {Card.group_and_sort_by_cost(self.owner.hand)}.")
        if len(set([card.name for card in self.owner.hand])) == len(self.owner.hand):
            # The revealed cards all have different names
            self.owner.draw(3)
        else:
            # There is at least one duplicate
            self.owner.draw(1)


class FarmingVillage(ActionCard):
    name = 'Farming Village'
    cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # '+2 Actions',
            'Reveal cards from your deck until you reveal a Treasure or Action card. Put that card into your hand and discard the rest.',
        ]
    )

    extra_cards = 0
    extra_actions = 2
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        cards_to_discard = []
        revealed_treasure_or_action = None
        # Reveal cards from your deck until you reveal a Treasure or Action card
        while True:
            if (card := self.owner.take_from_deck()) is None:
                self.game.broadcast(f'{self.owner} has no more cards to draw from.')
                break
            if CardType.TREASURE in card.types or CardType.ACTION in card.types:
                revealed_treasure_or_action = card
                break
            cards_to_discard.append(card)
        # Put it into your hand
        if revealed_treasure_or_action is not None:
            self.owner.hand.append(revealed_treasure_or_action)
            self.game.broadcast(f"{self.owner} put {a(revealed_treasure_or_action.name)} into their hand.")
        # Discard the rest
        if cards_to_discard:
            self.owner.discard_pile.extend(cards_to_discard)
            self.game.broadcast(f"{self.owner} discarded {Card.group_and_sort_by_cost(cards_to_discard)}.")


class HorseTraders(ReactionCard):
    name = 'Horse Traders'
    pluralized = 'Horse Traders'
    cost = 4
    types = [CardType.ACTION, CardType.REACTION]
    image_path = ''

    description = '\n'.join(
        [
            # '+1 Buy',
            # '+3 $',
            'Discard 2 cards.',
            'When another player plays an Attack card, you may first set this aside from your hand. If you do, then at the start of your next turn, +1 Card and return this to your hand.',
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 1
    extra_coppers = 3

    def action(self):
        # Discard 2 cards
        prompt = "You played a Horse Traders. Select 2 cards to discard."
        if (cards := self.owner.interactions.choose_cards_from_hand(prompt, force=True, max_cards=2)) is not None:
            for card in cards:
                self.owner.discard(card, message=False)
            self.game.broadcast(f"{self.owner} discarded {Card.group_and_sort_by_cost(cards)}.")
        else:
            self.game.broadcast(f"{self.owner} did not have any cards to discard.")

    @property
    def can_react(self):
        return True

    class HorseTradersPreTurnHook(PreTurnHook):
        persistent = False

        def __init__(self, game, player, set_aside_card: Card):
            super().__init__(game, player)
            self.set_aside_card = set_aside_card

        def __call__(self):
            self.game.broadcast(f"{self.player} draws an additional card from the Horse Traders they set aside.")
            self.player.draw(1)
            self.game.broadcast(f"{self.player} returns the Horse Traders they set aside to their hand.")
            self.player.hand.append(self.set_aside_card)

    def react(self):
        prompt = "Would you like to set this Horse Traders aside from your hand? If you do, then at the start of your next turn, you will return it to your hand and get +1 Card."
        if self.owner.interactions.choose_yes_or_no(prompt):
            self.owner.hand.remove(self)
            self.game.broadcast(f"{self.owner} set a Horse Traders aside from their hand for next turn.")
            pre_turn_hook = self.HorseTradersPreTurnHook(game=self.game, player=self.owner, set_aside_card=self)
            self.game.add_pre_turn_hook(pre_turn_hook)
        return None, False # When set aside, it is not in play or in your hand and cannot be further revealed when Attacked


class Remake(ActionCard):
    name = 'Remake'
    cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            'Do this twice: Trash a card from your hand, then gain a card costing exactly 1 $ more than it.',
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        for num in ['first', 'second']:
            prompt = f'You played a Remake. Choose the {num} card from your hand to trash.'
            card_to_trash = self.interactions.choose_card_from_hand(prompt, force=True)
            if card_to_trash is not None:
                self.owner.trash(card_to_trash)
                cost = card_to_trash.cost + 1
                prompt = f'You trashed {a(card_to_trash.name)} with your Remake. Choose a card costing exactly {cost} $ to gain.'
                card_class_to_gain = self.interactions.choose_card_class_from_supply(prompt, cost, force=True, exact_cost=True)
                if card_class_to_gain is not None:
                    self.owner.gain(card_class_to_gain)


class Tournament(ActionCard):
    name = 'Tournament'
    cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # '+1 Action',
            'Each player may reveal a Province from their hand. If you do, discard it and gain any Prize (from the Prize pile) or a Duchy, onto your deck. If no-one else does, +1 Card and +1 $.',
        ]
    )

    extra_cards = 0
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        def player_reaction(player):
            nonlocal owner_revealed_province
            nonlocal other_revealed_province
            if player == self.owner:
                # You may reveal a Province from your hand
                prompt = f'You played a Tournament. Would you like to reveal a Province from your hand to gain a Prize (from the Prize pile) or a Duchy, onto your deck? If you do, you will discard the Province.'
                if (
                    not any(isinstance(card, base_cards.Province) for card in self.owner.hand)
                    or
                    not self.owner.interactions.choose_yes_or_no(prompt)
                ):
                    return
                owner_revealed_province = True
                self.game.broadcast(f"{self.owner} revealed a Province from their hand.")
            else:
                prompt = f'{self.owner} played a Tournament. Would you like to reveal a Province from your hand to prevent {self.owner} from getting +1 Card and +1 $?'
                if (
                    not any(isinstance(card, base_cards.Province) for card in player.hand)
                    or
                    not player.interactions.choose_yes_or_no(prompt)
                ):
                    return
                other_revealed_province = True
                self.game.broadcast(f"{player} revealed a Province from their hand.")

        greenlets = []
        owner_revealed_province = False
        other_revealed_province = False
        for player in self.game.turn_order:
            # Simultaneous reactions are only allowed if they are enabled for the game
            if self.game.allow_simultaneous_reactions:
                greenlets.append(Greenlet.spawn(player_reaction, player))
            else:
                player_reaction(player)
        joinall(greenlets)
        if owner_revealed_province:
            # Find a Province in your hand
            for card in self.owner.hand:
                if isinstance(card, base_cards.Province):
                    break
            # Discard the Province
            self.owner.discard(card)
            # Find the Cornucopia expansion instance
            cornucopia_expansion_instance = None
            for expansion_instance in self.supply.customization.expansions:
                if expansion_instance.name == 'Cornucopia':
                    cornucopia_expansion_instance = expansion_instance
                    break
            prizes = cornucopia_expansion_instance.prizes
            # Gain a Prize or a Duchy onto your deck
            num_prizes_remaining = len(prizes)
            num_duchies_remaining = self.game.supply.card_stacks[base_cards.Duchy].cards_remaining
            prompt = f'You played a Tournament and discarded a Province. What would you like to gain onto your deck?' 
            options = [
                f"A Prize ({num_prizes_remaining} remaining)",
                f"A Duchy ({num_duchies_remaining} remaining)",
            ]
            choice = self.owner.interactions.choose_from_options(prompt, options, force=True)
            if choice == f"A Prize ({num_prizes_remaining} remaining)":
                prompt = f"You played a Tournament and discarded a Province. Choose a card from the Prize Pile to gain onto your deck."
                card_to_gain = self.owner.interactions.choose_card_from_prizes(prompt)
                if card_to_gain is not None:
                    prizes.remove(card_to_gain)
                    self.owner.gain_to_deck(type(card_to_gain), from_supply=False)
                    self.game.broadcast(f"{self.owner} gained {a(card_to_gain.name)} from the Prize Pile onto their deck.")
            else:
                self.owner.gain_to_deck(base_cards.Duchy)
        if not other_revealed_province:
            # +1 Card and +1 $
            self.owner.draw(1)
            self.game.current_turn.plus_coppers(1)


class Harvest(ActionCard):
    name = 'Harvest'
    cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            'Reveal the top 4 cards of your deck, then discard them. +1 $ per differently named card revealed.',
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        # Reveal the top 4 cards of your deck and discard them
        revealed_cards = []
        for _ in range(4):
            card = self.owner.take_from_deck()
            if card is None:
                break
            self.owner.discard_pile.append(card)
            revealed_cards.append(card)
        # Count the number of differently named cards revealed
        num_differently_named_cards = len(set([card.name for card in revealed_cards]))
        self.game.broadcast(f"{self.owner} played a Harvest and revealed {Card.group_and_sort_by_cost(revealed_cards)} ({s(num_differently_named_cards, 'differently named card')}).")
        self.game.current_turn.plus_coppers(num_differently_named_cards)


class HornOfPlenty(TreasureCard):
    name = 'Horn of Plenty'
    pluralized = 'Horns of Plenty'
    cost = 5
    types = [CardType.TREASURE]
    image_path = ''

    value = 0

    description = '\n'.join(
        [
            "When you play this, gain a card costing up to $1 per differently named card you have in play (counting this). If it's a Victory card, trash this.",
        ]
    )

    def play(self):
        # Count the number of differently named cards in play (counting this)
        num_differently_named_cards = len(set([card.name for card in self.owner.played_cards]))
        # Gain a card costing up to that amount
        self.game.broadcast(f"{self.owner} may gain a card costing up to {num_differently_named_cards} $ from their Horn of Plenty.")
        prompt = f"Choose a card costing up to {num_differently_named_cards} to gain from your Horn of Plenty."
        card_class_to_gain = self.owner.interactions.choose_card_class_from_supply(prompt, max_cost=num_differently_named_cards, force=True)
        if card_class_to_gain is not None:
            self.owner.gain(card_class_to_gain)
        # If the gained card is a Victory card, trash this card
        if CardType.VICTORY in card_class_to_gain.types:
            self.game.broadcast(f"{self.owner} trashed a Horn of Plenty because they used it to gain a Victory card.")
            self.owner.trash_played_card(self, message=False)


class HuntingParty(ActionCard):
    name = 'Hunting Party'
    pluralized = 'Hunting Parties'
    cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # '+1 Card',
            # '+1 Action',
            "Reveal your hand. Reveal cards from your deck until you reveal one that isn't a copy of one in your hand. Put it into your hand and discard the rest.",
        ]
    )

    extra_cards = 1
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        # Reveal your hand
        self.game.broadcast(f"{self.owner} revealed their hand: {Card.group_and_sort_by_cost(self.owner.hand)}.")
        # Reveal cards from your deck until you reveal one that isn't a copy of one in your hand
        revealed_cards = []
        unique_revealed_card = None
        while True:
            revealed_card = self.owner.take_from_deck()
            print(revealed_card)
            if revealed_card is None:
                self.game.broadcast(f'{self.owner} had no cards left to draw from and did not put anything into their hand.')
                break
            # Check whether the card is a copy of one in your hand
            if any(card.name == revealed_card.name for card in self.owner.hand):
                revealed_cards.append(revealed_card)
            else:
                unique_revealed_card = revealed_card
                break
        # Put it into your hand (the rest have already been discarded but that has not yet been broadcasted)
        if revealed_cards:
            for card in revealed_cards:
                self.owner.discard_pile.append(card)
            self.game.broadcast(f"{self.owner} revealed and discarded {Card.group_and_sort_by_cost(revealed_cards)} with their Hunting Party.")
        if unique_revealed_card is not None:
            self.owner.hand.append(unique_revealed_card)
            self.game.broadcast(f"{self.owner} put {a(unique_revealed_card.name)} into their hand with their Hunting Party.")


class Jester(AttackCard):
    name = 'Jester'
    cost = 5
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = '\n'.join(
        [
            # '+2 $',
            "Each other player discards the top card of their deck. If it's a Victory card they gain a Curse; otherwise they gain a copy of the discarded card or you do, your choice.",
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 2

    allow_simultaneous_reactions = False # If only one Curse is left in the Supply, it is important that this is resolved in turn order
    
    @property
    def prompt(self):
        return f"Each other player discards the top card of their deck. If it's a Victory card they gain a Curse; otherwise they gain a copy of the discarded card or {self.owner} does, {self.owner}'s choice."

    def action(self):
        pass
        
    def attack_effect(self, attacker, player):
        # Discard the top card of your deck
        card = player.take_from_deck()
        if card is None:
            # Players with no cards are unaffected
            self.game.broadcast(f"{player} has no cards left to draw from and is unaffected by {attacker}'s Jester.")
            return
        player.discard_pile.append(card)
        self.game.broadcast(f"{player} discarded {a(card)} via {attacker}'s Jester.")
        if CardType.VICTORY in card.types:
            # If the card is a Victory card, gain a Curse
            player.gain(base_cards.Curse)
            return
        # Otherwise, they gain a copy of the discarded card or the attacker does, the attacker's choice
        card_class_to_gain = type(card)
        if card_class_to_gain not in self.supply.card_stacks or self.supply.card_stacks[card_class_to_gain].is_empty:
            # If the card is not in the Supply (e.g., a Prize) or its Supply pile is empty, no copy is gained
            self.game.broadcast(f"There are no remaining copies of {card.name} to be gained.")
            return
        prompt = f'You played a Jester and {player} revealed and discarded a {card.name} from their deck. Who would you like to gain a copy of the {card.name}?'
        options = [
            f'Me ({attacker})',
            f'{player}',
        ]
        choice = attacker.interactions.choose_from_options(prompt, options, force=True)
        if choice == options[0]:
            # The attacker gains a copy of the card
            attacker.gain(card_class_to_gain)
        else:
            # The attacked player gains a copy of the card
            player.gain(card_class_to_gain)


class Fairgrounds(VictoryCard):
    name = 'Fairgrounds'
    pluralized = 'Fairgrounds'
    cost = 6
    types = [CardType.VICTORY]
    image_path = ''

    description = 'Worth 2 victory points per 5 differently named cards you have (round down).'

    @property
    def points(self):
        num_differently_named_cards = len(set([card.name for card in self.owner.all_cards]))
        return 2 * math.floor(num_differently_named_cards / 5)


KINGDOM_CARDS = [
    Hamlet,
    FortuneTeller,
    Menagerie,
    FarmingVillage,
    HorseTraders,
    Remake,
    Tournament,
    # YoungWitch,
    Harvest,
    HornOfPlenty,
    HuntingParty,
    Jester,
    Fairgrounds,
]


# PRIZES


class BagOfGold(ActionCard):
    name = 'Bag of Gold' 
    pluralized = 'Bags of Gold' # Not really needed since by definition there is only one in the game
    cost = 0
    types = [CardType.ACTION, CardType.PRIZE]
    image_path = ''

    description = '\n'.join(
        [
            # '+1 Action',
            'Gain a Gold onto your deck.',
            '<i>(This is not in the Supply.)</i>',
        ]
    )

    extra_cards = 0
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        self.owner.gain_to_deck(base_cards.Gold)


class Diadem(TreasureCard):
    name = 'Diadem'
    cost = 0
    types = [CardType.TREASURE, CardType.PRIZE]
    image_path = ''

    value = 2

    description = '\n'.join(
        [
            '<b>+2 $</b>', # Must be explicitly stated since this is a Treasure card
            'When you play this, +1 $ per unused Action you have (Action, not Action card).',
            '<i>(This is not in the Supply.)</i>',
        ]
    )

    def play(self):
        if (num_unused_actions := self.game.current_turn.actions_remaining) > 0:
            self.game.broadcast(f"{self.owner} gets an additional {num_unused_actions} $ from their Diadem.")
            self.game.current_turn.plus_coppers(num_unused_actions, message=False)


class Followers(AttackCard):
    name = 'Followers'
    pluralized = 'Followers' # Not really needed since by definition there is only one in the game
    cost = 0
    types = [CardType.ACTION, CardType.ATTACK, CardType.PRIZE]
    image_path = ''

    description = '\n'.join(
        [
            # '+2 Cards',
            'Gain an Estate.',
            'Each other player gains a Curse and discards down to 3 cards in hand.',
            '<i>(This is not in the Supply.)</i>',
        ]
    )

    prompt = 'Each other player gains a Curse and discards down to 3 cards in hand.'

    extra_cards = 2
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    allow_simultaneous_reactions = False # If only one Curse is left in the Supply, it is important that this is resolved in turn order
    
    def action(self):
        # Gain an Estate
        self.owner.gain(base_cards.Estate)
        
    def attack_effect(self, attacker, player):
        # Gain a Curse
        player.gain(base_cards.Curse)
        # Discard down to 3 cards in hand
        number_to_discard = max(len(player.hand) - 3, 0)
        if number_to_discard == 0:
            self.game.broadcast(f"{player} only has {s(len(player.hand), 'card')} in their hand.")
            return
        self.game.broadcast(f"{player} must discard {s(number_to_discard, 'card')}.")
        prompt = f"{attacker} has played a Followers. Choose {s(number_to_discard, 'card')} to discard."
        cards_to_discard = player.interactions.choose_cards_from_hand(prompt=prompt, force=True, max_cards=number_to_discard)
        for card_to_discard in cards_to_discard:
            player.discard(card_to_discard)


class Princess(ActionCard):
    name = 'Princess'
    pluralized = 'Princesses' # Not really needed since by definition there is only one in the game
    cost = 0
    types = [CardType.ACTION, CardType.PRIZE]
    image_path = ''

    description = '\n'.join(
        [
            # '+1 Buy',
            'While this is in play, cards cost 2 $ less, but not less than 0 $.',
            '<i>(This is not in the Supply.)</i>',
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 1
    extra_coppers = 0

    def action(self):
        # Modify card costs
        for card_class in self.supply.card_stacks:
            self.supply.modify_cost(card_class, -2)


class TrustySteed(ActionCard):
    name = 'Trusty Steed'
    cost = 0
    types = [CardType.ACTION, CardType.PRIZE]
    image_path = ''

    description = '\n'.join(
        [
            'Choose two: +2 Cards; or +2 Actions; or +2 $; or gain 4 Silvers and put your deck into your discard pile. The choices must be different.',
            '<i>(This is not in the Supply.)</i>',
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        options = [
            '+2 Cards',
            '+2 Actions',
            '+2 $',
            'Gain 4 Silvers and put your deck into your discard pile',
        ]
        options_copy = options[:]
        # First, the choices are selected
        choices = []
        prompt = f'You played a Trusty Steed. Which would you like to choose first?'
        choice = self.interactions.choose_from_options(prompt, options, force=True)
        choices.append(choice)
        options.remove(choice) # The same option cannot be chosen again
        prompt = f'You played a Trusty Steed. Which would you like to choose second?'
        choice = self.interactions.choose_from_options(prompt, options, force=True)
        choices.append(choice)
        self.game.broadcast(f"{self.owner} chose: {', '.join(choices)}.")
        # Then the selected choices are executed in the order listed
        for option in options_copy:
            if option in choices:
                if option == '+2 Cards':
                    self.owner.draw(2)
                elif option == '+2 Actions':
                    self.owner.turn.plus_actions(2)
                elif option == '+2 $':
                    self.owner.turn.plus_coppers(2)
                elif option == 'Gain 4 Silvers and put your deck into your discard pile':
                    self.owner.gain(base_cards.Silver, quantity=4, message=False)
                    self.owner.discard_pile.extend(self.owner.deck)
                    self.owner.deck.clear()
                    self.game.broadcast(f"{self.owner} gained 4 Silvers and put their deck into their discard pile.")


PRIZES = [
    BagOfGold,
    Diadem,
    Followers,
    Princess,
    TrustySteed,
]