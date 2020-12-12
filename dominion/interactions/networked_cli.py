import prettytable
from ..cards import cards
from .interaction import Interaction


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
        while True:
            try:
                return hand_table.get_string()
            except:
                pass

    def get_discard_pile_string(self):
        discard_table = prettytable.PrettyTable(hrules=prettytable.ALL)
        discard_table.field_names = ['Number', 'Card', 'Type', 'Description']
        for idx, card in enumerate(self.discard_pile):
            types = ', '.join([type.name.lower().capitalize() for type in card.types])
            discard_table.add_row([idx + 1, card.name, types, card.description])
        while True:
            try:
                return discard_table.get_string()
            except:
                pass

    def display_supply(self):
        supply_table = self.supply.get_table()
        while True:
            try:
                self.send(supply_table.get_string())
            except:
                pass

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
                    if card_num < 1:
                        raise ValueError
                    card_chosen = self.hand[card_num - 1]
                else:
                    _prompt += f'\nEnter choice 1-{len(self.hand)} (0 to skip): '
                    card_num = self.enter_choice(_prompt)
                    if card_num < 0:
                        raise ValueError
                    elif card_num == 0:
                        return None
                    else:
                        card_chosen = self.hand[card_num - 1]
                return card_chosen
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')

    def choose_specific_card_class_from_hand(self, prompt, force, card_class):
        if not any(isinstance(card, card_class) for card in self.hand):
            self.send(f'There are no {card_class} cards in your hand.')
            return None
        # Find a card in the player's hand of the correct class
        for card in self.hand:
            if isinstance(card, card_class):
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
                        _prompt = f'{prompt}\n{hand_table.get_string()}'
                        break
                    except:
                        pass
                _prompt += f'\nEnter choice 1-{len(playable_cards)} (0 to skip): '
                card_num = self.enter_choice(_prompt)
                if card_num < 0:
                    raise ValueError
                elif card_num == 0:
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
                    if card_num < 1:
                        raise ValueError
                    card_chosen = self.discard_pile[card_num - 1]
                else:
                    _prompt += f'\n{prompt}\nEnter choice 1-{len(self.discard_pile)} (0 to skip): '
                    card_num = self.enter_choice(_prompt)
                    if card_num < 0:
                        raise ValueError
                    elif card_num == 0:
                        return None
                    else:
                        card_chosen = self.discard_pile[card_num - 1]
                return card_chosen
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')        

    def choose_card_class_from_supply(self, prompt, max_cost, force, invalid_card_classes=None, exact_cost=False):
        if invalid_card_classes is None:
            invalid_card_classes = []
        while True:
            try:
                supply_table = prettytable.PrettyTable(hrules=prettytable.ALL)
                supply_table.field_names = ['Number', 'Card', 'Cost', 'Type', 'Quantity', 'Description']
                # Only cards you can afford can be chosen (and with non-zero quantity)
                stacks = self.supply.card_stacks
                buyable_card_stacks = [card_class for card_class in stacks if stacks[card_class].modified_cost <= max_cost and card_class not in invalid_card_classes and stacks[card_class].cards_remaining > 0]
                if exact_cost:
                    buyable_card_stacks = [card_class for card_class in buyable_card_stacks if stacks[card_class].modified_cost == max_cost]
                if not buyable_card_stacks:
                    return None
                # for idx, card_class in enumerate(sorted(buyable_card_stacks, key=lambda x: (x.types[0].value, x.cost))):
                for idx, card_class in enumerate(buyable_card_stacks):
                    types = ', '.join([type.name.lower().capitalize() for type in card_class.types])
                    card_quantity = stacks[card_class].cards_remaining
                    supply_table.add_row([idx + 1, card_class.name, stacks[card_class].modified_cost, types, card_quantity, card_class.description])
                while True:
                    try:
                        _prompt = f'{prompt}\n{supply_table.get_string()}'
                        break
                    except:
                        pass

                if force:
                    _prompt += f'\nEnter choice 1-{len(buyable_card_stacks)}: '
                    card_num = self.enter_choice(_prompt)
                    if card_num < 1:
                        raise ValueError
                    card_to_buy = list(buyable_card_stacks)[card_num - 1]
                else:
                    _prompt += f'\nEnter choice 1-{len(buyable_card_stacks)} (0 to skip): '
                    card_num = self.enter_choice(_prompt)
                    if card_num < 0:
                        raise ValueError
                    elif card_num == 0:
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
                buyable_card_stacks = [card_class for card_class in stacks if stacks[card_class].modified_cost <= max_cost and stacks[card_class].cards_remaining > 0 and card_type in card_class.types]
                # for idx, card_class in enumerate(sorted(buyable_card_stacks, key=lambda x: (x.types[0].value, x.cost))):
                for idx, card_class in enumerate(buyable_card_stacks):
                    types = ', '.join([type.name.lower().capitalize() for type in card_class.types])
                    card_quantity = stacks[card_class].cards_remaining
                    supply_table.add_row([idx + 1, card_class.name, stacks[card_class].modified_cost, types, card_quantity, card_class.description])
                while True:
                    try:
                        _prompt = f'{prompt}\n{supply_table.get_string()}'
                        break
                    except:
                        pass
                if force:
                    _prompt += f'\nEnter choice 1-{len(buyable_card_stacks)}: '
                    card_num = self.enter_choice(_prompt)
                    if card_num < 1:
                        raise ValueError
                    card_to_buy = list(buyable_card_stacks)[card_num - 1]
                else:
                    _prompt += f'\nEnter choice 1-{len(buyable_card_stacks)} (0 to skip): '
                    card_num = self.enter_choice(_prompt)
                    if card_num < 0:
                        raise ValueError
                    elif card_num == 0:
                        return None
                    else:
                        card_to_buy = list(buyable_card_stacks)[card_num - 1]
                return card_to_buy
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')     

    def choose_specific_card_type_from_trash(self, prompt, max_cost, card_type, force):
        while True:
            try:
                trash_table = prettytable.PrettyTable(hrules=prettytable.ALL)
                trash_table.field_names = ['Number', 'Card', 'Cost', 'Type', 'Quantity', 'Description']
                # Only cards you can afford can be chosen (and with non-zero quantity)
                trash_pile = self.supply.trash_pile
                gainable_card_classes = [card_class for card_class in trash_pile if trash_pile[card_class] and card_type in card_class.types]
                # for idx, card_class in enumerate(sorted(buyable_card_stacks, key=lambda x: (x.types[0].value, x.cost))):
                for idx, card_class in enumerate(gainable_card_classes):
                    types = ', '.join([type.name.lower().capitalize() for type in card_class.types])
                    card_quantity = len(trash_pile[card_class])
                    trash_table.add_row([idx + 1, card_class.name, card_class.cost, types, card_quantity, card_class.description])
                while True:
                    try:
                        _prompt = f'{prompt}\n{trash_table.get_string()}'
                        break
                    except:
                        pass
                if force:
                    _prompt += f'Enter choice 1-{len(gainable_card_classes)}: '
                    card_num = self.enter_choice(_prompt)
                    if card_num < 1:
                        raise ValueError
                    card_to_gain = list(gainable_card_classes)[card_num - 1]
                else:
                    _prompt += f'Enter choice 1-{len(gainable_card_classes)} (0 to skip): '
                    card_num = self.enter_choice(_prompt)
                    if card_num < 0:
                        raise ValueError
                    elif card_num == 0:
                        return None
                    else:
                        card_to_gain = list(gainable_card_classes)[card_num - 1]
                return card_to_gain
            except (IndexError, ValueError):
                self.send('That is not a valid choice.\n')   

    def choose_yes_or_no(self, prompt):
        while True:
            try:
                _prompt = f'{prompt}\nEnter choice (Yes/No): '
                response = self.socketio.call('choose yes or no', {'prompt': _prompt}, to=self.sid, timeout=None)
                if response.lower() in ['yes', 'y', 'no', 'n']:
                    break
            except AttributeError:
                self.send(f'{response} is not a valid choice.')
        if response.lower() in ['yes', 'y']:
            return True
        else:
            return False

    def choose_from_range(self, prompt, minimum, maximum, force):
        options = list(range(minimum, maximum + 1))
        while True:
            try:
                if force:
                    _prompt = f'{prompt}\nEnter choice {minimum}-{maximum}: '
                    response = self.enter_choice(_prompt)
                    if response < minimum or response > maximum:
                        raise ValueError
                else:
                    _prompt = f'{prompt}\nEnter choice {minimum}-{maximum} (0 to skip): '
                    response = self.enter_choice(_prompt)
                    if response == 0:
                        return None
                    elif response < minimum or response > maximum:
                        raise ValueError
                return response
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')

    def choose_from_options(self, prompt, options, force):
        while True:
            options_table = prettytable.PrettyTable(hrules=prettytable.ALL)
            options_table.field_names = ['Number', 'Option']
            for idx, option in enumerate(options):
                options_table.add_row([idx + 1, option])
            try:
                while True:
                    try:
                        _prompt = f'{prompt}\n{options_table.get_string()}'
                        break
                    except:
                        pass
                if force:
                    _prompt += f'\nEnter choice 1-{len(options)}: '
                    response_num = self.enter_choice(_prompt)
                    if response_num < 1:
                        raise ValueError
                    response = options[response_num - 1]
                else:
                    _prompt += f'\nEnter choice 0-{len(options)} (0 to skip): '
                    response_num = self.enter_choice(_prompt)
                    if response_num < 0:
                        raise ValueError
                    elif response_num == 0:
                        return None
                    else:
                        response = options[response_num - 1]
                return response
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')

    def new_turn(self):
        if self.socketio is not None:
            self.socketio.emit('new turn', {'player': self.player.name}, room=self.room)
