import math
from .cards import CardType, Card, TreasureCard, ActionCard, AttackCard, ReactionCard, VictoryCard, CurseCard
from . import base_cards
from ..hooks import TreasureHook, PreBuyHook, PostGainHook


# KINGDOM CARDS

class Courtyard(ActionCard):
    name = 'Courtyard'
    cost = 2
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+3 Cards',
            'Put a card from your hand onto your deck.'
        ]
    )

    extra_cards = 3
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        # Choose a card from your hand
        prompt = f'Choose a card from your hand to put onto your deck.'
        card = self.interactions.choose_card_from_hand(prompt, force=True)
        # Put that card onto your deck
        if card is not None:
            self.owner.hand.remove(card)
            self.owner.deck.append(card)
            self.game.broadcast(f'{self.owner} put a card from their hand onto their deck.')


class Lurker(ActionCard):
    name = 'Lurker'
    cost = 2
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Action',
            'Choose one: Trash an Action card from the Supply; or gain an Action card from the trash.'
        ]
    )

    extra_cards = 0
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        # Choose one
        prompt = f'Which would you like to choose?'
        options = [
            'Trash an Action card from the Supply',
            'Gain an Action card from the trash'
        ]
        choice = self.interactions.choose_from_options(prompt, options, force=True)
        if choice == 'Trash an Action card from the Supply':
            prompt = f'Choose an Action card from the Supply to trash.'
            card_class = self.interactions.choose_specific_card_type_from_supply(prompt, max_cost=math.inf, card_type=CardType.ACTION, force=True)
            if card_class is not None:
                card_to_trash = self.supply.draw(card_class)
                self.supply.trash(card_to_trash)
                self.game.broadcast(f'{self.owner} trashed a {card_to_trash} from the Supply.')
        elif choice == 'Gain an Action card from the trash':
            prompt = f'Choose an Action card from the trash to gain.'
            options = [card_class for card_class in self.supply.trash_pile if CardType.ACTION in card_class.types and self.supply.trash_pile[card_class]]
            if options:
                card_class_to_gain = self.interactions.choose_specific_card_type_from_trash(prompt, max_cost=math.inf, card_type=CardType.ACTION, force=True)
                if card_class_to_gain is not None:
                    self.owner.gain_from_trash(card_class_to_gain)
            else:
                self.game.broadcast('There are no Action cards in the trash to gain.')


class Pawn(ActionCard):
    name = 'Pawn'
    cost = 2
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            'Choose two: +1 Card; +1 Action; +1 Buy; +1 $. The choices must be different.'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        options = [
            '+1 Card',
            '+1 Action',
            '+1 Buy',
            '1 $'
        ]
        # First, the choices are selected
        choices = []
        prompt = f'Which would you like to choose first?'
        choice = self.interactions.choose_from_options(prompt, options, force=True)
        choices.append(choice)
        options.remove(choice) # The same option cannot be chosen again
        prompt = f'Which would you like to choose second?'
        choice = self.interactions.choose_from_options(prompt, options, force=True)
        choices.append(choice)
        self.game.broadcast(f"{self.owner} chose: {', '.join(choices)}.")
        # Then the selected choices are executed
        for choice in choices:
            if choice == '+1 Card':
                cards_drawn = self.owner.draw(1)
                if cards_drawn:
                    card = cards_drawn[0]
                    self.game.broadcast(f'+1 card --> {len(self.owner.hand)} cards in hand.')
                    self.interactions.send(f'You drew: {card}.')
            elif choice == '+1 Action':
                self.owner.turn.actions_remaining += 1
                self.game.broadcast(f'+1 action --> {self.owner.turn.actions_remaining} actions.')
            elif choice == '+1 Buy':
                self.owner.turn.buys_remaining += 1
                self.game.broadcast(f'+1 buy --> {self.owner.turn.buys_remaining} buys.')
            elif choice == '1 $':
                self.owner.turn.coppers_remaining += 1
                self.game.broadcast(f'+1 $ --> {self.owner.turn.coppers_remaining} $.')


