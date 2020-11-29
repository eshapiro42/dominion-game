import cards
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass


class Turn:
    def __init__(self, player):
        self.player = player
        self.player.turn = self
        self.actions_remaining = 1
        self.buys_remaining = 1
        self.coppers_remaining = 0
        self.action_phase = ActionPhase(turn=self)
        self.buy_phase = BuyPhase(turn=self)
        self.cleanup_phase = CleanupPhase(turn=self)
        self.pre_buy_hooks = {
            cards.Copper: [],
            cards.Silver: [],
            cards.Gold: [],
        }
        self.start()

    def start(self):
        print(f"{self.player}'s turn!\n".upper())
        self.player.interactions.display_hand()
        self.action_phase.start()
        self.buy_phase.start()
        self.cleanup_phase.start()


class PreBuyHook(metaclass=ABCMeta):
    def __init__(self, player):
        self.player = player

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
        self.supply = self.player.game.supply

    @abstractmethod
    def start(self):
        pass


class ActionPhase(Phase):
    def start(self):
        while self.turn.actions_remaining > 0:
            # If there are no action cards in the player's hand, move on
            if not any(cards.CardType.ACTION in card.types for card in self.player.hand):
                print('No action cards to play. Ending action phase.\n')
                return
            prompt = f'You have {self.turn.actions_remaining} actions. Select an action card to play.'
            card = self.player.interactions.choose_specific_card_type_from_hand(prompt=prompt, card_type=cards.CardType.ACTION)
            if card is None:
                # The player is forfeiting their action phase
                print('Action phase forfeited.\n')
                return
            self.play(card)
        print('No actions left. Ending action phase.\n')

    def play(self, card):
        modifier = 'an' if card.name[0] in ['a', 'e', 'i', 'o', 'u'] else 'a'
        print(f'{self.player} played {modifier} {card}.\n')
        # Add the card to the played cards area
        self.player.play(card)
        # Playing an action card uses one action
        self.turn.actions_remaining -= 1
        print(f'-1 action --> {self.turn.actions_remaining}')
        # Draw any additional cards specified on the card
        drawn_cards = self.player.draw(quantity=card.extra_cards)
        print(f'+{card.extra_cards} cards --> {drawn_cards}')
        # Add back any additional actions on the card
        self.turn.actions_remaining += card.extra_actions
        print(f'+{card.extra_actions} actions --> {self.turn.actions_remaining}')
        # Add any additional buys on the card
        self.turn.buys_remaining += card.extra_buys
        print(f'+{card.extra_buys} buys --> {self.turn.buys_remaining}')
        # Add any additional coppers on the card
        self.turn.coppers_remaining += card.extra_coppers
        print(f'+{card.extra_coppers} $ --> {self.turn.coppers_remaining}\n')
        # Do whatever the card is supposed to do
        card.play()

    def play_without_side_effects(self, card):
        '''Use this to play a card without losing actions or moving the card to the played cards area'''
        modifier = 'an' if card.name[0] in ['a', 'e', 'i', 'o', 'u'] else 'a'
        print(f'{self.player} played {modifier} {card}.\n')
        # Draw any additional cards specified on the card
        drawn_cards = self.player.draw(quantity=card.extra_cards)
        print(f'+{card.extra_cards} cards --> {drawn_cards}')
        # Add back any additional actions on the card
        self.turn.actions_remaining += card.extra_actions
        print(f'+{card.extra_actions} actions --> {self.turn.actions_remaining}')
        # Add any additional buys on the card
        self.turn.buys_remaining += card.extra_buys
        print(f'+{card.extra_buys} buys --> {self.turn.buys_remaining}')
        # Add any additional coppers on the card
        self.turn.coppers_remaining += card.extra_coppers
        print(f'+{card.extra_coppers} $ --> {self.turn.coppers_remaining}\n')
        # Do whatever the card is supposed to do
        card.play()


class BuyPhase(Phase):
    def start(self):
        # Add up any treasures from player's hand
        for card in self.player.hand:
            if cards.CardType.TREASURE in card.types:
                # Activate any pre-buy hooks caused by playing the Treasure
                for pre_buy_hook in self.turn.pre_buy_hooks[type(card)]:
                    pre_buy_hook()
                    if not pre_buy_hook.persistent:
                        self.turn.pre_buy_hooks[type(card)].remove(pre_buy_hook)
                self.turn.coppers_remaining += card.value
        # Buy cards
        while self.turn.buys_remaining > 0:
            prompt = f'You have {self.turn.coppers_remaining} $ to spend and {self.turn.buys_remaining} buys. Select a card to buy.'
            card_class = self.player.interactions.choose_card_class_from_supply(prompt=prompt, max_cost=self.turn.coppers_remaining, force=False)
            if card_class is None:
                # The player is forfeiting their buy phase
                print('Buy phase forfeited.\n')
                return
            else:
                self.buy(card_class)
        print('No buys left. Ending buy phase.\n')

    def buy(self, card_class):
        # Buying a card uses one buy
        self.turn.buys_remaining -= 1
        # Gain the desired card
        modifier = 'an' if card_class.name[0] in ['a', 'e', 'i', 'o', 'u'] else 'a'
        print(f'{self.player} bought {modifier} {card_class.name}.\n')
        self.player.gain(card_class)
        self.turn.coppers_remaining -= card_class.cost

    def buy_without_side_effects(self, max_cost, force):
        '''Buy a card without affecting coppers_remaining or buys_remaining'''
        prompt = f'You have {max_cost} $ to spend. Select a card to buy.'
        card_class = self.player.interactions.choose_card_class_from_supply(prompt=prompt, max_cost=max_cost, force=force)
        if card_class is None:
            print('Did not buy anything.\n')
            return
        else:
            # Gain the desired card
            modifier = 'an' if card_class.name[0] in ['a', 'e', 'i', 'o', 'u'] else 'a'
            print(f'{self.player} bought {modifier} {card_class.name}.\n')
            self.player.gain(card_class)


class CleanupPhase(Phase):
    def start(self):
        self.player.cleanup()