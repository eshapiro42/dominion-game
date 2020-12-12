import random
from ..cards import cards, base_cards
from .interaction import Interaction


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
                    choices = list(range(1, len(self.hand) + 1))
                    # Weight options equally
                    weights = [1 for card in self.hand]
                    card_num = random.choices(choices, weights, k=1)[0]
                    print(card_num)
                    print()
                    card_chosen = self.hand[card_num - 1]
                else:
                    print(f'Enter choice 1-{len(self.hand)} (0 to skip): ', end='')
                    choices = list(range(0, len(self.hand) + 1))
                    # Weight options equally
                    weights = [1] + [1 for card in self.hand]
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
                raise

    def choose_specific_card_class_from_hand(self, prompt, force, card_class):
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

    def choose_card_class_from_supply(self, prompt, max_cost, force, invalid_card_classes=None, exact_cost=False):
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
                        0 if cards.CardType.CURSE in card_class.types \
                        else 1 if card_class == base_cards.Copper or card_class == base_cards.Estate \
                        else card_class.cost * 5 \
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
                        0 if cards.CardType.CURSE in card_class.types \
                        else 1 if card_class == base_cards.Copper or card_class == base_cards.Estate \
                        else card_class.cost * 5 \
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
                    weights = [card.cost * 5 for card in buyable_card_stacks]
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
        print(prompt)
        print()
        while True:
            try:
                # Only cards you can afford can be chosen (and with non-zero quantity)
                trash_pile = self.supply.trash_pile
                gainable_card_classes = [card_class for card_class in trash_pile if trash_pile[card_class] and card_type in card_class.types]
                # for idx, card_class in enumerate(sorted(buyable_card_stacks, key=lambda x: (x.types[0].value, x.cost))):
                if force:
                    print(f'Enter choice 1-{len(gainable_card_classes)}: ')
                    choices = list(range(1, len(gainable_card_classes) + 1))
                    # Weight equally
                    weights = [1 for card in gainable_card_classes]
                    card_num = random.choices(choices, weights, k=1)[0]
                    print(card_num)
                    print()
                    card_to_gain = list(gainable_card_classes)[card_num - 1]
                else:
                    print(f'Enter choice 1-{len(gainable_card_classes)} (0 to skip): ')
                    choices = list(range(0, len(gainable_card_classes)))
                    # Weight equally
                    weights = [1] + [1 for card in gainable_card_classes]
                    card_num = random.choices(choices, weights, k=1)[0]
                    print(card_num)
                    print()
                    if card_num == 0:
                        return None
                    else:
                        card_to_gain = list(gainable_card_classes)[card_num - 1]
                return card_to_gain
            except (IndexError, ValueError):
                print('That is not a valid choice.\n')
                raise

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

    def choose_from_range(self, prompt, minimum, maximum, force):
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