class Masquerade(ActionCard):
    name = 'Masquerade'
    cost = 3
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+2 Cards',
            'Each player with any cards in hand passes one to the next such player to their left at once. Then you may trash a card from your hand.'
        ]
    )

    extra_cards = 2
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        self.game.broadcast('Each player with any cards in hand much choose a card to pass to the next such player to their left.')
        players_with_cards = [player for player in self.owner.other_players if len(player.hand) > 0]
        if len(self.owner.hand) > 0:
            players_with_cards = [self.owner] + players_with_cards
        cards_passed = [] # This will be a list of [(card_received, old_owner, new_owner)]
        # Each player chooses a card to pass
        for player in players_with_cards:
            player_idx = players_with_cards.index(player)
            try:
                player_to_left = players_with_cards[player_idx + 1]
            except IndexError:
                player_to_left = players_with_cards[0]
            prompt = f'{player}: Choose a card from your hand to pass to {player_to_left}.'
            card_to_pass = player.interactions.choose_card_from_hand(prompt, force=True)
            player.interactions.send(f'{player}: You passed {player_to_left} a {card_to_pass}.')
            cards_passed.append((card_to_pass, player, player_to_left))
        # Cards get passed
        for card_received, old_owner, new_owner in cards_passed:
            old_owner.hand.remove(card_received)
            new_owner.hand.append(card_received)
            card_received.owner = new_owner # Set .owner attribute of each card after they trade hands
            new_owner.interactions.send(f'{new_owner}: {old_owner} passed you a {card_received}.')
        # You may trash a card from your hand
        prompt = f'You may trash a card from your hand.'
        card_to_trash = self.interactions.choose_card_from_hand(prompt, force=False)
        if card_to_trash is not None:
            self.owner.trash(card_to_trash)


class ShantyTown(ActionCard):
    name = 'Shanty Town'
    cost = 3
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+2 Actions',
            'Reveal your hand. If you have no Action cards in hand, +2 Cards.'
        ]
    )

    extra_cards = 0
    extra_actions = 2
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        self.game.broadcast(f"{self.owner} reveals their hand: {', '.join(map(str, self.owner.hand))}")
        if not any(CardType.ACTION in card.types for card in self.owner.hand):
            self.game.broadcast(f'{self.owner} has no Action cards in their hand, so they draw 2 cards.')
            cards_drawn = self.owner.draw(2)
            if cards_drawn:
                self.game.broadcast(f'{self.owner} drew {len(cards_drawn)} cards.')
                self.interactions.send(f"You drew: {', '.join(map(str, cards_drawn))}.")
            else:
                self.game.broadcast(f'{self.owner} has no more cards to draw from.')
        else:
            self.game.broadcast(f'{self.owner} has Action cards in their hand.')


