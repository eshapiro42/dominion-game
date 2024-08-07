import math
from .cards import Card, CardType, ReactionType, ActionCard, AttackCard, ReactionCard, VictoryCard
from .base_cards import Copper, Silver, Gold, Curse
from ..hooks import TreasureHook
from ..grammar import a, s


# KINGDOM CARDS


class Cellar(ActionCard):
    name = 'Cellar'
    _cost = 2
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # '+1 Action',
            'Discard any number of cards, then draw that many.'
        ]
    )

    extra_cards = 0
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        prompt = 'You played a Cellar. Choose any number of cards from your hand to discard. You will then draw that many cards.'
        cards_to_discard = self.interactions.choose_cards_from_hand(prompt=prompt, force=False, max_cards=None)
        if not cards_to_discard:
            self.game.broadcast(f'{self.owner} did not discard or draw any cards.')
            return
        for card_to_discard in cards_to_discard:
            self.owner.discard_from_hand(card_to_discard)
        self.owner.draw(len(cards_to_discard))


class Chapel(ActionCard):
    name = 'Chapel'
    _cost = 2
    types = [CardType.ACTION]
    image_path = ''

    description = 'Trash up to 4 cards from your hand.'

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        prompt = f"You played a Chapel. You may choose up to 4 cards from your hand to trash."
        cards_to_trash = self.interactions.choose_cards_from_hand(prompt=prompt, force=False, max_cards=4)
        if not cards_to_trash:
            self.game.broadcast(f'{self.owner} did not trash any cards.')
            return
        for card_to_trash in cards_to_trash:
            self.owner.trash(card_to_trash)


class Moat(ReactionCard):
    name = 'Moat'
    _cost = 2
    types = [CardType.ACTION, CardType.REACTION]
    image_path = ''

    description = '\n'.join(
        [
            # '+2 Cards',
            'When another player plays an Attack card, you may first reveal this from your hand, to be unaffected by it.'
        ]
    )

    extra_cards = 2
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    @property
    def reacts_to(self):
        return [ReactionType.ATTACK]

    def action(self):
        pass

    def react_to_attack(self):
        immune = True
        ignore_card_class_next_time = True
        return immune, ignore_card_class_next_time # Will make the owner immune to attacks and prevents the Moat from being played twice


class Harbinger(ActionCard):
    name = 'Harbinger'
    _cost = 3
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # '+1 Card',
            # '+1 Action',
            'Look through your discard pile. You may put a card from it onto your deck.'
        ]
    )

    extra_cards = 1
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        if not self.owner.discard_pile:
            self.game.broadcast(f'{self.owner} has no cards in their discard pile.')
            return
        prompt = 'You played a Harbinger. You may choose a card from your discard pile to put onto your deck.'
        card = self.interactions.choose_card_from_discard_pile(prompt=prompt, force=False)
        if card is not None:
            self.owner.deck.append(card)
            self.owner.discard_pile.remove(card)


class Merchant(ActionCard):
    name = 'Merchant'
    _cost = 3
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # '+1 Card',
            # '+1 Action',
            'The first time you play a Silver this turn, +1 $.'
        ]
    )
    
    extra_cards = 1
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0


    class MerchantTreasureHook(TreasureHook):
        persistent = False

        def __call__(self):
            player = self.game.current_turn.player
            self.game.broadcast(f'{player} played a Silver and gets +1 $ from their Merchant.')
            player.turn.coppers_remaining += 1


    def action(self):
        treasure_hook = self.MerchantTreasureHook(self.game)
        self.owner.turn.add_treasure_hook(treasure_hook, Silver)


class Vassal(ActionCard):
    name = 'Vassal'
    _cost = 3
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # '+2 $',
            "Discard the top card of your deck. If it's an Action card, you may play it."
        ]
    )
    
    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 2

    def action(self):
        card = self.owner.take_from_deck()
        if card is None:
            self.game.broadcast(f'{self.owner} has no cards left to draw from.')
            return
        self.owner.discard(card)
        if CardType.ACTION in card.types:
            prompt = f'You played a Vassal and revealed {a(card.name)}. Would you like to play it?'
            if self.interactions.choose_yes_or_no(prompt=prompt):
                self.owner.turn.action_phase.play_without_side_effects(card)


