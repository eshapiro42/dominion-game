import cards
import prettytable
from abc import ABCMeta, abstractmethod
from flask_socketio import SocketIO
from math import inf


class Broadcast(metaclass=ABCMeta):
    def __init__(self, socketio=None, room=None):
        self.socketio = socketio
        self.room = room

    @abstractmethod
    def __call__(self, message):
        pass


class Interaction(metaclass=ABCMeta):
    def __init__(self, player, socketio=None, sid=None):
        self.player = player
        self.socketio = socketio
        self.sid = sid

    def start(self):
        self.hand = self.player.hand
        self.discard_pile = self.player.discard_pile
        self.deck = self.player.deck
        self.supply = self.player.game.supply
        self.game = self.player.game
        self.room = self.player.game.room

    # @abstractmethod
    # def display_hand(self):
    #     pass

    # @abstractmethod
    # def display_discard_pile(self):
    #     pass

    # @abstractmethod
    # def choose_card_from_hand(self, force):
    #     pass

    # @abstractmethod
    # def choose_action_card_from_hand(self):
    #     pass

    # @abstractmethod
    # def choose_specific_card_class_from_hand(self, force, card_class):
    #     pass

    # @abstractmethod
    # def choose_card_from_discard_pile(self, force):
    #     pass

    # @abstractmethod
    # def choose_card_class_from_supply(self, max_cost, force):
    #     pass

    # @abstractmethod
    # def choose_yes_or_no(self):
    #     pass


class CLIBroadcast(Broadcast):
    def __call__(self, message):
        print(self.message)
        print()