class Steward(ActionCard):
    name = 'Steward'
    cost = 3
    types = [CardType.ACTION]
    image_path = 'Steward'

    description = '\n'.join(
        [
            'Choose one: +2 Cards; or +2 $; or trash 2 cards from your hand.'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        # Choose one
        options = [
            '+2 Cards',
            '2 $',
            'Trash 2 cards from your hand'
        ]
        prompt = f'Which would you like to choose?'
        choice = self.interactions.choose_from_options(prompt, options, force=True)
        if choice == '+2 Cards':
            cards_drawn = self.owner.draw(2)
            if cards_drawn:
                self.game.broadcast(f'+{len(cards_drawn)} cards --> {len(self.owner.hand)} cards in hand.')
                self.interactions.send(f"You drew: {', '.join(map(str, cards_drawn))}.")
        elif choice == '2 $':
            self.owner.turn.coppers_remaining += 2
            self.game.broadcast(f'+2 $ --> {self.owner.turn.coppers_remaining} $.')
        elif choice == 'Trash 2 cards from your hand':
            for trash_num in range(2):
                prompt = f'Choose a card from your hand to trash ({trash_num + 1}/2).'
                card_to_trash = self.interactions.choose_card_from_hand(prompt, force=True)
                if card_to_trash is not None:
                    self.owner.trash(card_to_trash)


class Swindler(AttackCard):
    name = 'Swindler'
    cost = 3
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = '\n'.join(
        [
            '+2 $',
            'Each other player trashes the top card of their deck and gains a card with the same cost that you choose.'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 2

    @property
    def prompt(self):
        return f'Each other player trashes the top card of their deck and gains a card with the same cost that {self.owner} chooses.'

    def attack_effect(self, attacker, player):
        # Trash the top card of their deck
        card_to_trash = player.take_from_deck()
        if card_to_trash is not None:
            self.supply.trash(card_to_trash)
            # Gain a card with the same cost that the attacker chooses
            cost = card_to_trash.cost
            prompt = f'{attacker}: choose a card costing {cost} $ for {player} to gain.'
            card_class_to_gain = attacker.interactions.choose_card_class_from_supply(prompt, max_cost=cost, force=True, exact_cost=True)
            if card_class_to_gain is not None:
                player.gain(card_class_to_gain)
            else:
                self.game.broadcast(f'There are no cards costing {cost} $ in the Supply, so {player} did not gain a card.')
        else:
            self.game.broadcast(f'{player} has no cards in their deck.')

    def action(self):
        pass


class WishingWell(ActionCard):
    name = 'Wishing Well'
    cost = 3
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Card',
            '+1 Action',
            'Name a card, then reveal the top card of your deck. If you named it, put it into your hand.'
        ]
    )

    extra_cards = 1
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        # Name a card
        all_cards = [card_class for card_class in self.supply.card_stacks]
        prompt = 'Name a card.'
        named_card_class = self.interactions.choose_from_options(prompt, options=all_cards, force=True)
        self.game.broadcast(f'{self.owner} named {named_card_class.name}.')
        # Reveal the top card of your deck
        revealed_card = self.owner.take_from_deck()
        self.game.broadcast(f'{self.owner} revealed a {revealed_card}.')
        if isinstance(revealed_card, named_card_class):
            # If you named it, put it into your hand.
            self.owner.hand.append(revealed_card)
            self.game.broadcast(f'{self.owner} put the {revealed_card} into their hand.')
        else:
            # Otherwise it goes back on your deck
            self.owner.deck.append(revealed_card)
            self.game.broadcast(f'{self.owner} put the {revealed_card} back onto their deck.')


class Baron(ActionCard):
    name = 'Baron'
    cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Buy',
            "You may discard an Estate for +4 $. If you don't, gain an Estate."
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 1
    extra_coppers = 0

    def action(self):
        # You may discard an Estate for +4 $
        prompt = 'You have an Estate in your hand. Would you like to discard it for +4 $?'
        if any(isinstance(card, base_cards.Estate) for card in self.owner.hand) and self.interactions.choose_yes_or_no(prompt):
            estate_to_discard = [card for card in self.owner.hand if isinstance(card, base_cards.Estate)][0]
            self.owner.discard(estate_to_discard)
            self.owner.turn.coppers_remaining += 4
            self.game.broadcast(f'+4 $ --> {self.owner.turn.coppers_remaining} $.')
        else:
            self.owner.gain(base_cards.Estate)


class Bridge(ActionCard):
    name = 'Bridge'
    cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Buy',
            '+1 $',
            'This turn, cards (everywhere) cost 1 $ less, but not less than 0 $.'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 1
    extra_coppers = 1

    def action(self):
        for card_class in self.supply.card_stacks:
            self.supply.modify_cost(card_class, -1)


class Conspirator(ActionCard):
    name = 'Conspirator'
    cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+2 $',
            "If you've played 3 or more Actions this turn (counting this), +1 Card and +1 Action."
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 2

    def action(self):
        if len([card for card in self.owner.played_cards if CardType.ACTION in card.types]) >= 3:
            self.game.broadcast(f'{self.owner} has played 3 or more Actions this turn.')
            drawn_cards = self.owner.draw(1)
            if drawn_cards:
                card = drawn_cards[0]
                self.game.broadcast(f'+1 card --> {len(self.owner.hand)} cards in hand.')
                self.interactions.send(f'You drew: {card}.')
            self.owner.turn.actions_remaining += 1
            self.game.broadcast(f'+1 action --> {self.owner.turn.actions_remaining} actions.')
        else:
            self.game.broadcast(f'{self.owner} has played fewer than 3 Actions this turn.')


class Diplomat(ReactionCard):
    name = 'Diplomat'
    cost = 4
    types = [CardType.ACTION, CardType.REACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+2 Cards',
            'If you have 5 or fewer cards in hand (after drawing), +2 Actions.',
            'When another player plays an Attack card, you may first reveal this from a hand of 5 or more cards, to draw 2 cards then discard 3.'
        ]
    )

    extra_cards = 2
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def react(self):
        pass

    def action(self):
        pass


class Ironworks(ActionCard):
    name = 'Ironworks'
    cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            'Gain a card costing up to 4 $. If the gained card is an...',
            'Action card, +1 Action',
            'Treasure card, +1 $',
            'Victory card, +1 Card'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        prompt = f'Gain a card costing up to 4 $.'
        card_class_to_gain = self.interactions.choose_card_class_from_supply(prompt, max_cost=4, force=True)
        self.owner.gain(card_class_to_gain)
        if CardType.ACTION in card_class_to_gain.types:
            self.owner.turn.actions_remaining += 1
            self.game.broadcast(f'+1 action --> {self.owner.turn.actions_remaining} actions.')
        if CardType.TREASURE in card_class_to_gain.types:
            self.owner.turn.coppers_remaining += 1
            self.game.broadcast(f'+1 $ --> {self.owner.turn.coppers_remaining} $.')
        if CardType.VICTORY in card_class_to_gain.types:
            cards_drawn = self.owner.draw(1)
            if cards_drawn:
                card = cards_drawn[0]
                self.game.broadcast(f'+1 card --> {len(self.owner.hand)} cards in hand.')
                self.interactions.send(f'You drew: {card}.')


class Mill(ActionCard, VictoryCard):
    name = 'Mill'
    cost = 4
    types = [CardType.ACTION, CardType.VICTORY]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Card',
            '+1 Action',
            'You may discard 2 cards, for +2 $',
            '1 victory point'
        ]
    )

    extra_cards = 1
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    points = 1

    def action(self):
        prompt = 'Would you like to discard 2 cards for +2 $?'
        if self.interactions.choose_yes_or_no(prompt):
            discarded_cards = []
            for discard_num in range(2):
                prompt = f'Choose a card to discard ({discard_num + 1}/2).'
                card_to_discard = self.interactions.choose_card_from_hand(prompt, force=False)
                if card_to_discard is not None:
                    discarded_cards.append(card_to_discard)
                    self.owner.discard(card_to_discard)
            if len(discarded_cards) == 2:
                self.owner.turn.coppers_remaining += 2
                self.game.broadcast(f'+2 $ --> {self.owner.turn.coppers_remaining} $.')


