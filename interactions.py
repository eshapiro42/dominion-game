import cards
import prettytable
import random
import time
from abc import ABCMeta, abstractmethod
from copy import deepcopy


class Broadcast(metaclass=ABCMeta):
    def __init__(self, game, socketio=None, room=None):
        self.game = game
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

    @abstractmethod
    def send(self, message):
        pass

    @abstractmethod
    def display_hand(self):
        pass

    @abstractmethod
    def display_discard_pile(self):
        pass

    @abstractmethod
    def choose_card_from_hand(self, prompt, force):
        pass

    @abstractmethod
    def choose_specific_card_class_from_hand(self, prompt, force, card_class):
        pass

    @abstractmethod
    def choose_specific_card_type_from_hand(self, prompt, card_type):
        pass

    @abstractmethod
    def choose_card_from_discard_pile(self, prompt, force):
        pass

    @abstractmethod
    def choose_card_class_from_supply(self, prompt, max_cost, force):
        pass

    @abstractmethod
    def choose_specific_card_type_from_supply(self, prompt, max_cost, card_type, force):
        pass

    @abstractmethod
    def choose_yes_or_no(self, prompt):
        pass

    @abstractmethod
    def choose_from_options(self, prompt, options, force):
        pass


###############################
# LOCAL CLI INTERACTION LAYER #
###############################


class CLIBroadcast(Broadcast):
    def __call__(self, message):
        print(message)
        print()


class CLIInteraction(Interaction):
    def send(self, message):
        print(message)
        print()

    def display_supply(self):
        supply_table = self.supply.get_table()
        self.send(supply_table.get_string())

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


###################################
# NETWORKED CLI INTERACTION LAYER #
###################################


class NetworkedCLIBroadcast(Broadcast):
    def __call__(self, message):
        for player in self.game.players:
            player.interactions.send(message)


