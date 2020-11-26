import cards
import prettytable
from abc import ABCMeta, abstractmethod


class Interaction(metaclass=ABCMeta):
    def __init__(self, player):
        self.player = player

    def start(self):
        self.hand = self.player.hand
        self.discard_pile = self.player.discard_pile
        self.deck = self.player.deck
        self.supply = self.player.game.supply

    @abstractmethod
    def display_hand(self):
        pass

    @abstractmethod
    def display_discard_pile(self):
        pass

    @abstractmethod
    def choose_card_from_hand(self, force):
        pass

    @abstractmethod
    def choose_action_card_from_hand(self):
        pass

    @abstractmethod
    def choose_specific_card_class_from_hand(self, force, card_class):
        pass

    @abstractmethod
    def choose_card_from_discard_pile(self, force):
        pass

    @abstractmethod
    def choose_card_class_from_supply(self, max_cost, force):
        pass

    @abstractmethod
    def choose_yes_or_no(self):
        pass


class CLI(Interaction):
    def display_hand(self):
        print(f"{self.player}'s hand:\n")
        hand_table = prettytable.PrettyTable(hrules=prettytable.ALL)
        hand_table.field_names = ['Number', 'Card', 'Description']
        for idx, card in enumerate(self.hand):
            hand_table.add_row([idx + 1, card.name, card.description])
        print(hand_table)
        print('\n')

    def display_discard_pile(self):
        print(f"{self.player}'s discard pile:\n")
        discard_table = prettytable.PrettyTable(hrules=prettytable.ALL)
        discard_table.field_names = ['Number', 'Card', 'Description']
        for idx, card in enumerate(self.discard_pile):
            discard_table.add_row([idx + 1, card.name, card.description])
        print(discard_table)
        print('\n')

    def choose_card_from_hand(self, force):
        if not self.hand:
            return None
        while True:
            try:
                self.display_hand()
                if force:
                    card_num = int(input(f'Enter choice 1-{len(self.hand)}: '))
                    card_chosen = self.hand[card_num - 1]
                else:
                    card_num = int(input(f'Enter choice 1-{len(self.hand)} (0 to skip): '))
                    if card_num == 0:
                        return None
                    else:
                        card_chosen = self.hand[card_num - 1]
                return card_chosen
            except (IndexError, ValueError):
                print('That is not a valid choice.\n')

    def choose_action_card_from_hand(self):
        # Only action cards can be chosen
        playable_cards = [card for card in self.hand if cards.CardType.ACTION in card.types]
        if not playable_cards:
            return None
        while True:
            try:
                hand_table = prettytable.PrettyTable(hrules=prettytable.ALL)
                hand_table.field_names = ['Number', 'Card', 'Description']
                for idx, card in enumerate(playable_cards):
                    hand_table.add_row([idx + 1, card.name, card.description])
                print(hand_table)
                card_num = int(input(f'Enter choice 1-{len(playable_cards)} (0 to skip): '))
                if card_num == 0:
                    return None
                else:
                    card_to_play = playable_cards[card_num - 1]
                    return card_to_play
            except (IndexError, ValueError):
                print('That is not a valid choice.\n')

    def choose_specific_card_class_from_hand(self, force, card_class):
        if not any(type(card) == card_class for card in self.hand):
            return None
        # Find a card in the player's hand of the correct class
        for card in self.hand:
            if type(card) == card_class:
                break
        if force:
            return card
        else:
            print(f'Do you want to choose a {card_class.name} from your hand?\n')
            if self.choose_yes_or_no():
                return card
            else:
                return None

    def choose_card_from_discard_pile(self, force):
        if not self.discard_pile:
            print('There are no cards in your discard pile!\n')
            return None
        while True:
            try:
                self.display_discard_pile()
                if force:
                    card_num = int(input(f'Enter choice 1-{len(self.discard_pile)}: '))
                    card_chosen = self.discard_pile[card_num - 1]
                else:
                    card_num = int(input(f'Enter choice 1-{len(self.discard_pile)} (0 to skip): '))
                    if card_num == 0:
                        return None
                    else:
                        card_chosen = self.discard_pile[card_num - 1]
                return card_chosen
            except (IndexError, ValueError):
                print('That is not a valid choice.\n')

    def choose_card_class_from_supply(self, max_cost, force):
        while True:
            try:
                supply_table = prettytable.PrettyTable(hrules=prettytable.ALL)
                supply_table.field_names = ['Number', 'Card', 'Cost', 'Quantity', 'Description']
                # Only cards you can afford can be chosen (and with non-zero quantity)
                buyable_card_stacks = [card_class for card_class in self.supply.card_stacks if card_class.cost <= max_cost and self.supply.card_stacks[card_class].cards_remaining > 0]
                for idx, card_class in enumerate(buyable_card_stacks):
                    card_quantity = self.supply.card_stacks[card_class].cards_remaining
                    supply_table.add_row([idx + 1, card_class.name, card_class.cost, card_quantity, card_class.description])
                print(supply_table)
                if force:
                    card_num = int(input(f'Enter choice 1-{len(buyable_card_stacks)}: '))
                    card_to_buy = list(buyable_card_stacks)[card_num - 1]
                else:
                    card_num = int(input(f'Enter choice 1-{len(buyable_card_stacks)} (0 to skip): '))
                    if card_num == 0:
                        return None
                    else:
                        card_to_buy = list(buyable_card_stacks)[card_num - 1]
                return card_to_buy
            except (IndexError, ValueError):
                print('That is not a valid choice.\n')

    def choose_yes_or_no(self):
        while True:
            response = input('Enter choice Yes/No: ')
            if response.lower() in ['yes', 'y', 'no', 'n']:
                break
        if response.lower() in ['yes', 'y']:
            return True
        else:
            return False