class MiningVillage(ActionCard):
    name = 'Mining Village'
    cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Card',
            '+2 Actions',
            'You may trash this for +2 $.'
        ]
    )

    extra_cards = 1
    extra_actions = 2
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        prompt = 'Would you like to trash this Mining Village for +2 $?'
        if self.interactions.choose_yes_or_no(prompt):
            self.owner.trash_played_card(self)
            self.owner.turn.coppers_remaining += 2
            self.game.broadcast(f'+2 $ --> {self.owner.turn.coppers_remaining} $.')


class SecretPassage(ActionCard):
    name = 'Secret Passage'
    cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+2 Cards',
            '+1 Action',
            'Take a card from your hand and put it anywhere in your deck.'
        ]
    )

    extra_cards = 2
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        prompt = f'Choose a card from your hand to put in your deck.'
        card = self.interactions.choose_card_from_hand(prompt, force=True)
        if card is not None:
            minimum = 1
            maximum = len(self.owner.deck) + 1
            prompt = f'Where in your deck would you like to put your {card}? (1: on top, {maximum}: on bottom).'
            index = self.interactions.choose_from_range(prompt, minimum, maximum, force=True) - 1
            self.owner.deck.insert(len(self.owner.deck) - index, card)
            self.game.broadcast(f'{self.owner} put a card from his hand into position {index + 1} in his deck.')