class NetworkedCLIInteraction(Interaction):
    def enter_choice(self, prompt):
        prompt = f'\n{prompt}'
        return self.socketio.call('enter choice', {'prompt': prompt}, to=self.sid, timeout=None)

    def send(self, message):
        message = f'\n{message}'
        self.socketio.send(message, to=self.sid)

    def get_hand_string(self):
        hand_table = prettytable.PrettyTable(hrules=prettytable.ALL)
        hand_table.field_names = ['Number', 'Card', 'Type', 'Description']
        for idx, card in enumerate(self.hand):
            types = ', '.join([type.name.lower().capitalize() for type in card.types])
            hand_table.add_row([idx + 1, card.name, types, card.description])
        return hand_table.get_string()

    def get_discard_pile_string(self):
        discard_table = prettytable.PrettyTable(hrules=prettytable.ALL)
        discard_table.field_names = ['Number', 'Card', 'Type', 'Description']
        for idx, card in enumerate(self.discard_pile):
            types = ', '.join([type.name.lower().capitalize() for type in card.types])
            discard_table.add_row([idx + 1, card.name, types, card.description])
        return discard_table.get_string()

    def display_supply(self):
        supply_table = self.supply.get_table()
        self.send(supply_table.get_string())

    def display_hand(self):
        hand_string = f'Your hand:\n{self.get_hand_string()}'
        self.send(hand_string)

    def display_discard_pile(self):
        discard_string = f'Your discard pile:\n{self.get_discard_pile_string()}'
        self.send(discard_string)

    def choose_card_from_hand(self, prompt, force):
        if not self.hand:
            self.send('There are no cards in your hand.')
            return None
        while True:
            try:
                _prompt = f'{prompt}\n{self.get_hand_string()}'
                if force:
                    _prompt += f'\nEnter choice 1-{len(self.hand)}: '
                    card_num = self.enter_choice(_prompt)
                    card_chosen = self.hand[card_num - 1]
                else:
                    _prompt += f'\nEnter choice 1-{len(self.hand)} (0 to skip): '
                    card_num = self.enter_choice(_prompt)
                    if card_num == 0:
                        return None
                    else:
                        card_chosen = self.hand[card_num - 1]
                return card_chosen
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')

    def choose_specific_card_class_from_hand(self, prompt, force, card_class):
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
            _prompt = f'{prompt}\nDo you want to choose a {card_class.name} from your hand?'
            if self.choose_yes_or_no(_prompt):
                return card
            else:
                return None

    def choose_specific_card_type_from_hand(self, prompt, card_type):
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
                _prompt = f'{prompt}\n{hand_table.get_string()}'
                _prompt += f'\nEnter choice 1-{len(playable_cards)} (0 to skip): '
                card_num = self.enter_choice(_prompt)
                if card_num == 0:
                    return None
                else:
                    card_to_play = playable_cards[card_num - 1]
                    return card_to_play
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')

    def choose_card_from_discard_pile(self, prompt, force):
        if not self.discard_pile:
            self.send('There are no cards in your discard pile!')
            return None
        while True:
            try:
                _prompt = self.get_discard_pile_string()
                if force:
                    _prompt += f'\n{prompt}\nEnter choice 1-{len(self.discard_pile)}: '
                    card_num = self.enter_choice(_prompt)
                    card_chosen = self.discard_pile[card_num - 1]
                else:
                    _prompt += f'\n{prompt}\nEnter choice 1-{len(self.discard_pile)} (0 to skip): '
                    card_num = self.enter_choice(_prompt)
                    if card_num == 0:
                        return None
                    else:
                        card_chosen = self.discard_pile[card_num - 1]
                return card_chosen
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')        

    def choose_card_class_from_supply(self, prompt, max_cost, force):
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
                _prompt = f'{prompt}\n{supply_table.get_string()}'
                if force:
                    _prompt += f'\nEnter choice 1-{len(buyable_card_stacks)}: '
                    card_num = self.enter_choice(_prompt)
                    card_to_buy = list(buyable_card_stacks)[card_num - 1]
                else:
                    _prompt += f'\nEnter choice 1-{len(buyable_card_stacks)} (0 to skip): '
                    card_num = self.enter_choice(_prompt)
                    if card_num == 0:
                        return None
                    else:
                        card_to_buy = list(buyable_card_stacks)[card_num - 1]
                return card_to_buy
            except (IndexError, ValueError, TypeError):
                self.send('That is not a valid choice.')        

    def choose_specific_card_type_from_supply(self, prompt, max_cost, card_type, force):
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
                _prompt = f'{prompt}\n{supply_table.get_string()}'
                if force:
                    _prompt += f'\nEnter choice 1-{len(buyable_card_stacks)}: '
                    card_num = self.enter_choice(_prompt)
                    card_to_buy = list(buyable_card_stacks)[card_num - 1]
                else:
                    _prompt += f'\nEnter choice 1-{len(buyable_card_stacks)} (0 to skip): '
                    card_num = self.enter_choice(_prompt)
                    if card_num == 0:
                        return None
                    else:
                        card_to_buy = list(buyable_card_stacks)[card_num - 1]
                return card_to_buy
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')        

    def choose_yes_or_no(self, prompt):
        while True:
            try:
                _prompt = f'{prompt}\nEnter choice (Yes/No): '
                response = self.socketio.call('choose yes or no', {'prompt': _prompt}, to=self.sid, timeout=None)
                if response.lower() in ['yes', 'y', 'no', 'n']:
                    break
            except AttributeError:
                self.send(f'{response} is not a valid choice. WTF???')
        if response.lower() in ['yes', 'y']:
            return True
        else:
            return False

    def choose_from_options(self, prompt, options, force):
        while True:
            options_table = prettytable.PrettyTable(hrules=prettytable.ALL)
            options_table.field_names = ['Number', 'Option']
            for idx, option in enumerate(options):
                options_table.add_row([idx + 1, option])
            try:
                _prompt = f'{prompt}\n{options_table.get_string()}'
                if force:
                    _prompt += f'\nEnter choice 1-{len(options)}: '
                    response_num = self.enter_choice(_prompt)
                    response = options[response_num - 1]
                else:
                    _prompt += f'\nEnter choice 0-{len(options)} (0 to skip): '
                    response_num = self.enter_choice(_prompt)
                    if response_num == 0:
                        return None
                    else:
                        response = options[response_num - 1]
                return response
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')


