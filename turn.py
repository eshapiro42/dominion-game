import cards
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from prettytable import PrettyTable


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
        self.player_mat = self.player.player_mat

        self.actions_remaining = 1
        self.buys_remaining = 1
        self.coppers_remaining = 0

        self.action_phase = ActionPhase(turn=self)
        self.buy_phase = BuyPhase(turn=self)
        self.cleanup_phase = CleanupPhase(turn=self)

        self.start()

    def start(self):
        print(f"{self.player}'s turn.")
        self.action_phase.start()
        self.buy_phase.start()
        self.cleanup_phase.start()


class Phase(metaclass=ABCMeta):
    def __init__(self, turn):
        self.turn = turn
        self.player = self.turn.player
        self.player_mat = self.turn.player.player_mat
        self.supply = self.player.game.supply
    
    def choose_from_hand(self):
        while True:
            try:
                hand = self.player_mat.hand
                hand_string = '\n'
                for idx, card in enumerate(hand):
                    hand_string += f'{idx + 1}: \t {card.name}\n'
                print('\nWhich card would you like to play?')
                print(hand_string)
                card_num = int(input(f'Enter choice (1-{len(hand)}): '))
                card_to_play = hand[card_num - 1]
                # Check that the card is an action card
                if not cards.CardType.ACTION in card_to_play.types:
                    raise ActionPhaseError(card_to_play)
                else:
                    return card_to_play
            except ActionPhaseError:
                print('That is not an action card!')
            except (IndexError, ValueError):
                print('That is not a valid choice!')

    def choose_from_supply(self, max_cost):
        while True:
            try:
                supply_table = PrettyTable()
                supply_table.field_names = ['Number', 'Card', 'Cost', 'Quantity']
                for idx, card_class in enumerate(self.supply.card_stacks):
                    card_name = card_class.name
                    card_quantity = self.supply.card_stacks[card_class].cards_remaining
                    card_cost = card_class.cost
                    supply_table.add_row([idx + 1, card_name, card_cost, card_quantity])
                print(f'\nYou have {max_cost} coppers. Which card would you like to buy?')
                print(supply_table)
                card_num = int(input(f'Enter choice (1-{len(self.supply.card_stacks)}): '))
                card_to_buy = list(self.supply.card_stacks)[card_num - 1]
                # Check that the card is not too expensive
                if card_to_buy.cost > max_cost:
                    raise BuyPhaseError(card_to_buy)
                return card_to_buy
            except BuyPhaseError:
                print('That card is too expensive!')
            except (IndexError, ValueError):
                print('That is not a valid choice!')

    @abstractmethod
    def start(self):
        pass


class ActionPhase(Phase):
    def start(self):
        while self.turn.actions_remaining > 0:
            # If there are no action cards in the player's hand, move on
            if not any(cards.CardType.ACTION in card.types for card in self.player_mat.hand):
                print('No action cards to play. Ending action phase.')
                return
            card = self.choose_from_hand()
            self.play(card)
        print('No actions left. Ending action phase.')

    def play(self, card):
        self.player_mat.play(card)
        # Playing an action card uses one action
        self.turn.actions_remaining -= 1
        # Draw any additional cards specified on the card
        self.player_mat.draw(quantity=card.extra_cards)
        # Add back any additional actions on the card
        self.turn.actions_remaining += card.extra_actions
        # Add any additional buys on the card
        self.turn.buys_remaining += card.extra_buys
        # Add any additional coppers on the card
        self.turn.coppers_remaining += card.extra_coppers
        # Do whatever the card is supposed to do
        card.play()


class BuyPhase(Phase):
    def start(self):
        # Add up any coppers from player's hand
        for card in self.player_mat.hand:
            if cards.CardType.TREASURE in card.types:
                self.turn.coppers_remaining += card.value
        # Buy cards
        while self.turn.buys_remaining > 0:
            card_class = self.choose_from_supply(max_cost=self.turn.coppers_remaining)
            self.buy(card_class)
        print('No buys left. Ending buy phase.')

    def buy(self, card_class):
        # Buying a card uses one buy
        self.turn.buys_remaining -= 1
        # Gain the desired card
        self.player_mat.gain(card_class)
        self.turn.coppers_remaining -= card_class.cost



class CleanupPhase(Phase):
    def start(self):
        self.player_mat.cleanup()