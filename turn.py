import cards
import prettytable
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass


class ActionPhaseError(Exception):
    '''Raised when a player attempts to play the wrong card type during the action phase'''
    def __init__(self, card):
        message = f'{card.name} is not an Action card and cannot be played right now'
        super().__init__(message)


class BuyPhaseError(Exception):
    '''Raised when a player attempts to buy a card that is too expensive'''
    def __init__(self, card):
        message = f'{card.name} is too expensive and cannot be purchased right now'
        super().__init__(message)


class Turn:
    def __init__(self, player, reaction=False):
        self.player = player

        self.player.turn = self

        self.actions_remaining = 1
        self.buys_remaining = 1
        self.coppers_remaining = 0

        self.action_phase = ActionPhase(turn=self)
        self.buy_phase = BuyPhase(turn=self)
        self.cleanup_phase = CleanupPhase(turn=self)

        self.start()

    def start(self):
        print(f"{self.player}'s turn!\n".upper())
        self.player.interactions.display_hand()
        self.action_phase.start()
        self.buy_phase.start()
        self.cleanup_phase.start()

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
            print(f'You have {self.turn.actions_remaining} actions. Select an action card to play.')
            card = self.player.interactions.choose_action_card_from_hand()
            if card is None:
                # The player is forfeiting their action phase
                print('Action phase forfeited.\n')
                return
            self.play(card)
        print('No actions left. Ending action phase.\n')

    def play(self, card):
        modifier = 'an' if card.name[0] in ['a', 'e', 'i', 'o', 'u'] else 'a'
        print(f'{self.player} played {modifier} {card}.\n')
        # Playing an action card uses one action
        self.turn.actions_remaining -= 1
        # Draw any additional cards specified on the card
        self.player.draw(quantity=card.extra_cards)
        # Add back any additional actions on the card
        self.turn.actions_remaining += card.extra_actions
        # Add any additional buys on the card
        self.turn.buys_remaining += card.extra_buys
        # Add any additional coppers on the card
        self.turn.coppers_remaining += card.extra_coppers
        # Add the card to the played cards area
        self.player.play(card)
        # Do whatever the card is supposed to do
        card.play()


class BuyPhase(Phase):
    def start(self):
        # Add up any coppers from player's hand
        for card in self.player.hand:
            if cards.CardType.TREASURE in card.types:
                self.turn.coppers_remaining += card.value
        # Buy cards
        while self.turn.buys_remaining > 0:
            print(f'You have {self.turn.coppers_remaining} Coppers and {self.turn.buys_remaining} buys. Select a card to buy.')
            card_class = self.player.interactions.choose_card_class_from_supply(max_cost=self.turn.coppers_remaining)
            if card_class is None:
                # The player is forfeiting their buy phase
                print('Buy phase forfeited.\n')
                return
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


class CleanupPhase(Phase):
    def start(self):
        self.player.cleanup()