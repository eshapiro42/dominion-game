import copy
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from .cards import cards, base_cards


class Turn:
    def __init__(self, player):
        self.player = player
        self.player.turn = self
        self.game = self.player.game
        self.actions_remaining = 1
        self.buys_remaining = 1
        self.coppers_remaining = 0
        self.action_phase = ActionPhase(turn=self)
        self.buy_phase = BuyPhase(turn=self)
        self.cleanup_phase = CleanupPhase(turn=self)
        self.pre_buy_hooks = defaultdict(list)
        self.invalid_card_classes = []

    def start(self):
        self.player.turns_played += 1
        self.game.broadcast(''.join((['*'] * 80)))
        self.game.broadcast(f"{self.player}'s turn!".upper())
        self.player.interactions.display_hand()
        self.action_phase.start()
        self.buy_phase.start()
        self.cleanup_phase.start()

    def add_pre_buy_hook(self, pre_buy_hook, card_class):
        self.pre_buy_hooks[card_class].append(pre_buy_hook)


class Phase(metaclass=ABCMeta):
    def __init__(self, turn):
        self.turn = turn
        self.player = self.turn.player
        self.game = self.player.game
        self.supply = self.player.game.supply

    @abstractmethod
    def start(self):
        pass


class ActionPhase(Phase):
    def start(self):
        while self.turn.actions_remaining > 0:
            # If there are no action cards in the player's hand, move on
            if not any(cards.CardType.ACTION in card.types for card in self.player.hand):
                self.player.interactions.send('No Action cards to play. Ending action phase.')
                return
            prompt = f'You have {self.turn.actions_remaining} actions. Select an Action card to play.'
            card = self.player.interactions.choose_specific_card_type_from_hand(prompt=prompt, card_type=cards.CardType.ACTION)
            if card is None:
                # The player is forfeiting their action phase
                self.player.interactions.send('Action phase forfeited.')
                return
            self.play(card)
        self.player.interactions.send('No actions left. Ending action phase.')

    def play(self, card):
        modifier = 'an' if card.name[0] in ['a', 'e', 'i', 'o', 'u'] else 'a'
        self.game.broadcast(f'{self.player} played {modifier} {card}.')
        # Add the card to the played cards area
        self.player.play(card)
        # Playing an action card uses one action
        self.turn.actions_remaining -= 1
        self.game.broadcast(f'-1 action --> {self.turn.actions_remaining} actions.')
        self.walk_through_action_card(card)

    def play_without_side_effects(self, card):
        '''Use this to play a card without losing actions or moving the card to the played cards area'''
        modifier = 'an' if card.name[0] in ['a', 'e', 'i', 'o', 'u'] else 'a'
        self.game.broadcast(f'{self.player} played {modifier} {card}.')
        self.walk_through_action_card(card)

    def walk_through_action_card(self, card):
        # Draw any additional cards specified on the card
        drawn_cards = None
        if card.extra_cards != 0:
            drawn_cards = self.player.draw(quantity=card.extra_cards)
            self.game.broadcast(f'+{card.extra_cards} cards --> {len(self.player.hand)} cards in hand.')
        # Add back any additional actions on the card
        if card.extra_actions != 0:
            self.turn.actions_remaining += card.extra_actions
            self.game.broadcast(f'+{card.extra_actions} actions --> {self.turn.actions_remaining} actions.')
        # Add any additional buys on the card
        if card.extra_buys != 0:
            self.turn.buys_remaining += card.extra_buys
            self.game.broadcast(f'+{card.extra_buys} buys --> {self.turn.buys_remaining} buys.')
        # Add any additional coppers on the card
        if card.extra_coppers != 0:
            self.turn.coppers_remaining += card.extra_coppers
            self.game.broadcast(f'+{card.extra_coppers} $ --> {self.turn.coppers_remaining} $.')
        if drawn_cards:
            self.player.interactions.send(f"You drew: {', '.join(map(str, drawn_cards))}.")
        # Do whatever the card is supposed to do
        card.play()


