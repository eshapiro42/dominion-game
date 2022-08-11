from __future__ import annotations

from abc import ABCMeta, abstractmethod
from collections import defaultdict
from typing import TYPE_CHECKING, List, Dict, Type

from .cards.cards import Card, CardType
from .expansions import GuildsExpansion
from .grammar import a, s
from .interactions import AutoInteraction, BrowserInteraction

if TYPE_CHECKING:
    from .cards.cards import ActionCard, TreasureCard
    from .game import Game
    from .hooks import TreasureHook, PostGainHook, PostTreasureHook, PreCleanupHook
    from .player import Player
    from .supply import Supply


class Turn:
    '''
    Dominion turn object.

    All components of a player's turn are instantiated by this class.

    Args:
        player: The player whose turn it currently is.
    '''
    def __init__(self, player: Player):
        self._player = player
        self.player.turn = self
        self._game = self.player.game
        self._actions_remaining = 1
        self._buys_remaining = 1
        self._coppers_remaining = 0
        self._current_phase = "Action Phase"
        self._action_phase = ActionPhase(turn=self)
        self._buy_phase = BuyPhase(turn=self)
        self._cleanup_phase = CleanupPhase(turn=self)
        self._treasure_hooks = defaultdict(list)
        self._post_treasure_hooks = []
        self._post_gain_hooks = defaultdict(list)
        self._pre_cleanup_hooks = []
        self._invalid_card_classes = []
        self._cost_modifiers = defaultdict(int)

    @property
    def player(self) -> Player:
        """
        The player whose turn it currently is.
        """
        return self._player

    @property
    def game(self) -> Game:
        """
        The game which is currently being played.
        """
        return self._game

    @property
    def actions_remaining(self) -> int:
        """
        The number of actions the player has left this turn.
        """
        return self._actions_remaining

    @actions_remaining.setter
    def actions_remaining(self, actions_remaining: int):
        self._actions_remaining = actions_remaining

    @property
    def buys_remaining(self) -> int:
        """
        The number of buys the player has left this turn.
        """
        return self._buys_remaining

    @buys_remaining.setter
    def buys_remaining(self, buys_remaining: int):
        self._buys_remaining = buys_remaining

    @property
    def coppers_remaining(self) -> int:
        """
        The number of coppers the player has left to spend this turn.
        """
        return self._coppers_remaining

    @coppers_remaining.setter
    def coppers_remaining(self, coppers_remaining: int):
        self._coppers_remaining = coppers_remaining

    @property
    def current_phase(self) -> str:
        """
        A string representing the current phase of the turn.
        """
        return self._current_phase

    @current_phase.setter
    def current_phase(self, current_phase: str):
        self._current_phase = current_phase

    @property
    def action_phase(self) -> ActionPhase:
        """
        The action phase of this Turn.
        """
        return self._action_phase

    @property
    def buy_phase(self) -> BuyPhase:
        """
        The buy phase of this Turn.
        """
        return self._buy_phase

    @property
    def cleanup_phase(self) -> CleanupPhase:
        """
        The cleanup phase of this Turn.
        """
        return self._cleanup_phase

    @property
    def treasure_hooks(self) -> Dict[Type[Card], List[TreasureHook]]:
        """
        A dictionary of treasure hooks registered for this turn.
        """
        return self._treasure_hooks

    @treasure_hooks.setter
    def treasure_hooks(self, treasure_hooks: Dict[Type[Card], List[TreasureHook]]):
        self._treasure_hooks = treasure_hooks

    @property
    def post_treasure_hooks(self) -> List[PostTreasureHook]:
        """
        A list of post-treasure hooks registered for this turn.
        """
        return self._post_treasure_hooks

    @post_treasure_hooks.setter
    def post_treasure_hooks(self, post_treasure_hooks: List[PostTreasureHook]):
        self._post_treasure_hooks = post_treasure_hooks

    @property
    def post_gain_hooks(self) -> Dict[Type[Card], List[PostGainHook]]:
        """
        A dictionary of post-gain hooks registered for this turn.
        """
        return self._post_gain_hooks

    @post_gain_hooks.setter
    def post_gain_hooks(self, post_gain_hooks: Dict[Type[Card], List[PostGainHook]]):
        self._post_gain_hooks = post_gain_hooks

    @property
    def pre_cleanup_hooks(self) -> List[PreCleanupHook]:
        """
        A list of pre-cleanup hooks registered for this turn.
        """
        return self._pre_cleanup_hooks

    @pre_cleanup_hooks.setter
    def pre_cleanup_hooks(self, pre_cleanup_hooks: List[PreCleanupHook]):
        self._pre_cleanup_hooks = pre_cleanup_hooks

    @property
    def invalid_card_classes(self) -> List[Type[Card]]:
        """
        A list of card classes that cannot be purchased this turn.
        """
        return self._invalid_card_classes

    @invalid_card_classes.setter
    def invalid_card_classes(self, invalid_card_classes: List[Type[Card]]):
        self._invalid_card_classes = invalid_card_classes

    @property
    def cost_modifiers(self) -> Dict[Type[Card], int]:
        """
        A dictionary of cost modifiers for cards.
        """
        return self._cost_modifiers

    def get_cost(self, card_like: Card | Type[Card]) -> int:
        """
        Get the cost of a card or card class.

        Args:
            card: The card or card class to get the cost of.

        Returns:
            The cost of the card or card class.
        """
        if isinstance(card_like, Card):
            cost_modifier = self.cost_modifiers[type(card_like)]
        else:
            cost_modifier = self.cost_modifiers[card_like]
        return max(card_like._cost + cost_modifier, 0)

    def start(self):
        '''
        Start the Turn.

        This increments the current player's number of turns played.
        It first activates any pre-turn hooks registered to the current player.
        It then runs the Action, Buy and Cleanup phases in that order.
        '''
        self.player.turns_played += 1
        self.player.interactions.new_turn()
        self.process_pre_turn_hooks()
        self.player.interactions.display_hand()
        self.action_phase.start()
        self.buy_phase.start()
        self.cleanup_phase.start()

    def add_treasure_hook(self, treasure_hook: TreasureHook, card_class: Type[Card]):
        '''
        Add a turn-wide treasure hook to a specific card class.

        Args:
            treasure_hook: The treasure hook to add.
            card_class: The card class which should activate the treasure Hook.
        '''
        self.treasure_hooks[card_class].append(treasure_hook)

    def add_post_treasure_hook(self, post_treasure_hook: PostTreasureHook):
        '''
        Add a Turn-wide post-treasure hook.

        Args:
            post_treasure_hook: The post-treasure hook to add.
        '''
        self.post_treasure_hooks.append(post_treasure_hook)

    def add_post_gain_hook(self, post_gain_hook: PostGainHook, card_class: Type[Card]):
        '''
        Add a turn-wide post-gain hook to a specific card class.

        Args:
            post_gain_hook: The post-gain hook to add.
            card_class: The card class which should activate the post-gain hook.
        '''
        self.post_gain_hooks[card_class].append(post_gain_hook)

    def add_pre_cleanup_hook(self, pre_cleanup_hook: PreCleanupHook):
        '''
        Add a turn-wide pre-cleanup hook.

        Args:
            pre_cleanup_hook: The pre-cleanup hook to add.
        '''
        self.pre_cleanup_hooks.append(pre_cleanup_hook)

    def plus_actions(self, num_actions: int, message: bool = True):
        """
        Add actions to the player's turn.

        Args:
            num_actions: The number of actions to add.
            message: Whether or not to broadcast the change.
        """
        self.actions_remaining += num_actions
        if message:
            if num_actions > 0:
                self.game.broadcast(f"+{s(num_actions, 'action')} → {s(self.actions_remaining, 'action')}.")
            elif num_actions < 0:
                self.game.broadcast(f"-{s(-num_actions, 'action')} → {s(self.actions_remaining, 'action')}.")

    def plus_buys(self, num_buys: int, message: bool = True):
        """
        Add buys to the player's turn.

        Args:
            num_buys: The number of buys to add.
            message: Whether or not to broadcast the change.
        """
        self.buys_remaining += num_buys
        if message:
            if num_buys > 0:
                self.game.broadcast(f"+{s(num_buys, 'buy')} → {s(self.buys_remaining, 'buy')}.")
            elif num_buys < 0:
                self.buys_remaining(f"-{s(-num_buys, 'buy')} → {s(self.buys_remaining,'buy')}.")

    def plus_coppers(self, num_coppers: int, message: bool = True):
        """
        Add coppers to the player's turn.

        Args:
            num_coppers: The number of coppers to add.
            message: Whether or not to broadcast the change.
        """
        self.coppers_remaining += num_coppers
        if message:
            if num_coppers > 0:
                self.game.broadcast(f'+{num_coppers} $ → {self.coppers_remaining} $.')
            elif num_coppers < 0:
                self.game.broadcast(f'-{-num_coppers} $ → {self.coppers_remaining} $.')

    def display(self):
        """
        Send information about the turn to the client.
        """
        current_turn_info = {
            "current_phase": self.current_phase,
            "actions": s(self.actions_remaining, "Action"),
            "buys": s(self.buys_remaining, "Buy"),
            "coppers": self.coppers_remaining,
            "hand_size": s(len(self.player.hand), "Card"),
            "turns_played": self.player.turns_played,
        }
        if GuildsExpansion in self.game.expansions:
            current_turn_info["coffers"] = s(self.player.coffers, "Coffer")
        self.game.socketio.emit(
            "current turn info",
            current_turn_info,
            room=self.game.room,
        )

    def process_pre_turn_hooks(self):
        '''
        Activate any pre turn hooks registered to the current player.
        '''
        # Activate any pre turn hooks registered to the current player
        expired_hooks = []
        for pre_turn_hook in self.game.pre_turn_hooks:
            if pre_turn_hook.player == self.player:
                pre_turn_hook()
                if not pre_turn_hook.persistent:
                    expired_hooks.append(pre_turn_hook)
        # Remove any non-persistent hooks
        for hook in expired_hooks:
            self.game.pre_turn_hooks.remove(hook)

    def modify_cost(self, card_class: Type[Card], modifier: int):
        """
        Add a cost modifier to a card class.

        Args:
            card_class: The card class to modify.
            modifier: The modifier to add.
        """
        self.cost_modifiers[card_class] += modifier
        self.game.supply.modify_cost(card_class, modifier)


