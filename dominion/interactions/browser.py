import inspect
import math
from contextlib import contextmanager
from threading import Event

from ..cards import cards
from .interaction import Interaction


class BrowserInteraction(Interaction):
    @contextmanager
    def move_cards(self):
        self.display_hand()
        self.display_played_cards()
        self.display_supply()
        self.display_discard_pile()
        self.display_trash()
        yield
        self.display_hand()
        self.display_played_cards()
        self.display_supply()
        self.display_discard_pile()
        self.display_trash()

    def send(self, message):
        message = f'\n{message}\n'
        self.socketio.send(message, to=self.sid)
        
    def _call(self, event_name, data):
        event = Event()
        response = None

        def ack(data):
            nonlocal event
            nonlocal response
            response = data
            event.set()
        
        self.socketio.emit(
            event_name,
            data, 
            to=self.sid,
            callback=ack,
        )
        event.wait()
        print(response)
        return response

    def _enter_choice(self, prompt):
        return self._call(
            "enter choice",
            {
                "prompt": prompt,
            }
        )

    def _get_supply_data(self):
        return {
            "cards": [card_stack.json for card_stack in self.supply.card_stacks.values()],
        }

    def _get_played_cards_data(self):
        return {
            "cards" : [card.json for card in self.played_cards],
        }

    def _get_hand_data(self):
        return {
            "cards": [card.json for card in self.hand],
        }        

    def _get_discard_pile_data(self):
        return {
            "cards": [card.json for card in self.discard_pile],
        }

    def _get_trash_data(self):
        return {
            "cards": self.supply.trash_pile_json,
        }

    def display_supply(self):
        self.socketio.emit(
            "display supply",
            self._get_supply_data(),
            to=self.room, # Always send the supply to all players
        )

    def display_hand(self):
        self.socketio.emit(
            "display hand",
            self._get_hand_data(),
            to=self.sid, # Only send the player's hand to this player
        )

    def display_played_cards(self):
        self.socketio.emit(
            "display played cards",
            self._get_played_cards_data(),
            to=self.room, # Always send played cards to all players
        )

    def display_discard_pile(self):
        self.socketio.emit(
            "display discard pile",
            self._get_discard_pile_data(),
            to=self.sid, # Only send discard pile to this player
        )

    def display_trash(self):
        self.socketio.emit(
            "display trash",
            self._get_trash_data(),
            to=self.room, # Always send trash to all players
        )

    def choose_card_from_hand(self, prompt, force):
        with self.move_cards():
            print("choose_card_from_hand")
            if not self.hand:
                self.send('There are no cards in your hand.')
                return None
            while True:
                try:
                    response = self._call(
                        "choose card from hand",
                        {
                            "prompt": prompt,
                            "force": force,
                        }
                    )
                    if response is None:
                        return None
                    for card in self.hand:
                            if response["id"] == card.id:
                                return card
                except (IndexError, ValueError):
                    self.send('That is not a valid choice.')

    def choose_specific_card_class_from_hand(self, prompt, force, card_class):
        with self.move_cards():
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
        with self.move_cards():
            print("choose_specific_card_type_from_hand")
            # Only cards of the correct type can be chosen
            playable_cards = [card for card in self.hand if card_type in card.types]
            if not playable_cards:
                self.send(f'There are no {card_type.name.lower().capitalize()} cards in your hand.')
                return None
            while True:
                try:
                    response = self._call(
                        "choose specific card type from hand",
                        {
                            "prompt": prompt,
                            "card_type": card_type.name,
                        }
                    )
                    if response is None:
                        return None
                    for card in self.hand:
                            if response["id"] == card.id:
                                return card
                except (IndexError, ValueError):
                    self.send('That is not a valid choice.')

    def choose_card_from_discard_pile(self, prompt, force):
        with self.move_cards():
            print("choose_card_from_discard_pile")
            if not self.discard_pile:
                self.send('There are no cards in your discard pile.')
                return None
            while True:
                try:
                    response = self._call(
                        "choose card from discard pile",
                        {
                            "prompt": prompt,
                            "force": force,
                        }
                    )
                    if response is None:
                        return None
                    for card in self.discard_pile:
                            if response["id"] == card.id:
                                return card
                except (IndexError, ValueError):
                    self.send('That is not a valid choice.')

    def choose_treasures_from_hand(self, prompt):
        with self.move_cards():
            print("choose_treasures_from_hand")
            while True:
                try:
                    response = self._call(
                        "choose treasures from hand",
                        {
                            "prompt": prompt,
                        }
                    )
                    chosen_treasure_cards = []
                    for card_data in response:
                        for card in self.hand:
                            if card_data["id"] == card.id:
                                chosen_treasure_cards.append(card)
                    return chosen_treasure_cards
                except (IndexError, ValueError):
                    self.send('That is not a valid choice.')

    def choose_card_class_from_supply(self, prompt, max_cost, force, invalid_card_classes=None, exact_cost=False):
        with self.move_cards():
            print("choose_card_class_from_supply")
            if invalid_card_classes is None:
                invalid_card_classes = []
            while True:
                try:
                    # Only cards you can afford can be chosen (and with non-zero quantity)
                    stacks = self.supply.card_stacks
                    buyable_card_stacks = [card_class for card_class in stacks if stacks[card_class].modified_cost <= max_cost and card_class not in invalid_card_classes and stacks[card_class].cards_remaining > 0]
                    if exact_cost:
                        buyable_card_stacks = [card_class for card_class in buyable_card_stacks if stacks[card_class].modified_cost == max_cost]
                    if not buyable_card_stacks:
                        self.send('There are no cards in the Supply that you can buy.')
                        return None
                    card_data = self._call(
                        "choose card class from supply",
                        {
                            "prompt": prompt,
                            "max_cost": max_cost if max_cost != math.inf else None,
                            "force": force,
                        }
                    )
                    if card_data is None:
                        return None
                    for card_class, card_stack in self.supply.card_stacks.items():
                        if card_data["name"] == card_stack.example.name:
                            return card_class
                except (IndexError, ValueError, TypeError):
                    self.send('That is not a valid choice.')

    def choose_specific_card_type_from_supply(self, prompt, max_cost, card_type, force):
        with self.move_cards():
            print("choose_specific_card_type_from_supply")
            # Only cards you can afford can be chosen (and with non-zero quantity)
            stacks = self.supply.card_stacks
            buyable_card_stacks = [card_class for card_class in stacks if card_type in card_class.types and stacks[card_class].modified_cost <= max_cost and stacks[card_class].cards_remaining > 0]
            if not buyable_card_stacks:
                self.send('There are no cards in the Supply that you can buy.')
                return None
            card_data = self._call(
                "choose specific card type from supply",
                {
                    "prompt": prompt,
                    "max_cost": max_cost if max_cost != math.inf else None,
                    "card_type": card_type.name,
                    "force": force,
                }
            )
            if card_data is None:
                return None
            for card_class, card_stack in self.supply.card_stacks.items():
                if card_data["name"] == card_stack.example.name:
                    return card_class

    def choose_specific_card_type_from_trash(self, prompt, max_cost, card_type, force):
        with self.move_cards():
            print("choose_specific_card_type_from_trash")
            # Only cards you can afford can be chosen (and with non-zero quantity)
            trash_pile = self.supply.trash_pile
            gainable_card_classes = [card_class for card_class in trash_pile if trash_pile[card_class] and card_type in card_class.types]
            if not gainable_card_classes:
                self.send('There are no cards in the Trash that you can gain.')
                return None
            card_data = self._call(
                "choose specific card type from trash",
                {
                    "prompt": prompt,
                    "max_cost": max_cost if max_cost != math.inf else None,
                    "card_type": card_type.name,
                    "force": force,
                }
            )
            if card_data is None:
                return None
            for card_class in gainable_card_classes:
                if card_data["name"] == card_class.name:
                    return card_class
       
    def choose_yes_or_no(self, prompt): 
        print("choose_yes_or_no")
        while True:
            try:
                response = self._call(
                    "choose yes or no", 
                    {
                        "prompt": prompt,
                    },
                )
                return response
            except AttributeError:
                self.send(f'{response} is not a valid choice.')

    def choose_from_range(self, prompt, minimum, maximum, force):
        print("choose_from_range")
        while True:
            try:
                response = self._call(
                    "choose from range",
                    {
                        "prompt": prompt,
                        "start": minimum,
                        "stop": maximum,
                        "force": force,
                    }
                )
                return response
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')

    def choose_from_options(self, prompt, options, force):
        print("choose_from_options")
        option_names = []
        for option in options:
            if isinstance(option, cards.Card) or inspect.isclass(option):
                option_names.append(option.name)
            else:
                option_names.append(option)
        options_json = [{"id": idx, "name": name} for idx, name in enumerate(option_names)]
        print(options_json)
        response = self._call(
            "choose from options",
            {
                "prompt": prompt,
                "options": options_json,
                "force": force,
            }
        )
        if response is not None:
            return options[response]
        return None

    def new_turn(self):
        self.socketio.emit('new turn', {'player': self.player.name}, room=self.room)