class Village(ActionCard):
    name = 'Village'
    _cost = 3
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # '+1 Card',
            # '+2 Actions'
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
    _cost = 3
    types = [CardType.ACTION]
    image_path = ''

    description = 'Gain a card costing up to 4 $.'

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        prompt = f'You played a Workshop. Select a card costing up to 4 $ to gain.'
        self.owner.turn.buy_phase.gain_without_side_effects(prompt, max_cost=4, force=True)


class Bureaucrat(AttackCard):
    name = 'Bureaucrat'
    _cost = 4
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = 'Gain a Silver onto your deck. Each other player reveals a Victory card from their hand and puts it onto their deck (or reveals a hand with no Victory cards).'
    prompt = 'Other players must reveal a Victory card from their hand and put it onto their deck (or reveal a hand with no Victory cards).'

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    allow_simultaneous_reactions = True

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
                prompt = f'{attacker} played a Bureaucrat. Choose a Victory card to put back onto your deck.'
                card = player.interactions.choose_specific_card_type_from_hand(prompt=prompt, card_type=CardType.VICTORY, force=True)
            self.game.broadcast(f'{player} put {a(card)} on top of their deck.')
            player.hand.remove(card)
            player.deck.append(card)
        else:
            # Player reveals a hand with no Victory cards
            self.game.broadcast(f"{player} revealed a hand with no Victory cards: {', '.join(map(str, player.hand))}.")

    def action(self):
        # Gain a Silver and put onto deck
        self.owner.gain_to_deck(Silver)


class Gardens(VictoryCard):
    name = 'Gardens'
    pluralized = 'Gardens'
    _cost = 4
    types = [CardType.VICTORY]
    image_path = ''

    description = 'Worth 1 victory point per 10 cards you have (round down).'

    @property
    def points(self):
        num_cards = len(self.owner.all_cards)
        return math.floor(num_cards / 10)


class Militia(AttackCard):
    name = 'Militia'
    _cost = 4
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = '\n'.join(
        [
            # '+2 $',
            'Each other player discards down to 3 cards in hand.'
        ]
    )
    prompt = 'Other players must discard down to 3 cards in their hands.'


    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 2

    allow_simultaneous_reactions = True

    def attack_effect(self, attacker, player):
        number_to_discard = max(len(player.hand) - 3, 0)
        if number_to_discard == 0:
            self.game.broadcast(f"{player} only has {s(len(player.hand), 'card')} in their hand.")
            return
        self.game.broadcast(f"{player} must discard {s(number_to_discard, 'card')}.")
        prompt = f"{attacker} has played a Militia. Choose {s(number_to_discard, 'card')} to discard."
        cards_to_discard = player.interactions.choose_cards_from_hand(prompt=prompt, force=True, max_cards=number_to_discard)
        for card_to_discard in cards_to_discard:
            player.discard_from_hand(card_to_discard)

    def action(self):
        pass


class Moneylender(ActionCard):
    name = 'Moneylender'
    _cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = 'You may trash a Copper from your hand for +3 $.'

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        prompt = 'You played a Moneylender. You may trash a Copper from your hand for +3 $.'
        copper_to_trash = self.interactions.choose_specific_card_class_from_hand(prompt=prompt, force=False, card_class=Copper)
        if copper_to_trash is not None:
            self.owner.trash(copper_to_trash)
            self.owner.turn.plus_coppers(3)


class Poacher(ActionCard):
    name = 'Poacher'
    _cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # '+1 Card',
            # '+1 Action',
            # '+1 $',
            'Discard a card per empty Supply pile.'
        ]
    )

    extra_cards = 1
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 1

    def action(self):
        number_to_discard = min(self.supply.num_empty_stacks, len(self.owner.hand))
        if number_to_discard > 0:
            self.game.broadcast(f"{self.owner} must discard {s(number_to_discard, 'card')}.")
            prompt = f"You played a Poacher and there are {number_to_discard} empty Supply piles. Choose {s(number_to_discard, 'card')} to discard."
            cards_to_discard = self.owner.interactions.choose_cards_from_hand(prompt=prompt, force=True, max_cards=number_to_discard)
            for card_to_discard in cards_to_discard:
                self.owner.discard_from_hand(card_to_discard)