class Phase(metaclass=ABCMeta):
    '''
    Base class for the various different phases of a turn.

    Args:
        turn: The current turn.
    
    Args:
        player (:obj:`.player.Player`): The player whose turn it currently is.
        game (:obj:`.game.Game`): The game which is currently being played.
        supply (:obj:`.supply.Supply`): The supply for this game.
    '''
    def __init__(self, turn: Turn):
        self._turn = turn
        self._player = self.turn.player
        self._game = self.player.game
        self._supply = self.player.game.supply

    @property
    def turn(self) -> Turn:
        """
        The current turn.
        """
        return self._turn

    @property
    def player(self) -> Player:
        """
        The player whose turn it currently is.
        """
        return self._player

    @property
    def game(self) -> Game:
        """
        The current game.
        """
        return self._game

    @property
    def supply(self) -> Supply:
        """
        The current game's supply.
        """
        return self._supply

    @abstractmethod
    def start(self):
        '''
        Start the phase.
        '''
        pass


class ActionPhase(Phase):
    '''
    Action phase of the current turn.
    '''    
    def start(self):
        '''
        Start the Action phase. While the player has Actions remaining and Action cards
        in their hand, ask them which Action cards they would like to play (then play them).     
        '''
        while self.turn.actions_remaining > 0:
            # If there are no action cards in the player's hand, move on
            if not any(CardType.ACTION in card.types for card in self.player.hand):
                self.player.interactions.send('No Action cards to play. Ending action phase.')
                return
            prompt = f"You have {s(self.turn.actions_remaining, 'action')}. Select an Action card to play."
            card = self.player.interactions.choose_specific_card_type_from_hand(prompt=prompt, card_type=CardType.ACTION)
            if card is None:
                # The player is forfeiting their action phase
                self.player.interactions.send('Action phase forfeited.')
                return
            self.play(card)
        self.player.interactions.send('No actions left. Ending action phase.')

    def play(self, card: ActionCard):
        '''
        Play an action card.

        This adds the action card to the player's played cards area, subtracts
        one from the turn's remaining actions, and steps through the action card's effects.

        Args:
            card: The action card to play.
        '''
        self.game.broadcast(f'{self.player} played {a(card)}.')
        # Add the card to the played cards area
        self.player.play(card)
        # Playing an action card uses one action
        self.turn.plus_actions(-1)
        self.walk_through_action_card(card)

    def play_without_side_effects(self, card: ActionCard):
        '''
        Play an action card without losing actions or moving the card to the played cards area.

        Args:
            card: The action card to play.
        '''
        self.game.broadcast(f'{self.player} played {a(card)}.')
        self.walk_through_action_card(card)

    def walk_through_action_card(self, card: ActionCard):
        '''
        First tally up all effects of playing an action card (+cards, +actions, +buys, +$),
        then play the card.

        Args:
            card: The action card to play.        
        '''
        # Draw any additional cards specified on the card
        self.player.draw(card.extra_cards)
        # Add back any additional actions on the card
        self.turn.plus_actions(card.extra_actions)
        # Add any additional buys on the card
        self.turn.plus_buys(card.extra_buys)
        # Add any additional coppers on the card
        self.turn.plus_coppers(card.extra_coppers)
        # Do whatever the card is supposed to do
        card.play()