##################################################
# AUTOMATIC INTERACTION LAYER FOR STRESS TESTING #
##################################################


class AutoInteraction(Interaction):
    def send(self, message):
        # TODO: Turn off printing (useful for debugging)
        print(message)
        print()

    def display_supply(self):
        supply_table = self.supply.get_table()
        self.send(supply_table.get_string())

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
                    print(f'Enter choice 1-{len(self.hand)}: ', end='')
                    choices = range(1, len(self.hand) + 1)
                    # Weight options by cost (more expensive are more likely to be chosen)
                    weights = [card.cost * 5 for card in self.hand]
                    card_num = random.choices(choices, weights, k=1)[0]
                    print(card_num)
                    print()
                    card_chosen = self.hand[card_num - 1]
                else:
                    print(f'Enter choice 1-{len(self.hand)} (0 to skip): ', end='')
                    choices = range(0, len(self.hand) + 1)
                    weights = [1] + [card.cost * 5 for card in self.hand]
                    card_num = random.choices(choices, weights, k=1)[0]
                    print(card_num)
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
                print(f'Enter choice 1-{len(playable_cards)} (0 to skip): ', end='')
                choices = range(0, len(playable_cards) + 1)
                # Weight options equally (except for skip)
                weights = [1 if num == 0 else 100 for num in choices]
                card_num = random.choices(choices, weights, k=1)[0]
                print(card_num)
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
                    print(f'Enter choice 1-{len(self.discard_pile)}: ', end='')
                    # Weight options by cost
                    choices = range(1, len(self.discard_pile) + 1)
                    weights = [card.cost * 5 for card in self.discard_pile]
                    card_num = random.choices(choices, weights, k=1)[0]
                    print(card_num)
                    print()
                    card_chosen = self.discard_pile[card_num - 1]
                else:
                    print(f'Enter choice 1-{len(self.discard_pile)} (0 to skip): ', end='')
                    choices = range(0, len(self.discard_pile) + 1)
                    weights = [1] + [card.cost * 5 for card in self.discard_pile]
                    card_num = random.choices(choices, weights, k=1)[0]
                    print(card_num)
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
                    print(f'Enter choice 1-{len(buyable_card_stacks)}: ', end='')
                    choices = range(1, len(buyable_card_stacks) + 1)
                    # Weight by cost (more expensive are more likely, coppers and estates are unlikely)
                    weights = [0 if cards.CardType.CURSE in card.types else 1 if type(card) == cards.Copper or type(card) == cards.Estate else card.cost * 5 for card in buyable_card_stacks]
                    card_num = random.choices(choices, weights, k=1)[0]
                    print(card_num)
                    print()
                    card_to_buy = list(buyable_card_stacks)[card_num - 1]
                else:
                    print(f'Enter choice 1-{len(buyable_card_stacks)} (0 to skip): ', end='')
                    choices = range(0, len(buyable_card_stacks) + 1)
                    weights = [1] + [0 if cards.CardType.CURSE in card.types else 1 if type(card) == cards.Copper or type(card) == cards.Estate else card.cost * 5 for card in buyable_card_stacks]
                    card_num = random.choices(choices, weights, k=1)[0]
                    print(card_num)
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
                    print(f'Enter choice 1-{len(buyable_card_stacks)}: ', end='')
                    choices = range(1, len(buyable_card_stacks) + 1)
                    # Weight by cost (more expensive is more likely)
                    weights = [card.cost * 5 for card in buyable_card_stacks]
                    card_num = random.choices(choices, weights, k=1)[0]
                    print(card_num)
                    print()
                    card_to_buy = list(buyable_card_stacks)[card_num - 1]
                else:
                    print(f'Enter choice 1-{len(buyable_card_stacks)} (0 to skip): ', end='')
                    choices = range(0, len(buyable_card_stacks) + 1)
                    weights = [1] + [card.cost * 5 for card in buyable_card_stacks]
                    card_num = random.choices(choices, weights, k=1)[0]
                    print(card_num)
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
            print('Enter choice Yes/No: ', end='')
            # 50-50 chance
            response = random.choice(['Yes', 'No'])
            print(response)
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
                    print(f'Enter choice 1-{len(options)}: ', end='')
                    choices = range(1, len(options) + 1)
                    # Higher options more likely
                    weights = choices
                    response_num = random.choices(choices, weights, k=1)[0]
                    print(response_num)
                    print()
                    response = options[response_num - 1]
                else:
                    print(f'Enter choice 0-{len(options)} (0 to skip): ', end='')
                    choices = range(0, len(options) + 1)
                    # Higher options more likely
                    weights = [1] + choices
                    response_num = random.choices(choices, weights, k=1)[0]
                    print(response_num)
                    print()
                    if response_num == 0:
                        return None
                    else:
                        response = options[response_num - 1]
                return response
            except (IndexError, ValueError):
                print('That is not a valid choice.\n')


