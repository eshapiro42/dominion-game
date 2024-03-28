import inspect
import math
from contextlib import contextmanager
from threading import Event # Monkey patched to use gevent Events
from typing import List, Optional

from ..cards.cards import Card
from ..expansions import CornucopiaExpansion
from ..grammar import s
from .interaction import Interaction


class BrowserInteraction(Interaction):
    def send(self, message):
        message = f'\n{message}\n'
        self.socketio.send(message, to=self.sid)
        
    def _call(self, event_name, data):
        """
        Send a request to the player and wait for a response, then return it.
        """
        # If it is not this player's turn, notify the player whose turn it is that they are waiting on this player
        if self.game.current_turn.player != self.player:
            self.socketio.emit(
                "waiting on player",
                self.player.name,
                to=self.game.current_turn.player.sid,
            )
        self.event = Event()
        self.refresh = False
        self.response = None
        # Try in a loop with a one second timeout in case an event gets missed or a network error occurs
        tries = 0
        # Send request
        self.socketio.emit(
            event_name,
            data, 
            to=self.sid,
        )
        while True:
            if self.refresh:
                # Resend request if refresh is requested
                print("Resending request...")
                self.socketio.emit(
                    event_name,
                    data, 
                    to=self.sid,
                )
                self.refresh = False
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
        # If it is not this player's turn, notify the player whose turn it is that the response was received
        if self.game.current_turn.player != self.player:
            self.socketio.emit(
                "not waiting on player",
                self.player.name,
                to=self.game.current_turn.player.sid,
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
    
    def _refresh_heartbeat(self):
        self.refresh = True

    def choose_cards_from_hand(self, prompt, force, max_cards=1, invalid_cards=None) -> List[Card]:
        print("choose_card_from_hand")
        if not self.hand:
            self.send('There are no cards in your hand.')
            return []
        if max_cards is not None:
            max_cards = min(max_cards, len(self.hand)) # Don't ask for more cards than we have
        if invalid_cards is None:
            invalid_cards = []
        while True:
            try:
                response = self._call(
                    "choose cards from hand",
                    {
                        "prompt": prompt,
                        "force": force,
                        "max_cards": max_cards,
                        "invalid_cards": [card.id for card in invalid_cards]
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

    def choose_card_from_hand(self, prompt, force, invalid_cards=None) -> Optional[Card]:
        cards_chosen = self.choose_cards_from_hand(prompt, force, max_cards=1, invalid_cards=invalid_cards)
        if not cards_chosen:
            return None
        return cards_chosen[0]

    def choose_specific_card_class_from_hand(self, prompt, force, card_class):
        if not any(isinstance(card, card_class) for card in self.hand):
            self.send(f'There are no {card_class.name} cards in your hand.')
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

    def choose_specific_card_type_from_hand(self, prompt, card_type, force=False):
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
                        "force": force,
                        "card_type": card_type.name,
                    }
                )
                if force:
                    if response is None:
                        raise ArithmeticError("Not enough cards chosen.")
                if response is None:
                    return None
                for card in self.hand:
                    if response["id"] == card.id:
                        return card
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')

    def choose_cards_of_specific_type_from_played_cards(self, prompt, force, card_type, max_cards=1, ordered=False) -> List[Card]:
        print("choose_cards_of_specific_type_from_played_cards")
        # Only cards of the correct type can be chosen
        selectable_cards = [card for card in self.played_cards if card_type in card.types]
        if not selectable_cards:
            self.send(f'There are no {card_type.name.lower().capitalize()} cards in your played cards.')
            return []
        if max_cards is not None:
            max_cards = min(max_cards, len(selectable_cards)) # Don't ask for more cards than are available
        else:
            max_cards = len(selectable_cards)
        while True:
            try:
                response = self._call(
                    "choose cards of specific type from played cards",
                    {
                        "prompt": prompt,
                        "force": force,
                        "max_cards": max_cards,
                        "card_type": card_type.name,
                        "ordered": ordered,
                    }
                )
                if force:
                    if response is None or (len(response) < max_cards and max_cards is not None):
                        raise ArithmeticError("Not enough cards chosen.")
                if response is None:
                    return []
                chosen_cards = []
                for card_data in response:
                    for card in self.played_cards:
                        if card_data["id"] == card.id:
                            chosen_cards.append(card)
                return chosen_cards
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')
            except ArithmeticError:
                self.send(f"You must choose exactly {s(max_cards, 'card')}.")

    def choose_specific_card_type_from_played_cards(self, prompt, card_type):
        cards_chosen = self.choose_cards_of_specific_type_from_played_cards(prompt, force=False, card_type=card_type, max_cards=1)
        if not cards_chosen:
            return None
        return cards_chosen[0]

    def choose_cards_of_specific_type_from_discard_pile(self, prompt, force, card_type, max_cards=1) -> List[Card]:
        print("choose_cards_of_specific_type_from_discard_pile")
        # Only cards of the correct type can be chosen
        selectable_cards = [card for card in self.discard_pile if card_type in card.types]
        if not selectable_cards:
            self.send(f'There are no {card_type.name.lower().capitalize()} cards in your discard pile.')
            return []
        if max_cards is not None:
            max_cards = min(max_cards, len(selectable_cards)) # Don't ask for more cards than are available
        else:
            max_cards = len(selectable_cards)
        while True:
            try:
                response = self._call(
                    "choose cards of specific type from discard pile",
                    {
                        "prompt": prompt,
                        "force": force,
                        "max_cards": max_cards,
                        "card_type": card_type.name,
                    }
                )
                if force:
                    if response is None or (len(response) < max_cards and max_cards is not None):
                        raise ArithmeticError("Not enough cards chosen.")
                if response is None:
                    return []
                chosen_cards = []
                for card_data in response:
                    for card in self.discard_pile:
                        if card_data["id"] == card.id:
                            chosen_cards.append(card)
                return chosen_cards
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')
            except ArithmeticError:
                self.send(f"You must choose exactly {s(max_cards, 'card')}.")
        
    def choose_card_from_discard_pile(self, prompt, force):
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
                        "exact_cost": exact_cost,
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

    def choose_specific_card_type_from_supply(self, prompt, max_cost, card_type, force, exact_cost=False):
        print("choose_specific_card_type_from_supply")
        # Only cards you can afford can be chosen (and with non-zero quantity)
        stacks = self.supply.card_stacks
        buyable_card_stacks = [card_class for card_class in stacks if card_type in card_class.types and stacks[card_class].modified_cost <= max_cost and stacks[card_class].cards_remaining > 0]
        if exact_cost:
            buyable_card_stacks = [card_class for card_class in buyable_card_stacks if stacks[card_class].modified_cost == max_cost]
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
                "exact_cost": exact_cost,
            }
        )
        if card_data is None:
            return None
        for card_class, card_stack in self.supply.card_stacks.items():
            if card_data["name"] == card_stack.example.name:
                return card_class

    def choose_specific_card_type_from_trash(self, prompt, max_cost, card_type, force):
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

    def choose_card_from_prizes(self, prompt):
        # Find the Cornucopia expansion instance
        cornucopia_expansion_instance = None
        for expansion_instance in self.supply.customization.expansions:
            if isinstance(expansion_instance, CornucopiaExpansion):
                cornucopia_expansion_instance = expansion_instance
                break
        prizes = cornucopia_expansion_instance.prizes
        print("choose_card_from_prizes")
        if not prizes:
            self.send('There are no Prizes remaining.')
            return None
        while True:
            try:
                response = self._call(
                    "choose card from prizes",
                    {
                        "prompt": prompt,
                    }
                )
                if response is None:
                    return None
                for card in prizes:
                    if response["id"] == card.id:
                        return card
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')

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
            if isinstance(option, Card) or inspect.isclass(option):
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

    def choose_cards_from_list(self, prompt: str, cards: List[Card], force: bool, max_cards: int = 1, ordered: bool = False) -> List[Card]:
        print("choose_cards_from_list")
        if not cards:
            self.send('There are no cards to choose from.')
            return []
        if max_cards is not None:
            max_cards = min(max_cards, len(cards)) # Don't ask for more cards than we have
        while True:
            try:
                response = self._call(
                    "choose cards from list",
                    {
                        "prompt": prompt,
                        "force": force,
                        "max_cards": max_cards,
                        "cards": [card.json for card in cards],
                        "ordered": ordered,
                    }
                )
                if force:
                    if response is None or (len(response) < max_cards and max_cards is not None):
                        raise ArithmeticError("Not enough cards chosen.")
                if response is None:
                    return []
                chosen_cards = []
                for card_data in response:
                    for card in cards:
                        if card_data["id"] == card.id:
                            chosen_cards.append(card)
                return chosen_cards
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')
            except ArithmeticError:
                self.send(f"You must choose exactly {s(max_cards, 'card')}.")

    def new_turn(self):
        self.socketio.emit('new turn', {'player': self.player.name}, room=self.room)