class BuyPhase(Phase):
    '''
    Buy phase of the current turn.
    '''
    def start(self):
        '''
        Start the buy phase. 

        First, ask the player which treasures they would like to play this turn.

        When a treasure is played, any side effects and treasure hooks registered to that
        treasure will be activated.

        Before cards are bought, any pre-buy hooks registered to cards in the supply will
        be activated.

        While the player has buys remaining, ask them which cards 
        they would like to buy (then gain them).
        '''
        self.turn.current_phase = "Buy Phase"
        # Run any expansion-specific pre buy actions
        for expansion_instance in self.supply.customization.expansions:
            expansion_instance.additional_pre_buy_phase_actions()
        # Find any Treasures in the player's hand
        treasures_available = [card for card in self.player.hand if CardType.TREASURE in card.types]
        # Ask the player which Treasures they would like to play
        treasures_to_play = []
        if treasures_available:
            prompt = f'Which Treasures would you like to play this turn?'
            if isinstance(self.player.interactions, BrowserInteraction) or isinstance(self.player.interactions, AutoInteraction):
                treasures_to_play = self.player.interactions.choose_treasures_from_hand(prompt)
            else:
                while treasures_available:
                    options = ['Play all Treasures'] + treasures_available
                    choice = self.player.interactions.choose_from_options(prompt, options, force=False)
                    if choice is None:
                        break
                    elif choice == 'Play all Treasures':
                        treasures_to_play += treasures_available
                        break
                    else:
                        treasures_available.remove(choice)
                        treasures_to_play.append(choice)
        self.play_treasures(treasures_to_play)
        # Activate any post-treasure hooks
        self.process_post_treasure_hooks()
        # Activate any pre-buy hooks registered to cards in the Supply
        self.process_pre_buy_hooks()
        # Buy cards
        while self.turn.buys_remaining > 0:
            prompt = f"You have {self.turn.coppers_remaining} $ to spend and {s(self.turn.buys_remaining, 'buy')}. Select a card to buy."
            card_class = self.player.interactions.choose_card_class_from_supply(prompt=prompt, max_cost=self.turn.coppers_remaining, force=False, invalid_card_classes=self.turn.invalid_card_classes)
            if card_class is None:
                # The player is forfeiting their buy phase
                self.player.interactions.send('Buy phase forfeited.')
                return
            else:
                self.buy(card_class)
        self.player.interactions.send('No buys left. Ending buy phase.')

    def process_treasure_hooks(self, treasure: TreasureCard):
        '''
        Activate any treasure hooks registered to a treasure.

        Args:
            treasure: The treasure whose hooks to activate.
        '''
        # Check if there are any game-wide hooks registered to the played Treasures
        expired_hooks = []
        if type(treasure) in self.game.treasure_hooks:
            # Activate any hooks caused by playing the Treasure
            for treasure_hook in self.game.treasure_hooks[type(treasure)]:
                treasure_hook()
                if not treasure_hook.persistent:
                    expired_hooks.append(treasure_hook)
            # Remove any non-persistent hooks
            for hook in expired_hooks:
                self.game.treasure_hooks[type(treasure)].remove(hook)
        # Check if there are any turn-wide hooks registered to the played Treasures
        expired_hooks = []
        if type(treasure) in self.turn.treasure_hooks:
            # Activate any hooks caused by playing the Treasure
            for treasure_hook in self.turn.treasure_hooks[type(treasure)]:
                treasure_hook()
                if not treasure_hook.persistent:
                    expired_hooks.append(treasure_hook)
            # Remove any non-persistent hooks
            for hook in expired_hooks:
                self.turn.treasure_hooks[type(treasure)].remove(hook)

    def process_post_treasure_hooks(self):
        '''
        Activate any post-treasure hooks currently registered.
        '''
        expired_hooks = []
        # Activate any hooks caused by playing the Treasure
        for post_treasure_hook in self.turn.post_treasure_hooks:
            post_treasure_hook()
            if not post_treasure_hook.persistent:
                expired_hooks.append(post_treasure_hook)
        # Remove any non-persistent hooks
        for hook in expired_hooks:
            self.turn.post_treasure_hooks.remove(hook)

    def play_treasures(self, treasures: List[TreasureCard]):
        '''
        Play treasures.

        This will activate any side effects caused by playing the treasures.

        It will then activate any treasure hooks registered to the treasures.

        Args:
            treasures: A list of treasure cards to play.
        '''
        if not treasures:
            self.game.broadcast(f"{self.player} did not play any Treasures.")
            return
        # Allow each expansion to modify the order of Treasures played
        for expansion_instance in self.supply.customization.expansions:
            treasures = expansion_instance.order_treasures(self.player, treasures)
        treasures_string = Card.group_and_sort_by_cost(treasures)
        self.game.broadcast(f"{self.player} played Treasures: {treasures_string}.")
        # Play the Treasures
        for treasure in treasures:
            # Add the Treasure to the played cards area and remove from hand
            self.player.play(treasure)
            # Activate side effects cause by playing this Treasure
            if hasattr(treasure, 'play'):
                treasure.play()
            # Process any Treasure hooks
            self.process_treasure_hooks(treasure)
            # Add the value of this Treasure
            self.turn.coppers_remaining += treasure.value

    def process_pre_buy_hooks(self):
        '''
        Activate any game-wide pre buy hooks registered to cards in the supply.
        '''
        expired_hooks = []
        for card_class in self.supply.card_stacks:
            for pre_buy_hook in self.game.pre_buy_hooks[card_class]:
                pre_buy_hook()
                if not pre_buy_hook.persistent:
                    expired_hooks.append(pre_buy_hook)
            # Remove any non-persistent hooks
            for hook in expired_hooks:
                self.game.pre_buy_hooks[card_class].remove(hook)

    def process_post_buy_hooks(self, purchased_card: Card):
        '''
        Activate any game-wide post buy hooks registered to a specific card class.

        Args:
            purchased_card: The card to process post buy hooks for.
        '''
        card_class = type(purchased_card)
        expired_hooks = []
        for post_buy_hook in self.game.post_buy_hooks[card_class]:
            post_buy_hook(self.player, purchased_card)
            if not post_buy_hook.persistent:
                expired_hooks.append(post_buy_hook)
        # Remove any non-persistent hooks
        for hook in expired_hooks:
            self.game.post_buy_hooks[card_class].remove(hook)

    def buy(self, card_class: Type[Card]):
        '''
        Buy a card from the supply.

        First, the remaining buys for this turn are decremented by one.

        The current player will gain the card and its modified cost will be subtracted from
        their remaining coins to spend this turn.

        Args:
            card_class: The class of card to buy. 
        '''
        # Buying a card uses one buy
        self.turn.buys_remaining -= 1
        # Gain the desired card
        self.game.broadcast(f'{self.player} bought {a(card_class.name)}.')
        purchased_card = self.player.gain(card_class, message=False)[0]
        self.turn.coppers_remaining -= self.supply.card_stacks[card_class].modified_cost
        # Activate any post-buy hooks registered to this card class
        self.process_post_buy_hooks(purchased_card)

    def gain_without_side_effects(self, prompt: str, max_cost: int, force: bool, exact_cost: bool = False):
        '''
        Allow the player to gain a card from the supply.

        The current player will gain the card.

        Remaining buys and coins for this turn are not affected.

        Args:
            prompt: The prompt to display to the player.
            max_cost: The maximum cost of the card to gain.
            force: Whether to force the player to gain a card.
            exact_cost: Whether to force the player to gain a card with the exact specified cost.
        '''
        card_class = self.player.interactions.choose_card_class_from_supply(prompt=prompt, max_cost=max_cost, force=force, exact_cost=exact_cost)
        if card_class is None:
            self.game.broadcast(f'{self.player} did not gain anything.')
            return
        else:
            # Gain the desired card
            self.game.broadcast(f'{self.player} gained {a(card_class.name)}.')
            self.player.gain(card_class, message=False)