#############################
# BROWSER INTERACTION LAYER #
#############################


class BrowserInteraction(Interaction):
    choice = None

    def get_choice(self, choice):
        self.choice = choice

    def enter_choice(self, prompt):
        self.socketio.emit('enter choice', {'prompt': prompt}, to=self.sid, callback=self.get_choice)
        while self.choice is None:
            self.socketio.sleep(0.1)
        choice = deepcopy(self.choice)
        self.choice = None
        return choice

    def send(self, message):
        message = f'\n{message}\n'
        self.socketio.send(message, to=self.sid)

    def get_supply_string(self):
        supply_table = self.supply.get_table()
        while True:
            try:
                return supply_table.get_html_string()
            except TypeError: 
                pass

    def get_hand_string(self):
        hand_table = prettytable.PrettyTable(hrules=prettytable.ALL)
        hand_table.field_names = ['Number', 'Card', 'Type', 'Description']
        for idx, card in enumerate(self.hand):
            types = ', '.join([type.name.lower().capitalize() for type in card.types])
            hand_table.add_row([idx + 1, card.name, types, card.description])
        while True:
            try:
                return hand_table.get_html_string()
            except TypeError:
                pass

    def get_discard_pile_string(self):
        discard_table = prettytable.PrettyTable(hrules=prettytable.ALL)
        discard_table.field_names = ['Number', 'Card', 'Type', 'Description']
        for idx, card in enumerate(self.discard_pile):
            types = ', '.join([type.name.lower().capitalize() for type in card.types])
            discard_table.add_row([idx + 1, card.name, types, card.description])
        while True:
            try:
                return discard_table.get_html_string()
            except TypeError:
                pass

    def display_supply(self):
        supply_string = f'Supply:\n{self.get_supply_string()}'
        self.send(supply_string)

    def display_hand(self):
        hand_string = f'Your hand:\n{self.get_hand_string()}'
        self.send(hand_string)

    def display_discard_pile(self):
        discard_string = f'Your discard pile:\n{self.get_discard_pile_string()}'
        self.send(discard_string)

    def choose_card_from_hand(self, prompt, force):
        if not self.hand:
            self.send('There are no cards in your hand.')
            return None
        while True:
            try:
                _prompt = f'{prompt}\n{self.get_hand_string()}'
                if force:
                    _prompt += f'\nEnter choice 1-{len(self.hand)}: '
                    card_num = self.enter_choice(_prompt)
                    card_chosen = self.hand[card_num - 1]
                else:
                    _prompt += f'\nEnter choice 1-{len(self.hand)} (0 to skip): '
                    card_num = self.enter_choice(_prompt)
                    if card_num == 0:
                        return None
                    else:
                        card_chosen = self.hand[card_num - 1]
                return card_chosen
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')

    def choose_specific_card_class_from_hand(self, prompt, force, card_class):
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
            _prompt = f'{prompt}\nDo you want to choose a {card_class.name} from your hand?'
            if self.choose_yes_or_no(_prompt):
                return card
            else:
                return None

    def choose_specific_card_type_from_hand(self, prompt, card_type):
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
                while True:
                    try:
                        _prompt = f'{prompt}\n{hand_table.get_html_string()}'
                        break
                    except TypeError:
                        pass
                _prompt += f'\nEnter choice 1-{len(playable_cards)} (0 to skip): '
                card_num = self.enter_choice(_prompt)
                if card_num == 0:
                    return None
                else:
                    card_to_play = playable_cards[card_num - 1]
                    return card_to_play
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')

    def choose_card_from_discard_pile(self, prompt, force):
        if not self.discard_pile:
            self.send('There are no cards in your discard pile!')
            return None
        while True:
            try:
                _prompt = self.get_discard_pile_string()
                if force:
                    _prompt += f'\n{prompt}\nEnter choice 1-{len(self.discard_pile)}: '
                    card_num = self.enter_choice(_prompt)
                    card_chosen = self.discard_pile[card_num - 1]
                else:
                    _prompt += f'\n{prompt}\nEnter choice 1-{len(self.discard_pile)} (0 to skip): '
                    card_num = self.enter_choice(_prompt)
                    if card_num == 0:
                        return None
                    else:
                        card_chosen = self.discard_pile[card_num - 1]
                return card_chosen
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')        

    def choose_card_class_from_supply(self, prompt, max_cost, force):
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
                while True:
                    try:
                        _prompt = f'{prompt}\n{supply_table.get_html_string()}'
                        break
                    except TypeError:
                        pass
                if force:
                    _prompt += f'\nEnter choice 1-{len(buyable_card_stacks)}: '
                    card_num = self.enter_choice(_prompt)
                    card_to_buy = list(buyable_card_stacks)[card_num - 1]
                else:
                    _prompt += f'\nEnter choice 1-{len(buyable_card_stacks)} (0 to skip): '
                    card_num = self.enter_choice(_prompt)
                    if card_num == 0:
                        return None
                    else:
                        card_to_buy = list(buyable_card_stacks)[card_num - 1]
                return card_to_buy
            except (IndexError, ValueError, TypeError):
                self.send('That is not a valid choice.')        

    def choose_specific_card_type_from_supply(self, prompt, max_cost, card_type, force):
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
                while True:
                    try:
                        _prompt = f'{prompt}\n{supply_table.get_html_string()}'
                        break
                    except TypeError:
                        pass
                if force:
                    _prompt += f'\nEnter choice 1-{len(buyable_card_stacks)}: '
                    card_num = self.enter_choice(_prompt)
                    card_to_buy = list(buyable_card_stacks)[card_num - 1]
                else:
                    _prompt += f'\nEnter choice 1-{len(buyable_card_stacks)} (0 to skip): '
                    card_num = self.enter_choice(_prompt)
                    if card_num == 0:
                        return None
                    else:
                        card_to_buy = list(buyable_card_stacks)[card_num - 1]
                return card_to_buy
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')        

    def choose_yes_or_no(self, prompt):
        while True:
            try:
                _prompt = f'{prompt}\nEnter choice (Yes/No): '
                response = self.socketio.call('choose yes or no', {'prompt': _prompt}, to=self.sid, timeout=None)
                if response.lower() in ['yes', 'y', 'no', 'n']:
                    break
            except AttributeError:
                self.send(f'{response} is not a valid choice. WTF???')
        if response.lower() in ['yes', 'y']:
            return True
        else:
            return False

    def choose_from_options(self, prompt, options, force):
        while True:
            options_table = prettytable.PrettyTable(hrules=prettytable.ALL)
            options_table.field_names = ['Number', 'Option']
            for idx, option in enumerate(options):
                options_table.add_row([idx + 1, option])
            try:
                while True:
                    try:
                        _prompt = f'{prompt}\n{options_table.get_html_string()}'
                        break
                    except TypeError:
                        pass
                if force:
                    _prompt += f'\nEnter choice 1-{len(options)}: '
                    response_num = self.enter_choice(_prompt)
                    response = options[response_num - 1]
                else:
                    _prompt += f'\nEnter choice 0-{len(options)} (0 to skip): '
                    response_num = self.enter_choice(_prompt)
                    if response_num == 0:
                        return None
                    else:
                        response = options[response_num - 1]
                return response
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')
