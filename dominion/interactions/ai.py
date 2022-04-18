from __future__ import annotations

import numpy as np
import random

from enum import IntEnum, auto
from tkinter import ALL, CURRENT
from typing import List, Optional, TYPE_CHECKING

from ..cards import cards, base_cards, prosperity_cards, intrigue_cards
from .interaction import Interaction

if TYPE_CHECKING:
    from ..game import Game
    from ..player import Player


MAX_PLAYERS = 6

ALL_CARD_CLASSES = (
    base_cards.BASIC_CARDS + base_cards.KINGDOM_CARDS
    + prosperity_cards.BASIC_CARDS + prosperity_cards.KINGDOM_CARDS 
    + intrigue_cards.KINGDOM_CARDS
)


# Basic treasure cards always have infinite quantity so that would be irrelevant input in the Supply
SUPPLY_CARD_CLASSES = [card_class for card_class in ALL_CARD_CLASSES if card_class not in [base_cards.Copper, base_cards.Silver, base_cards.Gold]]


def card_class_to_index(card_class):
    return ALL_CARD_CLASSES.index(card_class)


def supply_card_class_to_index(card_class):
    return SUPPLY_CARD_CLASSES.index(card_class)


class InteractionType(IntEnum):
    """Enum for the different types of interactions."""
    CHOOSE_CARD_FROM_HAND = 0
    CHOOSE_CARDS_FROM_HAND = auto()
    CHOOSE_SPECIFIC_CARD_CLASS_FROM_HAND = auto()
    CHOOSE_SPECIFIC_CARD_TYPE_FROM_HAND = auto()
    CHOOSE_CARD_FROM_DISCARD_PILE = auto()
    CHOOSE_TREASURES_FROM_HAND = auto()
    CHOOSE_CARD_CLASS_FROM_SUPPLY = auto()
    CHOOSE_SPECIFIC_CARD_TYPE_FROM_SUPPLY = auto()
    CHOOSE_SPECIFIC_CARD_TYPE_FROM_TRASH = auto()
    CHOOSE_YES_OR_NO = auto()
    CHOOSE_FROM_RANGE = auto()
    CHOOSE_FROM_OPTIONS = auto()


class Phase(IntEnum):
    """Enum for the different phases of a turn."""
    ACTION = 0
    BUY = auto()
    CLEANUP = auto()

    @staticmethod
    def from_string(phase_string: str):
        return {
            "Action Phase": Phase.ACTION,
            "Buy Phase": Phase.BUY,
            "Cleanup Phase": Phase.CLEANUP
        }[phase_string]


