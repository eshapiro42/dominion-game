import prettytable
import random
import socketio


sio = socketio.Client()


class Client:
    def __init__(self):
        sio.connect('http://localhost:5000')
        self.username = self.get_username()
        self.room = None
        self.enter_room()
    
    @property
    def json(self):
        return {
            'username': self.username,
            'room': self.room,
            'room_creator': self.room_creator,
        }

    def get_username(self):
        return input('Please enter your username: ')

    def set_room(self, room):
        self.room = room

    def enter_room(self):
        prompt = 'What would you like to do?'
        options = ['Create a new room', 'Join an existing room']
        choice = choose_from_options(prompt=prompt, options=options, force=True)
        if choice == 'Create a new room':
            self.room_creator = True
            sio.emit('create room', self.json, callback=self.set_room)
        elif choice == 'Join an existing room':
            self.room_creator = False
            self.room = input('Please enter the room ID: ')
            sio.emit('join room', self.json)

@sio.event
def connect():
    print("You are connected to the server.")

@sio.event
def disconnect():
    print("You have been disconnected from the server.")

@sio.on('game startable')
def game_startable():
    if client.room_creator:
        print('The game can now be started.')
        input('Press Enter when you are ready to start the game... ')
        sio.emit('start game', client.json)        

@sio.on('message')
def on_message(data):
    print(data)

@sio.on('enter choice')
def send_choice(data):
    prompt = data['prompt']
    return int(input(prompt))

@sio.on('choose card from hand')
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

@sio.on('choose specific card class from hand')
def choose_specific_card_class_from_hand(prompt, force, card_class):
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

@sio.on('choose specific card type from hand')
def choose_specific_card_type_from_hand(prompt, card_type):
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

@sio.on('choose card from discard pile')
def choose_card_from_discard_pile(prompt, force):
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

@sio.on('choose card class from supply')
def choose_card_class_from_supply(prompt, max_cost, force):
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

@sio.on('choose specific card type from supply')
def choose_specific_card_type_from_supply(prompt, max_cost, card_type, force):
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

@sio.on('choose yes or no')
def choose_yes_or_no(prompt):
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

@sio.on('choose from options')
def choose_from_options(prompt, options, force):
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


if __name__ == '__main__':
    client = Client()


