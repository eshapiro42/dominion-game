from __future__ import annotations

import random
from typing import TYPE_CHECKING, List, Optional

from ..cards import base_cards
from ..cards.cards import CardType
from ..expansions import CornucopiaExpansion
from .interaction import Interaction

if TYPE_CHECKING:
    from ..cards.cards import Card


class AutoInteraction(Interaction):
    def send(self, message):
        # TODO: Turn off printing (useful for debugging)
        print(message)
        print()

    def display_supply(self):
        pass

    def display_hand(self):
        pass

    def display_discard_pile(self):
        pass

    def _get_played_cards_data(self):
        return {
            "cards" : [card.json for card in self.played_cards],
        }

    def display_played_cards(self):
        try:
            self.socketio.emit(
                "display played cards",
                self._get_played_cards_data(),
                to=self.room, # Always send played cards to all players
            )
        except Exception as exception:
            print(exception)

    def sleep_random(self):
        """
        Sleep to simulate thought unless we are running tests.
        """
        if not self.game.test:
            time_to_sleep = random.uniform(1, 3) 
            self.socketio.sleep(time_to_sleep)

    def choose_card_from_hand(self, prompt, force, invalid_cards=None) -> Optional[Card]:
        cards_chosen = self.choose_cards_from_hand(prompt, force, max_cards=1, invalid_cards=invalid_cards)
        if not cards_chosen:
            return None
        return cards_chosen[0]

    def choose_cards_from_hand(self, prompt, force, max_cards=1, invalid_cards=None) -> List[Card]:
        self.sleep_random()
        print(prompt)
        print()
        if not self.hand:
            print('There are no cards in your hand.\n')
            return []
        if max_cards is None:
            max_cards = len(self.hand)
        else:
            max_cards = min(max_cards, len(self.hand)) # Don't ask for more cards than we have
        if invalid_cards is None:
            invalid_cards = []
        valid_cards = [card for card in self.hand if card not in invalid_cards]
        while True:
            try:
                self.display_hand()
                if force:
                    cards_chosen = random.sample(valid_cards, max_cards)
                else:
                    num_cards = random.randint(0, max_cards)
                    cards_chosen = random.sample(valid_cards, num_cards)
                return cards_chosen
            except (IndexError, ValueError):
                print('That is not a valid choice.\n')
                raise

    def choose_specific_card_class_from_hand(self, prompt, force, card_class):
        self.sleep_random()
        print(prompt)
        print()
        if not any(isinstance(card, card_class) for card in self.hand):
            print(f'There are no {card_class} cards in your hand.\n')
            return None
        # Find a card in the player's hand of the correct class
        for card in self.hand:
            if isinstance(card, card_class):
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
        self.sleep_random()
        print(prompt)
        print()
        # Only cards of the correct type can be chosen
        playable_cards = [card for card in self.hand if card_type in card.types]
        if not playable_cards:
            print(f'There are no {card_type.name.lower().capitalize()} cards in your hand.\n')
            return None
        while True:
            try:
                print(f'Enter choice 1-{len(playable_cards)} (0 to skip): ', end='')
                choices = list(range(0, len(playable_cards) + 1))
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
                raise

    def choose_specific_card_type_from_played_cards(self, prompt, card_type):
        self.sleep_random()
        print(prompt)
        print()
        # Only cards of the correct type can be chosen
        selectable_cards = [card for card in self.played_cards if card_type in card.types]
        if not selectable_cards:
            print(f'There are no {card_type.name.lower().capitalize()} cards in your played cards.\n')
            return None
        while True:
            try:
                choices = [None] + selectable_cards
                weights = [1] + [card.cost for card in selectable_cards] # Weight options by card cost, except for "skip"
                selected_card = random.choices(choices, weights, k=1)[0]
                return selected_card
            except (IndexError, ValueError):
                print('That is not a valid choice.\n')
                raise

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
        if force:
            cards_chosen = random.sample(selectable_cards, max_cards)
        else:
            num_cards = random.randint(0, max_cards)
            cards_chosen = random.sample(selectable_cards, num_cards)
        return cards_chosen

    def choose_card_from_discard_pile(self, prompt, force):
        self.sleep_random()
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
                    choices = list(range(1, len(self.discard_pile) + 1))
                    weights = [card.cost * 5 for card in self.discard_pile]
                    card_num = random.choices(choices, weights, k=1)[0]
                    print(card_num)
                    print()
                    card_chosen = self.discard_pile[card_num - 1]
                else:
                    print(f'Enter choice 1-{len(self.discard_pile)} (0 to skip): ', end='')
                    choices = list(range(0, len(self.discard_pile) + 1))
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
                raise

    def choose_treasures_from_hand(self, prompt):
        # The CPU will always choose all available Treasures
        self.sleep_random()
        print(prompt)
        print()
        while True:
            try:
                available_treasures = [card for card in self.hand if CardType.TREASURE in card.types]
                if not available_treasures:
                    print('There are no treasures in your hand.\n')
                    return []
                print(f'Available treasures: {", ".join(map(str, available_treasures))}')
                return available_treasures
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')

    def choose_card_class_from_supply(self, prompt, max_cost, force, invalid_card_classes=None, exact_cost=False):
        self.sleep_random()
        print(prompt)
        print()
        if invalid_card_classes is None:
            invalid_card_classes = []
        while True:
            try:
                stacks = self.supply.card_stacks
                buyable_card_stacks = [card_class for card_class in stacks if stacks[card_class].modified_cost <= max_cost and card_class not in invalid_card_classes and stacks[card_class].cards_remaining > 0]
                if exact_cost:
                    buyable_card_stacks = [card_class for card_class in buyable_card_stacks if stacks[card_class].modified_cost == max_cost]
                if not buyable_card_stacks:
                    return None
                if force:
                    print(f'Enter choice 1-{len(buyable_card_stacks)}: ', end='')
                    choices = list(range(1, len(buyable_card_stacks) + 1))
                    # Weight by cost (more expensive are more likely, coppers and estates are unlikely)
                    weights = [
                        0 if CardType.CURSE in card_class.types \
                        else 1 if card_class == base_cards.Copper or card_class == base_cards.Estate \
                        else self.game.current_turn.get_cost(card_class) * 5 \
                        for card_class in buyable_card_stacks
                    ]
                    try:
                        card_num = random.choices(choices, weights, k=1)[0]
                    except IndexError:
                        return None
                    print(card_num)
                    print()
                    card_to_buy = list(buyable_card_stacks)[card_num - 1]
                else:
                    print(f'Enter choice 1-{len(buyable_card_stacks)} (0 to skip): ', end='')
                    choices = list(range(0, len(buyable_card_stacks) + 1))
                    weights = [1] + [
                        0 if CardType.CURSE in card_class.types \
                        else 1 if card_class == base_cards.Copper or card_class == base_cards.Estate \
                        else self.game.current_turn.get_cost(card_class) * 5 \
                        for card_class in buyable_card_stacks
                    ]
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
                raise

    def choose_specific_card_type_from_supply(self, prompt, max_cost, card_type, force):
        self.sleep_random()
        print(prompt)
        print()
        while True:
            try:
                # Only cards you can afford can be chosen (and with non-zero quantity)
                stacks = self.supply.card_stacks
                buyable_card_stacks = [card_class for card_class in stacks if stacks[card_class].modified_cost <= max_cost and stacks[card_class].cards_remaining > 0 and card_type in card_class.types]
                if force:
                    print(f'Enter choice 1-{len(buyable_card_stacks)}: ', end='')
                    choices = list(range(1, len(buyable_card_stacks) + 1))
                    # Weight by cost (more expensive is more likely)
                    weights = [self.game.current_turn.get_cost(card_class) * 5 for card_class in buyable_card_stacks]
                    card_num = random.choices(choices, weights, k=1)[0]
                    print(card_num)
                    print()
                    card_to_buy = list(buyable_card_stacks)[card_num - 1]
                else:
                    print(f'Enter choice 1-{len(buyable_card_stacks)} (0 to skip): ', end='')
                    choices = list(range(0, len(buyable_card_stacks) + 1))
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
                raise

    def choose_specific_card_type_from_trash(self, prompt, max_cost, card_type, force):
        self.sleep_random()
        print(prompt)
        print()
        while True:
            try:
                # Only cards you can afford can be chosen (and with non-zero quantity)
                trash_pile = self.supply.trash_pile
                gainable_card_classes = [card_class for card_class in trash_pile if trash_pile[card_class] and card_type in card_class.types]
                if not gainable_card_classes:
                    print('There are no cards in the Trash that you can gain.')
                    return None
                if force:
                    return random.choice(gainable_card_classes)
                else:
                    gainable_card_classes = ["skip"] + gainable_card_classes
                    card_to_gain = random.choice(gainable_card_classes)
                    if card_to_gain == "skip":
                        return None
                    return card_to_gain
            except (IndexError, ValueError):
                print('That is not a valid choice.\n')
                raise

    def choose_card_from_prizes(self, prompt):
        self.sleep_random()
        print(prompt)
        print()
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
        return random.choice(prizes)


    def choose_yes_or_no(self, prompt):
        self.sleep_random()
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

    def choose_from_range(self, prompt, minimum, maximum, force):
        self.sleep_random()
        options = list(range(minimum, maximum + 1))
        print(prompt)
        print()
        while True:
            try:
                if force:
                    print(f'Enter choice {minimum}-{maximum}: ', end='')
                    response = random.choice(options)
                    print(response)
                    print()
                    if response < minimum or response > maximum:
                        raise ValueError
                else:
                    print(f'Enter choice {minimum}-{maximum} (0 to skip): ', end='')
                    response = random.choice([0] + options)
                    print(response)
                    if response == 0:
                        return None
                    elif response < minimum or response > maximum:
                        raise ValueError
                return response
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')

    def choose_from_options(self, prompt, options, force):
        self.sleep_random()
        print(prompt)
        print()
        while True:
            try:
                if force:
                    print(f'Enter choice 1-{len(options)}: ', end='')
                    choices = list(range(1, len(options) + 1))
                    # Higher options more likely
                    weights = choices
                    response_num = random.choices(choices, weights, k=1)[0]
                    print(response_num)
                    print()
                    response = options[response_num - 1]
                else:
                    print(f'Enter choice 0-{len(options)} (0 to skip): ', end='')
                    choices = list(range(0, len(options) + 1))
                    # Higher options more likely
                    weights = [1] + choices[1:]
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
                raise

    def choose_cards_from_list(self, prompt: str, cards: List[Card], force: bool, max_cards: int = 1, ordered: bool = False) -> List[Card]:
        print("choose_cards_from_list")
        if not cards:
            self.send('There are no cards to choose from.')
            return []
        if max_cards is not None:
            max_cards = min(max_cards, len(cards)) # Don't ask for more cards than we have
        while True:
            try:
                self.display_hand()
                if force:
                    cards_chosen = random.sample(cards, max_cards)
                else:
                    num_cards = random.randint(0, max_cards)
                    cards_chosen = random.sample(cards, num_cards)
                return cards_chosen
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')
            except ArithmeticError:
                self.send(f"You must choose exactly {s(max_cards, 'card')}.")

    def new_turn(self):
        print(f"{self.player}'s turn.")
        if self.socketio is not None:
            self.socketio.emit('new turn', {'player': self.player.name}, room=self.room)
