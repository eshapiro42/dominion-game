import inspect
import math
from contextlib import contextmanager
from threading import Event # Monkey patched to use gevent Events
from typing import List, Optional

from ..cards import cards
from ..grammar import s
from .interaction import Interaction


class BrowserInteraction(Interaction):
    def display_all(self):
        self.display_hand()
        self.display_played_cards()
        self.display_supply()
        self.display_discard_pile()
        self.display_trash()

    @contextmanager
    def move_cards(self):
        # self.display_all()
        yield
        # self.display_all()

    def send(self, message):
        message = f'\n{message}\n'
        self.socketio.send(message, to=self.sid)
        
    def _call(self, event_name, data):
        """
        Send a request to the player and wait for a response, then return it.
        """
        self.event = Event()
        self.response = None
        # Try in a loop with a one second timeout in case an event gets missed or a network error occurs
        tries = 0
        while True:
            # Send request
            self.socketio.emit(
                event_name,
                data, 
                to=self.sid,
            )
            # Wait for response
            if self.event.wait(1):
                # Response was received
                break
            if self.game.killed:
                raise Exception(f"Game {self.room} was killed.")
            tries += 1
            if tries == 30 or tries % 60 == 0:
                print(f"Still waiting for input from player {self.player.name} in room {self.room} after {tries} seconds")
        # Acknowledge the response
        self.socketio.emit(
            "response received",
            to=self.sid,
        )
        # Return the response
        print(f"Response data: {self.response}")
        return self.response

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
        try:
            self.socketio.emit(
                "display supply",
                self._get_supply_data(),
                to=self.sid,
            )
        except Exception as exception:
            print(exception)

    def display_hand(self):
        try:
            self.socketio.emit(
                "display hand",
                self._get_hand_data(),
                to=self.sid,
            )
        except Exception as exception:
            print(exception)

    def display_played_cards(self):
        try:
            self.socketio.emit(
                "display played cards",
                self._get_played_cards_data(),
                to=self.room, # Always send played cards to all players
            )
        except Exception as exception:
            print(exception)

    def display_discard_pile(self):
        try:
            self.socketio.emit(
                "display discard pile",
                self._get_discard_pile_data(),
                to=self.sid,
            )
        except Exception as exception:
            print(exception)

    def display_trash(self):
        try:
            self.socketio.emit(
                "display trash",
                self._get_trash_data(),
                to=self.sid,
            )
        except Exception as exception:
            print(exception)

    def choose_cards_from_hand(self, prompt, force, max_cards=1) -> List[cards.Card]:
        with self.move_cards():
            print("choose_card_from_hand")
            if not self.hand:
                self.send('There are no cards in your hand.')
                return []
            if max_cards is not None:
                max_cards = min(max_cards, len(self.hand)) # Don't ask for more cards than we have
            while True:
                try:
                    response = self._call(
                        "choose cards from hand",
                        {
                            "prompt": prompt,
                            "force": force,
                            "max_cards": max_cards,
                        }
                    )
                    if force:
                        if response is None or (len(response) < max_cards and max_cards is not None):
                            raise ArithmeticError("Not enough cards chosen.")
                    if response is None:
                        return []
                    chosen_cards = []
                    for card_data in response:
                        for card in self.hand:
                            if card_data["id"] == card.id:
                                chosen_cards.append(card)
                    return chosen_cards
                except (IndexError, ValueError):
                    self.send('That is not a valid choice.')
                except ArithmeticError:
                    self.send(f"You must choose exactly {s(max_cards, 'card')}.")

    def choose_card_from_hand(self, prompt, force) -> Optional[cards.Card]:
        cards_chosen = self.choose_cards_from_hand(prompt, force, max_cards=1)
        if not cards_chosen:
            return None
        return cards_chosen[0]

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
                            "invalid_cards": [card_class.name for card_class in invalid_card_classes],
                        }
                    )
                    if card_data is None:
                        return None
                    for card_class, card_stack in self.supply.card_stacks.items():
                        if card_data["name"] == card_stack.example.name:
                            break
                    if card_class not in buyable_card_stacks:
                        raise ValueError()
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