class Courtier(ActionCard):
    name = 'Courtier'
    cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            'Reveal a card from your hand. For each type it has (Action, Attack, etc.), choose one: +1 Action; or +1 Buy; or +3 $; or gain a Gold. The choices must be different.'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        prompt = 'Choose a card from your hand to reveal.'
        revealed_card = self.interactions.choose_card_from_hand(prompt, force=True)
        if revealed_card is not None:
            num_types = len(revealed_card.types)
            self.game.broadcast(f'{self.owner} may choose {num_types} of the available options.')
            options = [
                '+1 Action',
                '+1 Buy',
                '+3 $',
                'Gain a Gold'
            ]
            choices = []
            for choice_num in range(num_types):
                prompt = f'Which would you like to choose? ({choice_num + 1}/{num_types})'
                choice = self.interactions.choose_from_options(prompt, options, force=True)
                choices.append(choice)
                options.remove(choice) # the same option cannot be chosen twice
            for choice in choices:
                if choice == '+1 Action':
                    self.owner.turn.actions_remaining += 1
                    self.game.broadcast(f'+1 action --> {self.owner.turn.actions_remaining} actions.')
                elif choice == '+1 Buy':
                    self.owner.turn.buys_remaining += 1
                    self.game.broadcast(f'+1 buy --> {self.owner.turn.buys_remaining} buys.')
                elif choice == '+3 $':
                    self.owner.turn.coppers_remaining += 3
                    self.game.broadcast(f'+3 $ --> {self.owner.turn.coppers_remaining} $.')
                elif choice == 'Gain a Gold':
                    self.owner.gain(base_cards.Gold)


class Duke(VictoryCard):
    name = 'Duke'
    cost = 5
    types = [CardType.VICTORY]
    image_path = ''

    description = '\n'.join(
        [
            'Worth 1 victory point per Duchy you have.'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    @property
    def points(self):
        num_duchies = len([card for card in self.owner.all_cards if isinstance(card, base_cards.Duchy)])
        return num_duchies


class Minion(AttackCard):
    name = 'Minion'
    cost = 5
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Action',
            'Choose one: +2 $; or discard your hand, +4 Cards, and each other player with at least 5 cards in hand discards their hand and draws 4 cards.'
        ]
    )
    prompt = 'Each other player with at least 5 cards in hand discards their hand and draws 4 cards.'

    extra_cards = 0
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def attack_effect(self, attacker, player):
        if len(player.hand) >= 5:
            # Discard your hand
            cards_to_discard = list(player.hand) # Make a shallow copy
            for card in cards_to_discard:
                player.discard(card)
            # Draw four cards
            cards_drawn = player.draw(4)
            if cards_drawn:
                self.game.broadcast(f'{player} drew {len(cards_drawn)} cards --> {len(player.hand)} cards in hand.')
                player.interactions.send(f"You drew: {', '.join(map(str, cards_drawn))}.")        

    def action(self):
        options = [
            '+2 $',
            'Discard your hand, +4 Cards, and each other player with at least 5 cards in hand discards their hand and draws 4 cards'
        ]
        prompt = 'Which would you like to choose?'
        choice = self.interactions.choose_from_options(prompt, options, force=True)
        if choice == '+2 $':
            self.attacking = False # do not activate the attack_effect
            self.owner.turn.coppers_remaining += 2
            self.game.broadcast(f'+2 $ --> {self.owner.turn.coppers_remaining} $.')
        elif choice == 'Discard your hand, +4 Cards, and each other player with at least 5 cards in hand discards their hand and draws 4 cards':
            self.attacking = True # activate the attack_effect
            # Discard your hand
            cards_to_discard = list(self.owner.hand) # Make a shallow copy
            for card in cards_to_discard:
                self.owner.discard(card)
            # Draw four cards
            cards_drawn = self.owner.draw(4)
            if cards_drawn:
                self.game.broadcast(f'+{len(cards_drawn)} cards --> {len(self.owner.hand)} cards in hand.')
                self.interactions.send(f"You drew: {', '.join(map(str, cards_drawn))}.")


