from abc import ABCMeta, abstractmethod
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
        self.pre_buy_hooks = {
            base_cards.Copper: [],
            base_cards.Silver: [],
            base_cards.Gold: [],
        }
        self.start()

    def start(self):
        self.game.broadcast(''.join((['*'] * 80)))
        self.game.broadcast(f"{self.player}'s turn!".upper())
        self.player.interactions.display_hand()
        self.action_phase.start()
        self.buy_phase.start()
        self.cleanup_phase.start()


class PreBuyHook(metaclass=ABCMeta):
    def __init__(self, player):
        self.player = player
        self.game = self.player.game

    @abstractmethod
    def __call__(self):
        pass

    @property
    @abstractmethod
    def persistent(self):
        pass


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
        treasures_in_hand = []
        for card in self.player.hand:
            if cards.CardType.TREASURE in card.types:
                treasures_in_hand.append(card)
        treasures_without_side_effects_to_play = []
        treasures_with_side_effects_to_play = []
        for treasure in treasures_in_hand:
            # If a Treasure in the player's hand has a play() method, ask if they want to use it; Otherwise, just assume they do
            if hasattr(treasure, 'play'):
                prompt = f'You have a {treasure.name} in your hand which has side effects. Would you like to play it?'
                if self.player.interactions.choose_yes_or_no(prompt):
                    treasures_with_side_effects_to_play.append(treasure)
                    self.player.play(treasure) # Add the treasure to the played cards area and remove from hand
                    # Activate side effects cause by playing this treasure
                    self.game.broadcast(f"{self.player} played a Treasure: {treasure.name}.")
                    treasure.play()
            else:
                treasures_without_side_effects_to_play.append(treasure)
                self.player.play(treasure) # Add the treasure to the played cards area and remove from hand
        # Broadcast which Treasures were played
        if treasures_without_side_effects_to_play:
            self.game.broadcast(f"{self.player} played Treasures: {', '.join(map(lambda card: card.name, treasures_without_side_effects_to_play))}.")
        treasures_played = treasures_with_side_effects_to_play + treasures_without_side_effects_to_play
        # Check if there are any pre-buy hooks registered to the played Treasures
        for treasure in treasures_played:
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
        for treasure in treasures_played:
            # Add the value of this Treasure
            self.turn.coppers_remaining += treasure.value
        # Buy cards
        while self.turn.buys_remaining > 0:
            prompt = f'You have {self.turn.coppers_remaining} $ to spend and {self.turn.buys_remaining} buys. Select a card to buy.'
            card_class = self.player.interactions.choose_card_class_from_supply(prompt=prompt, max_cost=self.turn.coppers_remaining, force=False)
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

    def buy_without_side_effects(self, max_cost, force):
        '''Buy a card without affecting coppers_remaining or buys_remaining'''
        prompt = f'You have {max_cost} $ to spend. Select a card to buy.'
        card_class = self.player.interactions.choose_card_class_from_supply(prompt=prompt, max_cost=max_cost, force=force)
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