class CLIInteraction(Interaction):
    def display_hand(self):
        print(f"{self.player}'s hand:\n")
        hand_table = prettytable.PrettyTable(hrules=prettytable.ALL)
        hand_table.field_names = ['Number', 'Card', 'Type', 'Description']
        for idx, card in enumerate(self.hand):
            types = ', '.join([type.name.lower().capitalize() for type in card.types])
            hand_table.add_row([idx + 1, card.name, types, card.description])
        print(hand_table)
        print()

    def display_discard_pile(self):
        print(f"{self.player}'s discard pile:\n")
        discard_table = prettytable.PrettyTable(hrules=prettytable.ALL)
        discard_table.field_names = ['Number', 'Card', 'Type', 'Description']
        for idx, card in enumerate(self.discard_pile):
            types = ', '.join([type.name.lower().capitalize() for type in card.types])
            discard_table.add_row([idx + 1, card.name, types, card.description])
        print(discard_table)
        print()

    def choose_card_from_hand(self, prompt, force):
        print(prompt)
        print()
        if not self.hand:
            print('There are no cards in your hand.\n')
            return None
        while True:
            try:
                self.display_hand()
                if force:
                    card_num = int(input(f'Enter choice 1-{len(self.hand)}: '))
                    print()
                    card_chosen = self.hand[card_num - 1]
                else:
                    card_num = int(input(f'Enter choice 1-{len(self.hand)} (0 to skip): '))
                    print()
                    if card_num == 0:
                        return None
                    else:
                        card_chosen = self.hand[card_num - 1]
                return card_chosen
            except (IndexError, ValueError):
                print('That is not a valid choice.\n')

    def choose_specific_card_class_from_hand(self, prompt, force, card_class):
        print(prompt)
        print()
        if not any(type(card) == card_class for card in self.hand):
            print(f'There are no {card_class} cards in your hand.\n')
            return None
        # Find a card in the player's hand of the correct class
        for card in self.hand:
            if type(card) == card_class:
                break
        if force:
            return card
        else:
            prompt = f'Do you want to choose a {card_class.name} from your hand?'
            if self.choose_yes_or_no(prompt=prompt):
                return card
            else:
                return None

    def choose_specific_card_type_from_hand(self, prompt, card_type):
        print(prompt)
        print()
        # Only cards of the correct type can be chosen
        playable_cards = [card for card in self.hand if card_type in card.types]
        if not playable_cards:
            print(f'There are no {card_type.name.lower().capitalize()} cards in your hand.\n')
            return None
        while True:
            try:
                hand_table = prettytable.PrettyTable(hrules=prettytable.ALL)
                hand_table.field_names = ['Number', 'Card', 'Type', 'Description']
                for idx, card in enumerate(playable_cards):
                    types = ', '.join([type.name.lower().capitalize() for type in card.types])
                    hand_table.add_row([idx + 1, card.name, types, card.description])
                print(hand_table)
                card_num = int(input(f'Enter choice 1-{len(playable_cards)} (0 to skip): '))
                print()
                if card_num == 0:
                    return None
                else:
                    card_to_play = playable_cards[card_num - 1]
                    return card_to_play
            except (IndexError, ValueError):
                print('That is not a valid choice.\n')

    def choose_card_from_discard_pile(self, prompt, force):
        print(prompt)
        print()
        if not self.discard_pile:
            print('There are no cards in your discard pile!\n')
            return None
        while True:
            try:
                self.display_discard_pile()
                if force:
                    card_num = int(input(f'Enter choice 1-{len(self.discard_pile)}: '))
                    print()
                    card_chosen = self.discard_pile[card_num - 1]
                else:
                    card_num = int(input(f'Enter choice 1-{len(self.discard_pile)} (0 to skip): '))
                    print()
                    if card_num == 0:
                        return None
                    else:
                        card_chosen = self.discard_pile[card_num - 1]
                return card_chosen
            except (IndexError, ValueError):
                print('That is not a valid choice.\n')

    def choose_card_class_from_supply(self, prompt, max_cost, force):
        print(prompt)
        print()
        while True:
            try:
                supply_table = prettytable.PrettyTable(hrules=prettytable.ALL)
                supply_table.field_names = ['Number', 'Card', 'Cost', 'Type', 'Quantity', 'Description']
                # Only cards you can afford can be chosen (and with non-zero quantity)
                stacks = self.supply.card_stacks
                buyable_card_stacks = [card_class for card_class in stacks if card_class.cost <= max_cost and stacks[card_class].cards_remaining > 0]
                # for idx, card_class in enumerate(sorted(buyable_card_stacks, key=lambda x: (x.types[0].value, x.cost))):
                for idx, card_class in enumerate(buyable_card_stacks):
                    types = ', '.join([type.name.lower().capitalize() for type in card_class.types])
                    card_quantity = stacks[card_class].cards_remaining
                    supply_table.add_row([idx + 1, card_class.name, card_class.cost, types, card_quantity, card_class.description])
                print(supply_table)
                if force:
                    card_num = int(input(f'Enter choice 1-{len(buyable_card_stacks)}: '))
                    print()
                    card_to_buy = list(buyable_card_stacks)[card_num - 1]
                else:
                    card_num = int(input(f'Enter choice 1-{len(buyable_card_stacks)} (0 to skip): '))
                    print()
                    if card_num == 0:
                        return None
                    else:
                        card_to_buy = list(buyable_card_stacks)[card_num - 1]
                return card_to_buy
            except (IndexError, ValueError):
                print('That is not a valid choice.\n')

    def choose_specific_card_type_from_supply(self, prompt, max_cost, card_type, force):
        print(prompt)
        print()
        while True:
            try:
                supply_table = prettytable.PrettyTable(hrules=prettytable.ALL)
                supply_table.field_names = ['Number', 'Card', 'Cost', 'Type', 'Quantity', 'Description']
                # Only cards you can afford can be chosen (and with non-zero quantity)
                stacks = self.supply.card_stacks
                buyable_card_stacks = [card_class for card_class in stacks if card_class.cost <= max_cost and stacks[card_class].cards_remaining > 0 and card_type in card_class.types]
                # for idx, card_class in enumerate(sorted(buyable_card_stacks, key=lambda x: (x.types[0].value, x.cost))):
                for idx, card_class in enumerate(buyable_card_stacks):
                    types = ', '.join([type.name.lower().capitalize() for type in card_class.types])
                    card_quantity = stacks[card_class].cards_remaining
                    supply_table.add_row([idx + 1, card_class.name, card_class.cost, types, card_quantity, card_class.description])
                print(supply_table)
                if force:
                    card_num = int(input(f'Enter choice 1-{len(buyable_card_stacks)}: '))
                    print()
                    card_to_buy = list(buyable_card_stacks)[card_num - 1]
                else:
                    card_num = int(input(f'Enter choice 1-{len(buyable_card_stacks)} (0 to skip): '))
                    print()
                    if card_num == 0:
                        return None
                    else:
                        card_to_buy = list(buyable_card_stacks)[card_num - 1]
                return card_to_buy
            except (IndexError, ValueError):
                print('That is not a valid choice.\n')

    def choose_yes_or_no(self, prompt):
        print(prompt)
        print()
        while True:
            response = input('Enter choice Yes/No: ')
            print()
            if response.lower() in ['yes', 'y', 'no', 'n']:
                break
        if response.lower() in ['yes', 'y']:
            return True
        else:
            return False

    def choose_from_options(self, prompt, options, force):
        print(prompt)
        print()
        while True:
            options_table = prettytable.PrettyTable(hrules=prettytable.ALL)
            options_table.field_names = ['Number', 'Option']
            for idx, option in enumerate(options):
                options_table.add_row([idx + 1, option])
            try:
                print(options_table)
                if force:
                    response_num = int(input(f'Enter choice 1-{len(options)}: '))
                    print()
                    response = options[response_num - 1]
                else:
                    response_num = int(input(f'Enter choice 0-{len(options)} (0 to skip): '))
                    print()
                    if response_num == 0:
                        return None
                    else:
                        response = options[response_num - 1]
                return response
            except (IndexError, ValueError):
                print('That is not a valid choice.\n')