class CleanupPhase(Phase):
    '''
    Cleanup phase of the current Turn.
    '''
    def process_pre_cleanup_hooks(self):
        '''
        Activate any pre-cleanup hooks currently registered.
        '''
        expired_hooks = []
        # Activate any hooks caused by playing the Treasure
        for pre_cleanup_hook in self.turn.pre_cleanup_hooks:
            pre_cleanup_hook()
            if not pre_cleanup_hook.persistent:
                expired_hooks.append(pre_cleanup_hook)
        # Remove any non-persistent hooks
        for hook in expired_hooks:
            self.turn.pre_cleanup_hooks.remove(hook)

    def start(self):
        '''
        Start the cleanup phase.

        First, the player's played cards and hand are moved to their discard pile.
        The player draws a new hand, shuffling if necessary. Their new hand for
        the next turn is displayed.

        All cards in the supply have their cost modifiers reset to the default.
        '''
        self.turn.current_phase = "Cleanup Phase"
        # Process any pre-cleanup hooks registered this turn
        self.process_pre_cleanup_hooks()
        # Clean up the player's mat
        self.player.cleanup()
        # Show their hand for next turn
        self.player.interactions.display_hand()
        # Set the player's turn to None
        self.player.turn = None
        # Reset all card's cost modifiers
        self.supply.reset_costs()
        if self.game.test:
            print([card_class.name for card_class in self.supply.card_stacks])
            for card in self.player.all_cards:
                print(card, card.owner, self.player)
                assert card.owner == self.player