class Patrol(ActionCard):
    name = 'Patrol'
    cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+3 Cards',
            'Reveal the top 4 cards of your deck. Put the Victory cards and Curses into your hand. Put the rest back in any order.'
        ]
    )

    extra_cards = 3
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        # Reveal the top 4 cards of your deck
        revealed_cards = []
        for _ in range(4):
            card = self.owner.take_from_deck()
            if card is not None:
                revealed_cards.append(card)
            else:
                break
        if revealed_cards:
            if len(revealed_cards) < 4:
                self.game.broadcast(f'{self.owner} only had {len(revealed_cards)} in their deck.')
            self.game.broadcast(f"{self.owner} revealed: {', '.join(map(str, revealed_cards))}.")
        else:
            self.game.broadcast(f'{self.owner} had no cards in their deck.')
        remaining_cards = list(revealed_cards) # make a shallow copy
        # Put the Victory cards and Curses into your hand
        victory_and_curse_cards = [card for card in revealed_cards if CardType.VICTORY in card.types or CardType.CURSE in card.types]
        for card in revealed_cards:
            if card in victory_and_curse_cards:
                remaining_cards.remove(card)
        self.owner.hand.extend(victory_and_curse_cards)
        self.game.broadcast(f"{self.owner} put card into their hand: {', '.join(map(str, victory_and_curse_cards))}.")
        # Put the rest back in any order
        choice_num = 0
        choice_count = len(remaining_cards)
        while remaining_cards:
            prompt = f'Which card would you like to put on your deck next? ({choice_num + 1}/{choice_count}).'
            choice = self.interactions.choose_from_options(prompt, remaining_cards, force=True)
            choice_num += 1
            self.owner.deck.append(choice)
            self.game.broadcast(f'{self.owner} put a {choice} onto their deck.')
            remaining_cards.remove(choice)    


class Replace(AttackCard):
    name = 'Replace'
    cost = 5
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = '\n'.join(
        [
            "Trash a card from your hand. Gain a card costing up to 2 $ more than it. If the gained card is an Action or Treasure, put it onto your deck; if it's a Victory card, each other player gains a Curse."
        ]
    )
    prompt = 'Each other player gains a curse.'

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def attack_effect(self, attacker, player):
        player.gain(base_cards.Curse)

    def action(self):
        self.attacking = False # attack_effect is only activated if the owner gains a Victory card
        # Trash a card from your hand
        prompt = 'Choose a card from your hand to trash.'
        card_to_trash = self.interactions.choose_card_from_hand(prompt, force=True)
        if card_to_trash is not None:
            self.owner.trash(card_to_trash)
            # Gain a card costing up to 2 $ more than it
            max_cost = card_to_trash.cost + 2
            card_class_to_gain = self.interactions.choose_card_class_from_supply(prompt, max_cost, force=True)
            # If it's an action or a treasure, gain to deck
            if CardType.ACTION in card_class_to_gain.types or CardType.TREASURE in card_class_to_gain.types:
                self.owner.gain_to_deck(card_class_to_gain)
            # Otherwise they gain it normally
            else:
                self.owner.gain(card_class_to_gain)
            # If the gained card is a Victory card, activate the attack_effect
            if CardType.VICTORY in card_class_to_gain.types:
                self.attacking = True