class GameState:
    """Object representing the current state of the game."""
    def __init__(self, player: Player, game: Game, interaction_type: InteractionType):
        # Info about the player
        self.own_index = game.players.index(player)
        # Info about the current turn
        self.current_player_is_self = player == game.current_turn.player
        self.current_phase = Phase.from_string(game.current_turn.current_phase)
        self.current_interaction = interaction_type
        self.turn_number = game.current_turn.player.turns_played
        self.current_played_cards = game.current_turn.player.played_cards
        self.actions_remaining = game.current_turn.actions_remaining
        self.buys_remaining = game.current_turn.buys_remaining
        self.coppers_remaining = game.current_turn.coppers_remaining
        if game.current_turn.player.played_cards:
            self.most_recently_played_card = game.current_turn.player.played_cards[-1]
        else:
            self.most_recently_played_card = None
        # Info about own cards
        self.own_hand = player.hand
        self.own_discard_pile = player.discard_pile
        # Info about shared card areas
        self.supply = game.supply.card_stacks
        self.trash = game.supply.trash_pile
        # Info about each player's hidden cards
        self.hand_sizes = [len(player.hand) for player in game.turn_order]
        self.discard_pile_sizes = [len(player.discard_pile) for player in game.turn_order]
        self.deck_sizes = [len(player.deck) for player in game.turn_order]
        # Info about each player's victory tokens
        if hasattr(player, "victory_tokens"):
            self.victory_tokens = [player.victory_tokens for player in game.turn_order]
        else:
            self.victory_tokens = [0 for _ in game.turn_order]
        # Info about each player's turns played
        self.turns_played = [player.turns_played for player in game.turn_order]
        # Info about coin tokens on Trade Route mat
        if hasattr(game.supply, "trade_route"):
            self.trade_route_coin_tokens = game.supply.trade_route
        else:
            self.trade_route_coin_tokens = 0

    @property
    def supply_vector(self):
        """Return a vector of the current supply."""
        supply = np.zeros(len(SUPPLY_CARD_CLASSES))
        for card_class in self.supply:
            if card_class not in SUPPLY_CARD_CLASSES:
                continue
            card_class_index = supply_card_class_to_index(card_class)
            quantity = self.supply[card_class].cards_remaining
            supply[card_class_index] = quantity
        return supply

    @property
    def trash_vector(self):
        """Return a vector of the current trash pile."""
        trash = np.zeros(len(ALL_CARD_CLASSES))
        for card_class in self.trash:
            card_class_index = card_class_to_index(card_class)
            quantity = len(self.trash[card_class])
            trash[card_class_index] = quantity
        return trash

    @property
    def played_cards_vector(self):
        """Return a vector of the cards played this turn."""
        played_cards = np.zeros(len(ALL_CARD_CLASSES))
        for card in self.current_played_cards:
            card_class = type(card)
            card_class_index = card_class_to_index(card_class)
            played_cards[card_class_index] += 1
        return played_cards

    @property
    def hand_vector(self):
        """Return a vector of the player's current hand."""
        hand = np.zeros(len(ALL_CARD_CLASSES))
        for card in self.own_hand:
            card_class = type(card)
            card_class_index = card_class_to_index(card_class)
            hand[card_class_index] += 1
        return hand

    @property
    def discard_pile_vector(self):
        """Return a vector of the player's current discard pile."""
        discard_pile = np.zeros(len(ALL_CARD_CLASSES))
        for card in self.own_discard_pile:
            card_class = type(card)
            card_class_index = card_class_to_index(card_class)
            discard_pile[card_class_index] += 1
        return discard_pile

    @property
    def hand_sizes_vector(self):
        """Return a vector of all players' current hand sizes."""
        hand_sizes = np.zeros(MAX_PLAYERS)
        for i, hand_size in enumerate(self.hand_sizes):
            hand_sizes[i] = hand_size
        return hand_sizes

    @property
    def discard_pile_sizes_vector(self):
        """Return a vector of all players' current discard pile sizes."""
        discard_pile_sizes = np.zeros(MAX_PLAYERS)
        for i, discard_pile_size in enumerate(self.discard_pile_sizes):
            discard_pile_sizes[i] = discard_pile_size
        return discard_pile_sizes

    @property
    def deck_sizes_vector(self):
        """Return a vector of all players' current deck sizes."""
        deck_sizes = np.zeros(MAX_PLAYERS)
        for i, deck_size in enumerate(self.deck_sizes):
            deck_sizes[i] = deck_size
        return deck_sizes

    @property
    def victory_tokens_vector(self):
        """Return a vector of all players' current victory tokens."""
        victory_tokens = np.zeros(MAX_PLAYERS)
        for i, num_victory_tokens in enumerate(self.victory_tokens):
            victory_tokens[i] = num_victory_tokens
        return victory_tokens

    @property
    def turns_played_vector(self):
        """Return a vector of all players' current turns played."""
        turns_played = np.zeros(MAX_PLAYERS)
        for i, num_turns_played in enumerate(self.turns_played):
            turns_played[i] = num_turns_played
        return turns_played

    @property
    def as_vector(self):
        """Return a vector representation of the game state."""
        singletons = np.array(
            [
                self.own_index,
                int(self.current_player_is_self),
                int(self.current_phase),
                int(self.current_interaction),
                self.turn_number,
                self.actions_remaining,
                self.buys_remaining,
                self.coppers_remaining,
                card_class_to_index(type(self.most_recently_played_card)) if self.most_recently_played_card is not None else 0,
                self.trade_route_coin_tokens,
            ]
        )
        return np.concatenate(
            (
                singletons,
                self.supply_vector,
                self.trash_vector,
                self.played_cards_vector,
                self.hand_vector,
                self.discard_pile_vector,
                self.hand_sizes_vector,
                self.discard_pile_sizes_vector,
                self.deck_sizes_vector,
                self.victory_tokens_vector,
                self.turns_played_vector,
            )
        )