class Remodel(ActionCard):
    name = 'Remodel'
    _cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = 'Trash a card from your hand. Gain a card costing up to 2 $ more than it.'

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        prompt = 'You played a Remodel. Choose a card from your hand to trash. You will then gain a card costing up to 2 $ more than it.'
        card_to_trash = self.interactions.choose_card_from_hand(prompt=prompt, force=True)
        if card_to_trash is not None:
            self.owner.trash(card_to_trash)
            max_cost = card_to_trash.cost + 2
            prompt = f'You played a Remodel and trashed a {card_to_trash.name}. Select a card costing up to {max_cost} $ to gain.'
            self.owner.turn.buy_phase.gain_without_side_effects(prompt, max_cost=max_cost, force=True)


class Smithy(ActionCard):
    name = 'Smithy'
    pluralized = 'Smithies'
    _cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # '+3 Cards'
        ]
    )

    extra_cards = 3
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        pass


class ThroneRoom(ActionCard):
    name = 'Throne Room'
    _cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = 'You may play an Action card from your hand twice.'

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        prompt = 'You played a Throne Room. Select an action card to play twice.'
        card = self.interactions.choose_specific_card_type_from_hand(prompt=prompt, card_type=CardType.ACTION)
        if card is not None:
            # Playing the card should not use any actions, so we use a special method
            # The first time, add the card to the played cards area
            self.owner.play(card)
            self.game.broadcast(f'{self.owner} plays {a(card.name)} for the first time, thanks to their Throne Room.')
            self.owner.turn.action_phase.play_without_side_effects(card)
            self.game.broadcast(f'{self.owner} plays {a(card.name)} for the second time, thanks to their Throne Room.')
            self.owner.turn.action_phase.play_without_side_effects(card)
        else:
            self.game.broadcast(f'{self.owner} has no other Actions cards to use with their Throne Room.')


class Bandit(AttackCard):
    name = 'Bandit'
    _cost = 5
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = 'Gain a Gold. Each other player reveals the top 2 cards of their deck, trashes a revealed Treasure other than Copper, and discards the rest.'
    prompt = 'Each other player must reveal the top 2 cards of their deck, trash a revealed Treasure other than Copper, and discard the rest.'

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    allow_simultaneous_reactions = True

    def attack_effect(self, attacker, player):
        trashable_cards = []
        other_cards = []
        for _ in range(2):
            card = player.take_from_deck()
            if card is None:
                self.game.broadcast(f'{player} has no more cards to draw from.')
                break
            else:
                self.game.broadcast(f'{player} revealed {a(card)}.')
                if CardType.TREASURE in card.types and not isinstance(card, Copper):
                    trashable_cards.append(card)
                else:
                    other_cards.append(card)
        revealed_cards = trashable_cards + other_cards
        if not trashable_cards:
            # The player discards both cards
            player.discard(other_cards)
        elif len(trashable_cards) == 1:
            # The player trashes the only possible card
            card_to_trash = trashable_cards[0]
            self.supply.trash(card_to_trash)
            self.game.broadcast(f'{player} trashed {a(card_to_trash)}.')
            try:
                card_to_discard = other_cards[0]
                player.discard(card_to_discard)
            except IndexError:
                pass
        elif len(trashable_cards) == 2 and type(trashable_cards[0]) == type(trashable_cards[1]):
            # The player trashes either card since they're the same
            card_to_trash = trashable_cards[0]
            card_to_discard = trashable_cards[1]
            self.game.broadcast(f'{player} trashed {a(card_to_trash)} and discarded {a(card_to_discard)}.')
            self.supply.trash(card_to_trash)
            player.discard(card_to_discard, message=False)
        else:
            # The player must choose a card to trash
            prompt = f'{attacker} played a Bandit. You must choose a card to trash.'
            card_to_trash = player.interactions.choose_from_options(prompt=prompt, options=trashable_cards, force=True)
            trashable_cards.remove(card_to_trash)
            card_to_discard = trashable_cards[0]
            self.game.broadcast(f'{player} trashed {a(card_to_trash)} and discarded {a(card_to_discard)}.')
            self.supply.trash(card_to_trash)
            player.discard(card_to_discard, message=False)

    def action(self):
        self.owner.gain(Gold)