class NetworkedCLIBroadcast(Broadcast):
    def __call__(self, message):
        self.socketio.send('', room=self.room)
        self.socketio.send(message, room=self.room)


class NetworkedCLIInteraction(Interaction):
    def enter_choice(self, prompt):
        self.socketio.send('', to=self.sid)
        return self.socketio.call('enter choice', {'prompt': prompt}, to=self.sid, timeout=None)

    def send(self, message):
        self.socketio.send('', to=self.sid)
        self.socketio.send(message, to=self.sid)

    def display_hand(self):
        self.send('Your hand:')
        hand_table = prettytable.PrettyTable(hrules=prettytable.ALL)
        hand_table.field_names = ['Number', 'Card', 'Type', 'Description']
        for idx, card in enumerate(self.hand):
            types = ', '.join([type.name.lower().capitalize() for type in card.types])
            hand_table.add_row([idx + 1, card.name, types, card.description])
        self.send(hand_table.get_string())

    def display_discard_pile(self):
        self.send('Your discard pile:')
        discard_table = prettytable.PrettyTable(hrules=prettytable.ALL)
        discard_table.field_names = ['Number', 'Card', 'Type', 'Description']
        for idx, card in enumerate(self.discard_pile):
            types = ', '.join([type.name.lower().capitalize() for type in card.types])
            discard_table.add_row([idx + 1, card.name, types, card.description])
        self.send(discard_table.get_string())

    def choose_card_from_hand(self, prompt, force):
        self.send(prompt)
        if not self.hand:
            self.send('There are no cards in your hand.')
            return None
        while True:
            try:
                self.display_hand()
                if force:
                    prompt = f'Enter choice 1-{len(self.hand)}: '
                    card_num = self.enter_choice(prompt)
                    card_chosen = self.hand[card_num - 1]
                else:
                    prompt = f'Enter choice 1-{len(self.hand)} (0 to skip): '
                    card_num = self.enter_choice(prompt)
                    if card_num == 0:
                        return None
                    else:
                        card_chosen = self.hand[card_num - 1]
                return card_chosen
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')

    def choose_specific_card_class_from_hand(self, prompt, force, card_class):
        self.send(prompt)
        if not any(type(card) == card_class for card in self.hand):
            self.send(f'There are no {card_class} cards in your hand.')
            return None
        # Find a card in the player's hand of the correct class
        for card in self.hand:
            if type(card) == card_class:
                break
        if force:
            return card
        else:
            prompt = f'Do you want to choose a {card_class.name} from your hand?'
            if self.choose_yes_or_no(prompt):
                return card
            else:
                return None

    def choose_specific_card_type_from_hand(self, prompt, card_type):
        self.send(prompt)
        # Only cards of the correct type can be chosen
        playable_cards = [card for card in self.hand if card_type in card.types]
        if not playable_cards:
            self.send(f'There are no {card_type.name.lower().capitalize()} cards in your hand.')
            return None
        while True:
            try:
                hand_table = prettytable.PrettyTable(hrules=prettytable.ALL)
                hand_table.field_names = ['Number', 'Card', 'Type', 'Description']
                for idx, card in enumerate(playable_cards):
                    types = ', '.join([type.name.lower().capitalize() for type in card.types])
                    hand_table.add_row([idx + 1, card.name, types, card.description])
                self.send(hand_table.get_string())
                prompt = f'Enter choice 1-{len(playable_cards)} (0 to skip): '
                card_num = self.enter_choice(prompt)
                if card_num == 0:
                    return None
                else:
                    card_to_play = playable_cards[card_num - 1]
                    return card_to_play
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')

    def choose_card_from_discard_pile(self, prompt, force):
        self.send(prompt)
        if not self.discard_pile:
            self.send('There are no cards in your discard pile!')
            return None
        while True:
            try:
                self.display_discard_pile()
                if force:
                    prompt = f'Enter choice 1-{len(self.discard_pile)}: '
                    card_num = self.enter_choice(prompt)
                    card_chosen = self.discard_pile[card_num - 1]
                else:
                    prompt = f'Enter choice 1-{len(self.discard_pile)} (0 to skip): '
                    card_num = self.enter_choice(prompt)
                    if card_num == 0:
                        return None
                    else:
                        card_chosen = self.discard_pile[card_num - 1]
                return card_chosen
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')        

    def choose_card_class_from_supply(self, prompt, max_cost, force):
        while True:
            self.send(prompt)
            try:
                supply_table = prettytable.PrettyTable(hrules=prettytable.ALL)
                supply_table.field_names = ['Number', 'Card', 'Cost', 'Type', 'Quantity', 'Description']
                # Only cards you can afford can be chosen (and with non-zero quantity)
                stacks = self.supply.card_stacks
                buyable_card_stacks = [card_class for card_class in stacks if card_class.cost <= max_cost and stacks[card_class].cards_remaining > 0]
                # for idx, card_class in enumerate(sorted(buyable_card_stacks, key=lambda x: (x.types[0].value, x.cost))):
                for idx, card_class in enumerate(buyable_card_stacks):
                    types = ', '.join([type.name.lower().capitalize() for type in card_class.types])
                    card_quantity = stacks[card_class].cards_remaining
                    supply_table.add_row([idx + 1, card_class.name, card_class.cost, types, card_quantity, card_class.description])
                self.send(supply_table.get_string())       
                if force:
                    card_num = self.enter_choice(f'Enter choice 1-{len(buyable_card_stacks)}: ')
                    card_to_buy = list(buyable_card_stacks)[card_num - 1]
                else:
                    card_num = self.enter_choice(f'Enter choice 1-{len(buyable_card_stacks)} (0 to skip): ')
                    if card_num == 0:
                        return None
                    else:
                        card_to_buy = list(buyable_card_stacks)[card_num - 1]
                return card_to_buy
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')        

    def choose_specific_card_type_from_supply(self, prompt, max_cost, card_type, force):
        self.send(prompt)
        while True:
            try:
                supply_table = prettytable.PrettyTable(hrules=prettytable.ALL)
                supply_table.field_names = ['Number', 'Card', 'Cost', 'Type', 'Quantity', 'Description']
                # Only cards you can afford can be chosen (and with non-zero quantity)
                stacks = self.supply.card_stacks
                buyable_card_stacks = [card_class for card_class in stacks if card_class.cost <= max_cost and stacks[card_class].cards_remaining > 0 and card_type in card_class.types]
                # for idx, card_class in enumerate(sorted(buyable_card_stacks, key=lambda x: (x.types[0].value, x.cost))):
                for idx, card_class in enumerate(buyable_card_stacks):
                    types = ', '.join([type.name.lower().capitalize() for type in card_class.types])
                    card_quantity = stacks[card_class].cards_remaining
                    supply_table.add_row([idx + 1, card_class.name, card_class.cost, types, card_quantity, card_class.description])
                self.send(supply_table.get_string())
                if force:
                    prompt = f'Enter choice 1-{len(buyable_card_stacks)}: '
                    card_num = self.enter_choice(prompt)
                    card_to_buy = list(buyable_card_stacks)[card_num - 1]
                else:
                    prompt = f'Enter choice 1-{len(buyable_card_stacks)} (0 to skip): '
                    card_num = self.enter_choice(prompt)
                    if card_num == 0:
                        return None
                    else:
                        card_to_buy = list(buyable_card_stacks)[card_num - 1]
                return card_to_buy
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')        

    def choose_yes_or_no(self, prompt):
        self.send(prompt)
        while True:
            response = self.enter_choice('Enter choice (Yes/No): ')
            if response.lower() in ['yes', 'y', 'no', 'n']:
                break
        if response.lower() in ['yes', 'y']:
            return True
        else:
            return False

    def choose_from_options(self, prompt, options, force):
        self.send(prompt)
        while True:
            options_table = prettytable.PrettyTable(hrules=prettytable.ALL)
            options_table.field_names = ['Number', 'Option']
            for idx, option in enumerate(options):
                options_table.add_row([idx + 1, option])
            try:
                self.send(options_table.get_string())
                if force:
                    prompt = f'Enter choice 1-{len(options)}: '
                    response_num = self.enter_choice(prompt)
                    response = options[response_num - 1]
                else:
                    prompt = f'Enter choice 0-{len(options)} (0 to skip): '
                    response_num = self.enter_choice(prompt)
                    if response_num == 0:
                        return None
                    else:
                        response = options[response_num - 1]
                return response
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')