class AIInteraction(Interaction):
    def send(self, message):
        # TODO: Turn off printing (useful for debugging)
        print(message)
        print()

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

    def display_discard_pile(self):
        pass

    def display_hand(self):
        pass

    def display_supply(self):
        pass

    def sleep_random(self):
        """
        Sleep to simulate thought unless we are running tests.
        """
        if not self.game.test:
            time_to_sleep = random.uniform(1, 3) 
            self.socketio.sleep(time_to_sleep)

    def choose_card_from_hand(self, prompt, force) -> Optional[cards.Card]:
        game_state = GameState(self.player, self.game, InteractionType.CHOOSE_CARD_FROM_HAND)
        print(game_state.as_vector)

        cards_chosen = self.choose_cards_from_hand(prompt, force, max_cards=1)
        if not cards_chosen:
            return None
        return cards_chosen[0]

    def choose_cards_from_hand(self, prompt, force, max_cards=1) -> List[cards.Card]:
        game_state = GameState(self.player, self.game, InteractionType.CHOOSE_CARDS_FROM_HAND)
        print(game_state.as_vector)

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
        while True:
            try:
                self.display_hand()
                if force:
                    cards_chosen = random.sample(self.hand, max_cards)
                else:
                    num_cards = random.randint(0, max_cards)
                    cards_chosen = random.sample(self.hand, num_cards)
                return cards_chosen
            except (IndexError, ValueError):
                print('That is not a valid choice.\n')
                raise

    def choose_specific_card_class_from_hand(self, prompt, force, card_class):
        game_state = GameState(self.player, self.game, InteractionType.CHOOSE_SPECIFIC_CARD_CLASS_FROM_HAND)
        print(game_state.as_vector)

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
        game_state = GameState(self.player, self.game, InteractionType.CHOOSE_SPECIFIC_CARD_TYPE_FROM_HAND)
        print(game_state.as_vector)

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

    def choose_card_from_discard_pile(self, prompt, force):
        game_state = GameState(self.player, self.game, InteractionType.CHOOSE_CARD_FROM_DISCARD_PILE)
        print(game_state.as_vector)

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
        game_state = GameState(self.player, self.game, InteractionType.CHOOSE_TREASURES_FROM_HAND)
        print(game_state.as_vector)

        # The CPU will always choose all available Treasures
        self.sleep_random()
        print(prompt)
        print()
        while True:
            try:
                available_treasures = [card for card in self.hand if cards.CardType.TREASURE in card.types]
                if not available_treasures:
                    print('There are no treasures in your hand.\n')
                    return []
                print(f'Available treasures: {", ".join(map(str, available_treasures))}')
                return available_treasures
            except (IndexError, ValueError):
                self.send('That is not a valid choice.')

    def choose_card_class_from_supply(self, prompt, max_cost, force, invalid_card_classes=None, exact_cost=False):
        game_state = GameState(self.player, self.game, InteractionType.CHOOSE_CARD_CLASS_FROM_SUPPLY)
        print(game_state.as_vector)
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
        game_state = GameState(self.player, self.game, InteractionType.CHOOSE_SPECIFIC_CARD_TYPE_FROM_SUPPLY)
        print(game_state.as_vector)

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
        game_state = GameState(self.player, self.game, InteractionType.CHOOSE_SPECIFIC_CARD_TYPE_FROM_TRASH)
        print(game_state.as_vector)

        self.sleep_random()
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
        game_state = GameState(self.player, self.game, InteractionType.CHOOSE_YES_OR_NO)
        print(game_state.as_vector)

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
        game_state = GameState(self.player, self.game, InteractionType.CHOOSE_FROM_RANGE)
        print(game_state.as_vector)

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
        game_state = GameState(self.player, self.game, InteractionType.CHOOSE_FROM_OPTIONS)
        print(game_state.as_vector)

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

    def new_turn(self):
        if self.socketio is not None:
            self.socketio.emit('new turn', {'player': self.player.name}, room=self.room)