class BuyPhase(Phase):
    def start(self):
        # Find any Treasures in the player's hand
        treasures_available = []
        for card in self.player.hand:
            if cards.CardType.TREASURE in card.types:
                treasures_available.append(card)
        # Ask the player which Treasures they would like to play
        treasures_to_play = []
        while treasures_available:
            options = ['Play all Treasures'] + treasures_available
            prompt = f'Which Treasures would you like to play this turn?'
            choice = self.player.interactions.choose_from_options(prompt, options, force=False)
            if choice is None:
                break
            elif choice == 'Play all Treasures':
                treasures_to_play += treasures_available
                break
            else:
                treasures_available.remove(choice)
                treasures_to_play.append(choice)
        for treasure in treasures_to_play:
            self.game.broadcast(f"{self.player} played a Treasure: {treasure.name}.")
            # Add the Treasure to the played cards area and remove from hand
            self.player.play(treasure)
            # Activate side effects cause by playing this Treasure
            if hasattr(treasure, 'play'):
                treasure.play()
        # Check if there are any game-wide pre-buy hooks registered to the played Treasures
        for treasure in treasures_to_play:
            expired_hooks = []
            if type(treasure) in self.game.pre_buy_hooks:
                # Activate any pre-buy hooks caused by playing the Treasure
                for pre_buy_hook in self.game.pre_buy_hooks[type(treasure)]:
                    pre_buy_hook()
                    if not pre_buy_hook.persistent:
                        expired_hooks.append(pre_buy_hook)
                # Remove any non-persistent hooks
                for hook in expired_hooks:
                    self.game.pre_buy_hooks[type(treasure)].remove(hook)
        # Check if there are any turn-wide pre-buy hooks registered to the played Treasures
        for treasure in treasures_to_play:
            expired_hooks = []
            if type(treasure) in self.turn.pre_buy_hooks:
                # Activate any pre-buy hooks caused by playing the Treasure
                for pre_buy_hook in self.turn.pre_buy_hooks[type(treasure)]:
                    pre_buy_hook()
                    if not pre_buy_hook.persistent:
                        expired_hooks.append(pre_buy_hook)
                # Remove any non-persistent hooks
                for hook in expired_hooks:
                    self.turn.pre_buy_hooks[type(treasure)].remove(hook)
        # Add up any played treasures
        for treasure in treasures_to_play:
            # Add the value of this Treasure
            self.turn.coppers_remaining += treasure.value
        # Buy cards
        while self.turn.buys_remaining > 0:
            prompt = f'You have {self.turn.coppers_remaining} $ to spend and {self.turn.buys_remaining} buys. Select a card to buy.'
            card_class = self.player.interactions.choose_card_class_from_supply(prompt=prompt, max_cost=self.turn.coppers_remaining, force=False, invalid_card_classes=self.turn.invalid_card_classes)
            if card_class is None:
                # The player is forfeiting their buy phase
                self.player.interactions.send('Buy phase forfeited.')
                return
            else:
                self.buy(card_class)
        self.player.interactions.send('No buys left. Ending buy phase.')

    def buy(self, card_class):
        # Buying a card uses one buy
        self.turn.buys_remaining -= 1
        # Gain the desired card
        modifier = 'an' if card_class.name[0] in ['a', 'e', 'i', 'o', 'u'] else 'a'
        self.game.broadcast(f'{self.player} bought {modifier} {card_class.name}.')
        self.player.gain(card_class)
        self.turn.coppers_remaining -= card_class.cost

    def buy_without_side_effects(self, max_cost, force, exact_cost=False):
        '''Buy a card without affecting coppers_remaining or buys_remaining'''
        prompt = f'You have {max_cost} $ to spend. Select a card to buy.'
        card_class = self.player.interactions.choose_card_class_from_supply(prompt=prompt, max_cost=max_cost, force=force, exact_cost=exact_cost)
        if card_class is None:
            self.game.broadcast(f'{self.player} did not buy anything.')
            return
        else:
            # Gain the desired card
            modifier = 'an' if card_class.name[0] in ['a', 'e', 'i', 'o', 'u'] else 'a'
            self.game.broadcast(f'{self.player} bought {modifier} {card_class.name}.')
            self.player.gain(card_class)


class CleanupPhase(Phase):
    def start(self):
        self.player.cleanup()
        self.player.interactions.send('Your hand for next turn:')
        self.player.interactions.display_hand()