class CouncilRoom(ActionCard):
    name = 'Council Room'
    _cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # '+4 Cards',
            # '+1 Buy',
            'Each other player draws a card.'
        ]
    )

    extra_cards = 4
    extra_actions = 0
    extra_buys = 1
    extra_coppers = 0

    def action(self):
        self.game.broadcast(f"Other players ({', '.join(map(str, self.owner.other_players))}) each draw a card.")
        for player in self.owner.other_players:
            player.draw(1)



class Festival(ActionCard):
    name = 'Festival'
    _cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # '+2 Actions',
            # '+1 Buy',
            # '+2 $'
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
    pluralized = 'Laboratories'
    _cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # '+2 Cards',
            # '+1 Action',
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
    pluralized = 'Libraries'
    _cost = 5
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
            if card_drawn is None:
                self.game.broadcast(f'{self.owner} has no more cards to draw from.')
                break
            self.interactions.send(f'You drew {a(card_drawn)}.')
            if CardType.ACTION in card_drawn.types:
                prompt = f"You drew {a(card_drawn)} with your Library. It's an Action card. You have {s(self.owner.turn.actions_remaining, 'action')} remaining. Would you like to keep it?"
                if self.interactions.choose_yes_or_no(prompt=prompt):
                    self.interactions.send('Adding it to your hand.')
                    self.owner.hand.append(card_drawn)
                    self.game.broadcast(f"+1 card → {s(len(self.owner.hand), 'card')} in hand.")
                else:
                    self.owner.discard(card_drawn)
            else:
                self.interactions.send('Adding it to your hand.')
                self.owner.hand.append(card_drawn)
                self.game.broadcast(f"+1 card → {s(len(self.owner.hand), 'card')} in hand.")


class Market(ActionCard):
    name = 'Market'
    _cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # '+1 Card',
            # '+1 Action',
            # '+1 Buy',
            # '+1 $'
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
    _cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = 'You may trash a Treasure from your hand. Gain a Treasure to your hand costing up to 3 $ more than it.'

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        prompt = 'You played a Mine. You may choose a Treasure card from your hand to trash. If you do, you will gain a Treasure card to your hand costing up to 3 $ more than the trashed card.'
        card_to_trash = self.interactions.choose_specific_card_type_from_hand(prompt=prompt, card_type=CardType.TREASURE)
        if card_to_trash is None:
            self.game.broadcast(f'{self.owner} did not trash anything.')
        else:
            self.owner.trash(card_to_trash)
            max_cost = card_to_trash.cost + 3
            prompt = f'Choose a Treasure card costing up to {max_cost} $ to gain to your hand.'
            card_class_to_gain = self.interactions.choose_specific_card_type_from_supply(prompt=prompt, max_cost=max_cost, card_type=CardType.TREASURE, force=True)
            self.owner.gain_to_hand(card_class_to_gain)


class Sentry(ActionCard):
    name = 'Sentry'
    pluralized = 'Sentries'
    _cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # '+1 Card',
            # '+1 Action',
            'Look at the top 2 cards of your deck. Trash and/or discard any number of them. Put the rest back on top in any order.'
        ]
    )

    extra_cards = 1
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        cards_kept = []
        cards_revealed = []
        # Look at the top 2 cards of the deck and decide what to do with them
        for card_num in range(2):
            card = self.owner.take_from_deck()
            if card is not None:
                cards_revealed.append(card)
            else:
                self.game.broadcast(f'{self.owner} has no more cards to draw from.')
        for card in cards_revealed:
            prompt = f'You revealed {a(card)} with your Sentry. What would you like to do with it?'
            options = ['Trash', 'Discard', 'Return to deck']
            choice = self.interactions.choose_from_options(prompt=prompt, options=options, force=True)
            if choice == 'Trash':
                self.game.broadcast(f'{self.owner} trashed {a(card)}.')
                self.supply.trash(card)
            elif choice == 'Discard':
                self.owner.discard(card)
            elif choice == 'Return to deck':
                self.interactions.send(f'You set the {card} aside to return to your deck.')
                cards_kept.append(card)
        if not cards_kept:
            return
        # If there is only one card (or card class) left, do not bother asking the player for the order
        if len(set([type(card) for card in cards_kept])) != 1:
            prompt = "You played a Sentry and must return these revealed cards to your deck in any order. (The last card you choose will be the top card of your deck.)"
            cards_kept = self.owner.interactions.choose_cards_from_list(prompt, cards_kept, force=True, max_cards=len(cards_kept), ordered=True)
        for card in cards_kept:
            self.owner.deck.append(card)
        self.owner.interactions.send(f"You put {Card.group_and_sort_by_cost(cards_kept)} back onto your deck.")
        self.game.broadcast(f"{self.owner.name} put {s(len(cards_kept), 'card')} back on top of their deck.")