class Torturer(AttackCard):
    name = 'Torturer'
    cost = 5
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = '\n'.join(
        [
            '+3 Cards',
            "Each other player either discards 2 cards or gains a Curse to their hand, their choice. (They may pick an option they can't do)."
        ]
    )
    prompt = "Each other player either discards 2 cards or gains a Curse to their hand, their choice. (They may pick an option they can't do)."

    extra_cards = 3
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def attack_effect(self, attacker, player):
        prompt = f'{player}: Which would you like to choose?'
        num_cards_in_hand = len(player.hand)
        num_curses_in_supply = self.supply.card_stacks[base_cards.Curse].cards_remaining
        options = [
            f'Discard 2 cards ({num_cards_in_hand} in your hand)',
            f'Gain a Curse to your hand ({num_curses_in_supply} in the Supply)'
        ]
        choice = player.interactions.choose_from_options(prompt, options, force=True)
        self.game.broadcast(f'{player} chose: {choice}.')
        if choice == f'Discard 2 cards ({num_cards_in_hand} in your hand)':
            for card_num in range(2):
                prompt = f'{player}: Choose card {card_num + 1} of 2 to discard.'
                card_to_discard = player.interactions.choose_card_from_hand(prompt=prompt, force=True)
                if card_to_discard is not None:
                    player.discard(card_to_discard)
                else:
                    self.game.broadcast(f'{player} has no more cards to discard.')
        elif choice == f'Gain a Curse to your hand ({num_curses_in_supply} in the Supply)':
            player.gain_to_hand(base_cards.Curse)

    def action(self):
        pass


class TradingPost(ActionCard):
    name = 'Trading Post'
    cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            'Trash 2 cards from your hand. If you did, gain a Silver to your hand.'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        trashed_cards = []
        for trash_num in range(2):
            prompt = f'Choose a card from your hand to trash ({trash_num + 1}/2).'
            card_to_trash = self.interactions.choose_card_from_hand(prompt, force=True)
            if card_to_trash is not None:
                trashed_cards.append(card_to_trash)
                self.owner.trash(card_to_trash)
        if len(trashed_cards) == 2:
            self.owner.gain(base_cards.Silver)


class Upgrade(ActionCard):
    name = 'Upgrade'
    cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Card',
            '+1 Action',
            'Trash a card from your hand. Gain a card costing exactly 1 $ more than it.'
        ]
    )

    extra_cards = 1
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        prompt = f'Choose a card from your hand to trash.'
        card_to_trash = self.interactions.choose_card_from_hand(prompt, force=True)
        if card_to_trash is not None:
            self.owner.trash(card_to_trash)
            cost = card_to_trash.cost + 1
            prompt = f'Choose a card costing exactly {cost} to gain.'
            card_class_to_gain = self.interactions.choose_card_class_from_supply(prompt, cost, force=True, exact_cost=True)
            if card_class_to_gain is not None:
                self.owner.gain(card_class_to_gain)


class Harem(TreasureCard, VictoryCard):
    name = 'Harem'
    cost = 6
    types = [CardType.TREASURE, CardType.VICTORY]
    image_path = ''

    description = '\n'.join(
        [
            '2 $',
            '2 victory points'
        ]
    )

    value = 2
    points = 2


class Nobles(ActionCard, VictoryCard):
    name = 'Nobles'
    cost = 6
    types = [CardType.ACTION, CardType.VICTORY]
    image_path = ''

    description = '\n'.join(
        [
            'Choose one: +3 Cards; or +2 Actions.'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    points = 2

    def action(self):
        options = [
            '+3 Cards',
            '+2 Actions',
        ]
        prompt = f'Which would you like to choose?'
        choice = self.interactions.choose_from_options(prompt, options, force=True)
        self.game.broadcast(f"{self.owner} chose: {choice}.")
        if choice == '+3 Cards':
            cards_drawn = self.owner.draw(3)
            if cards_drawn:
                self.game.broadcast(f'+3 cards --> {len(self.owner.hand)} cards in hand.')
                self.interactions.send(f"You drew: {', '.join(map(str, cards_drawn))}.")
        elif choice == '+2 Actions':
            self.owner.turn.actions_remaining += 2
            self.game.broadcast(f'+2 actions --> {self.owner.turn.actions_remaining} actions.')


KINGDOM_CARDS = [
    Courtyard,
    Lurker,
    Pawn,
    Masquerade,
    ShantyTown,
    Steward,
    Swindler,
    WishingWell,
    Baron,
    Bridge,
    Conspirator,
    # Diplomat,
    Ironworks,
    Mill,
    MiningVillage,
    SecretPassage,
    Courtier,
    Duke,
    Minion,
    Patrol,
    Replace,
    Torturer,
    TradingPost,
    Upgrade,
    Harem,
    Nobles
]