class Witch(AttackCard):
    name = 'Witch'
    pluralized = 'Witches'
    _cost = 5
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = '\n'.join(
        [
            # '+2 Cards',
            'Each other player gains a Curse.'
        ]
    )
    prompt = 'Each other player gains a Curse.'

    extra_cards = 2
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    allow_simultaneous_reactions = False # If only one Curse is left in the Supply, it is important that this is resolved in turn order

    def attack_effect(self, attacker, player):
        player.gain(Curse)

    def action(self):
        pass


class Artisan(ActionCard):
    name = 'Artisan'
    _cost = 6
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
        prompt = 'You played an Artisan. Gain a card to your hand costing up to 5 $. You will then put a card from your hand onto your deck.'
        card_class = self.interactions.choose_card_class_from_supply(prompt=prompt, max_cost=5, force=True)
        self.owner.gain_to_hand(card_class)
        prompt = f'You played an Artisan and gained a {card_class.name}. Put a card from your hand onto your deck.'
        card = self.interactions.choose_card_from_hand(prompt=prompt, force=True)
        self.owner.hand.remove(card)
        self.owner.deck.append(card)
        self.interactions.send(f'You put {a(card)} from your hand onto your deck.')


class Chancellor(ActionCard):
    name = 'Chancellor'
    _cost = 3
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # '+2 $',
            'You may immediately put your deck into your discard pile.'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 2

    def action(self):
        prompt = f"You played a Chancellor. Would you like to put your deck ({s(len(self.owner.deck), 'card')}) into your discard pile ({s(len(self.owner.discard_pile), 'card')})?"
        if self.interactions.choose_yes_or_no(prompt):
            self.game.broadcast(f'{self.owner} put their deck into their discard pile.')
            self.owner.discard_pile.extend(self.owner.deck)
            self.owner.deck.clear()


class Woodcutter(ActionCard):
    name = 'Woodcutter'
    _cost = 3
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # '+1 Buy',
            # '+2 $'
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
    _cost = 4
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
        prompt = f'You played and trashed a Feast. Select a card costing up to 5 $ to gain.'
        self.owner.turn.buy_phase.gain_without_side_effects(prompt, max_cost=5, force=True)


class Spy(AttackCard):
    name = 'Spy'
    pluralized = 'Spies'
    _cost = 4
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = '\n'.join(
        [
            # '+1 Card',
            # '+1 Action',
            'Each player (including you) reveals the top card of their deck and either discards it or puts it back, your choice.'
        ]
    )

    extra_cards = 1
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    allow_simultaneous_reactions = True

    def reveal_top_card_and_discard_or_replace(self, revealer, chooser):
        # Revealer reveals a card
        card = revealer.take_from_deck()
        if card is None:
            self.game.broadcast(f'{revealer} has no more cards to draw from.')
            return
        self.game.broadcast(f'{revealer} revealed {a(card)}.')
        # Then the chooser makes a choice
        options = ['Discard', 'Return to deck']
        if revealer == chooser:
            prompt = f'You revealed {a(card)} with your Spy. What would you like to do with it?'
        else:
            prompt = f'{revealer} revealed {a(card)} with your Spy. What would you like {revealer} to do with it?'
        choice = chooser.interactions.choose_from_options(prompt=prompt, options=options, force=True)
        if choice == 'Discard':
            revealer.discard(card)
        elif choice == 'Return to deck':
            revealer.deck.append(card)
            self.game.broadcast(f'{revealer} returned the {card} to their deck.')

    def attack_effect(self, attacker, player):
        self.reveal_top_card_and_discard_or_replace(revealer=player, chooser=attacker)

    def action(self):
        self.reveal_top_card_and_discard_or_replace(revealer=self.owner, chooser=self.owner)

    @property
    def prompt(self):
        return f"Each player reveals the top card of their deck and either discards it or puts it back, {self.owner}'s choice."


class Thief(AttackCard):
    name = 'Thief'
    pluralized = 'Thieves'
    _cost = 4
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = '\n'.join(
        [
            'Each other player reveals the top 2 cards of their deck. If they revealed any Treasure cards, they trash one of them that you choose.',
            'You may gain any or all of these trashed cards. They discard the other revealed cards.'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    allow_simultaneous_reactions = True

    def attack_effect(self, attacker, player):
        # Player reveals two cards
        revealed_cards = []
        for _ in range(2):
            card = player.take_from_deck()
            if card is None:
                self.game.broadcast(f'{player} has no more cards to draw from.')
                break
            else:
                self.game.broadcast(f'{player} revealed {a(card)}.')
            revealed_cards.append(card)
        # Check if they revealed any treasure cards
        if any(CardType.TREASURE in card.types for card in revealed_cards):
            treasures = [card for card in revealed_cards if CardType.TREASURE in card.types]
            if len(set(type(card) for card in treasures)) == 1:
                # If there's only one type of treasure, just trash it automatically
                if len(treasures) == 1:
                    card_to_trash = treasures[0]
                    revealed_cards.remove(card_to_trash)
                    try:
                        card_to_discard = revealed_cards[0]
                    except IndexError:
                        card_to_discard = None
                elif len(treasures) == 2:
                    card_to_trash = treasures[0]
                    card_to_discard = treasures[1]
            else:
                # Otherwise, the attacker chooses which treasure to trash
                prompt = f"Your Thief revealed several of {player}'s Treasures. Choose a Treasure that {player} revealed to trash. You will have the opportunity to gain it afterward."
                card_to_trash = attacker.interactions.choose_from_options(prompt=prompt, options=treasures, force=True)
                treasures.remove(card_to_trash)
                card_to_discard = treasures[0]
            self.game.broadcast(f'{player} trashed {a(card_to_trash)}.')
            if card_to_discard is not None:
                player.discard(card_to_discard)
            # Allow the attacker to gain the trashed card
            prompt = f"Would you like to gain {player}'s trashed {card_to_trash}?"
            if attacker.interactions.choose_yes_or_no(prompt=prompt):
                card_to_trash.owner = attacker
                attacker.discard_pile.append(card_to_trash)
                self.game.broadcast(f"{attacker} gained {player}'s trashed {card_to_trash}.")
            else:
                self.supply.trash(card_to_trash)
        else:
            # If no Treasures were revealed, they discard both revealed cards
            player.discard(revealed_cards)

    @property
    def prompt(self):
        return f'Each other player reveals the top 2 cards of their deck. If they revealed any Treasure cards, they trash one of them that {self.owner} chooses. {self.owner} may gain any or all of these trashed cards. They discard the other revealed cards.'

    def action(self):
        pass


class Adventurer(ActionCard):
    name = 'Adventurer'
    _cost = 6
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
                self.game.broadcast(f'{self.owner} has no cards left to draw from.')
                break
            else:
                if CardType.TREASURE in card.types:
                    revealed_treasures.append(card)
                else:
                    revealed_other_cards.append(card)
        if revealed_treasures:
            self.game.broadcast(f"Revealed treasures: {', '.join(map(str, revealed_treasures))}. {self.owner} puts these into their hand.")
            self.owner.hand.extend(revealed_treasures)
        if revealed_other_cards:
            self.game.broadcast(f"Other revealed cards: {', '.join(map(str, revealed_other_cards))}. {self.owner} discards these.")
            self.owner.discard(revealed_other_cards)


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


for card_class in KINGDOM_CARDS:
    card_class.expansion = "Dominion"
