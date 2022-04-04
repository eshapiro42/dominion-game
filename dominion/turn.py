import copy
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from dataclasses import dataclass

from .cards import cards, base_cards
from .grammar import a, s
from .interactions import AutoInteraction, BrowserInteraction


class Turn:
    '''Dominion Turn object.

    All components of a player's turn are instantiated by this class.

    Args:
        player (:obj:`player.Player`): The Player whose turn it currently is.

    Attributes:
        game (:obj:`.game.Game`): The Game which is currently being played.
        actions_remaining (:obj:`int`): The number of Actions the player has left this turn. Starts at 1.
        buys_remaining (:obj:`int`): The number of Buys the player has left this turn. Starts at 1.
        coppers_remaining (:obj:`int`): The number of Coins the player has left to spend this turn. Starts at 0.
        action_phase (:obj:`ActionPhase`): This Turn's Action phase.
        buy_phase (:obj:`BuyPhase`): This Turn's Buy phase.
        cleanup_phase (:obj:`CleanupPhase`): This Turn's Cleanup phase.
        treasure_hooks (:obj:`dict` with keys :obj:`type(cards.Card)` and values :obj:`hooks.TreasureHook`): Turn-wide Treasure hooks registered for this turn.
        post_gain_hooks (:obj:`dict` with keys :obj:`type(cards.Card)` and values :obj:`hooks.PostGainHook`): Turn-wide post gain hooks registered for this turn.
        invalid_card_classes (:obj:`list` of :obj:`type(cards.Card)`): A list of card classes that cannot be purchased this turn.
    '''
    def __init__(self, player):
        self.player = player
        self.player.turn = self
        self.game = self.player.game
        self.actions_remaining = 1
        self.buys_remaining = 1
        self.coppers_remaining = 0
        self.current_phase = "Action Phase"
        self.action_phase = ActionPhase(turn=self)
        self.buy_phase = BuyPhase(turn=self)
        self.cleanup_phase = CleanupPhase(turn=self)
        self.treasure_hooks = defaultdict(list)
        self.post_gain_hooks = defaultdict(list)
        self.invalid_card_classes = []

    def start(self):
        '''
        Start the Turn.

        This increments the current Player's number of turns played.
        It then runs the Action, Buy and Cleanup phases in that order.
        '''
        self.player.turns_played += 1
        self.player.interactions.new_turn()
        self.player.interactions.display_hand()
        self.action_phase.start()
        self.buy_phase.start()
        self.cleanup_phase.start()

    def add_treasure_hook(self, treasure_hook, card_class):
        '''
        Add a Turn-wide Treasure Hook to a specific card_class.

        Args:
            treasure_hook (:obj:`.hooks.TreasureHook`): The Treasure Hook to add.
            card_class (:obj:`type(cards.Card)`): The card_class which should activate the Treasure Hook.
        '''
        self.treasure_hooks[card_class].append(treasure_hook)

    def add_post_gain_hook(self, post_gain_hook, card_class):
        '''
        Add a Turn-wide Pre Buy Hook to a specific card_class.

        Args:
            treasure_hook (:obj:`.hooks.PreBuyHook`): The Pre Buy Hook to add.
            card_class (:obj:`type(cards.Card)`): The card_class which should activate the Treasure Hook.
        '''
        self.post_gain_hooks[card_class].append(post_gain_hook)

    def plus_actions(self, num_actions, message=True):
        self.actions_remaining += num_actions
        if message:
            if num_actions > 0:
                self.game.broadcast(f"+{s(num_actions, 'action')} → {s(self.actions_remaining, 'action')}.")
            elif num_actions < 0:
                self.game.broadcast(f"-{s(-num_actions, 'action')} → {s(self.actions_remaining, 'action')}.")

    def plus_buys(self, num_buys, message=True):
        self.buys_remaining += num_buys
        if message:
            if num_buys > 0:
                self.game.broadcast(f"+{s(num_buys, 'buy')} → {s(self.buys_remaining, 'buy')}.")
            elif num_buys < 0:
                self.buys_remaining(f"-{s(-num_buys, 'buy')} → {s(self.buys_remaining,'buy')}.")

    def plus_coppers(self, num_coppers, message=True):
        self.coppers_remaining += num_coppers
        if message:
            if num_coppers > 0:
                self.game.broadcast(f'+{num_coppers} $ → {self.coppers_remaining} $.')
            elif num_coppers < 0:
                self.game.broadcast(f'-{-num_coppers} $ → {self.coppers_remaining} $.')

    def display(self):
        self.game.socketio.emit(
            "current turn info",
            {
                "current_phase": self.current_phase,
                "actions": s(self.actions_remaining, "Action"),
                "buys": s(self.buys_remaining, "Buy"),
                "coppers": self.coppers_remaining,
                "turns_played": self.player.turns_played,
            }
        )


class Phase(metaclass=ABCMeta):
    '''
    Base class for the various different Phases of a turn.

    Args:
        turn (:obj:`Turn`): The current turn.
    
    Attributes:
        player (:obj:`.player.Player`): The player whose turn it currently is.
        game (:obj:`.game.Game`): The game which is currently being played.
        supply (:obj:`.supply.Supply`): The supply for this game.
    '''
    def __init__(self, turn):
        self.turn = turn
        self.player = self.turn.player
        self.game = self.player.game
        self.supply = self.player.game.supply

    @abstractmethod
    def start(self):
        '''Start the phase.'''
        pass


class ActionPhase(Phase):
    '''
    Action phase of the current Turn.

    Args:
        turn (:obj:`Turn`): The current turn.
    
    Attributes:
        player (:obj:`.player.Player`): The player whose turn it currently is.
        game (:obj:`.game.Game`): The game which is currently being played.
        supply (:obj:`.supply.Supply`): The supply for this game.
    '''    
    def start(self):
        '''
        Start the Action phase. While the player has Actions remaining and Action cards
        in their hand, ask them which Action cards they would like to play (then play them).     
        '''
        while self.turn.actions_remaining > 0:
            # If there are no action cards in the player's hand, move on
            if not any(cards.CardType.ACTION in card.types for card in self.player.hand):
                self.player.interactions.send('No Action cards to play. Ending action phase.')
                return
            prompt = f"You have {s(self.turn.actions_remaining, 'action')}. Select an Action card to play."
            card = self.player.interactions.choose_specific_card_type_from_hand(prompt=prompt, card_type=cards.CardType.ACTION)
            if card is None:
                # The player is forfeiting their action phase
                self.player.interactions.send('Action phase forfeited.')
                return
            self.play(card)
        self.player.interactions.send('No actions left. Ending action phase.')

    def play(self, card):
        '''
        Play an Action card.

        This adds the Action card to the player's played cards area, subtracts
        one from the turn's remaining actions, and steps through the Action card's effects.

        Args:
            card (:obj:`cards.ActionCard`): The Action card to play.
        '''
        self.game.broadcast(f'{self.player} played {a(card)}.')
        # Add the card to the played cards area
        self.player.play(card)
        # Playing an action card uses one action
        self.turn.plus_actions(-1)
        self.walk_through_action_card(card)

    def play_without_side_effects(self, card):
        '''
        Play a card without losing actions or moving the card to the played cards area.

        Args:
            card (:obj:`cards.ActionCard`): The Action card to play.
        '''
        self.game.broadcast(f'{self.player} played {a(card)}.')
        self.walk_through_action_card(card)

    def walk_through_action_card(self, card):
        '''
        First tally up all effects of playing an Action card (+cards, +actions, +buys, +$),
        then play the card.

        Args:
            card (:obj:`cards.ActionCard`): The Action card to play.        
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
    Buy phase of the current Turn.

    Args:
        turn (:obj:`Turn`): The current turn.
    
    Attributes:
        player (:obj:`.player.Player`): The player whose turn it currently is.
        game (:obj:`.game.Game`): The game which is currently being played.
        supply (:obj:`.supply.Supply`): The supply for this game.
    '''
    def start(self):
        '''
        Start the Buy phase. 

        First, ask the player which Treasures they would like to play this turn.

        When a Treasure is played, any side effects and treasure hooks registered to that
        Treasure will be activated.

        Before cards are bought, any pre-buy hooks registered to cards in the Supply will
        be activated.

        While the player has Buys remaining, ask them which cards 
        they would like to buy (then gain them).

        '''
        self.turn.current_phase = "Buy Phase"
        # Find any Treasures in the player's hand
        treasures_available = []
        for card in self.player.hand:
            if cards.CardType.TREASURE in card.types:
                treasures_available.append(card)
        # Ask the player which Treasures they would like to play
        prompt = f'Which Treasures would you like to play this turn?'
        if isinstance(self.player.interactions, BrowserInteraction) or isinstance(self.player.interactions, AutoInteraction):
            treasures_to_play = self.player.interactions.choose_treasures_from_hand(prompt)
        else:
            treasures_to_play = []
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

    def process_treasure_hooks(self, treasure):
        '''
        Activate any treasure hooks registered to a Treasure.

        Args:
            treasure (:obj:`cards.TreasureCard`): The Treasure whose hooks to activate.
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

    def play_treasures(self, treasures):
        '''
        Play Treasures.

        This will activate any side effects caused by playing the Treasures.

        It will then activate any treasure hooks registered to the Treasures.

        Args:
            list[treasure] (:obj:`cards.TreasureCard`): The Treasures whose hooks to activate.
        '''
        # Get a pretty, sorted list of the Treasures
        treasure_name_counts = defaultdict(int) # compute as a dict first since that's easier
        for treasure in treasures:
            treasure_name_counts[treasure.name] += 1
        treasure_counts = [(self.supply.card_name_to_card_class(name), quantity) for name, quantity in treasure_name_counts.items()] # convert from dict[treasure_name, count] into list[tuple(treasure_class, count)]
        # Sort the treasures by cost
        sorted_treasure_counts = sorted(treasure_counts, key=lambda treasure_tuple: treasure_tuple[0].cost)
        treasure_strings = [s(quantity, treasure.name) for treasure, quantity in sorted_treasure_counts]
        self.game.broadcast(f"{self.player} played Treasures: {', '.join(treasure_strings)}.")
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
        Activate any game-wide pre buy hooks registered to cards in the Supply.
        '''
        # Activate any game-wide pre-buy hooks registered to cards in the Supply
        expired_hooks = []
        for card_class in self.supply.card_stacks:
            for pre_buy_hook in self.game.pre_buy_hooks[card_class]:
                pre_buy_hook()
                if not pre_buy_hook.persistent:
                    expired_hooks.append(pre_buy_hook)
            # Remove any non-persistent hooks
            for hook in expired_hooks:
                self.game.treasure_hooks[card_class].remove(hook)

    def buy(self, card_class):
        '''
        Buy a card from the Supply.

        First, the remaining buys for this turn are decremented by one.

        The current player will gain the card and its modified cost will be subtracted from
        their remaining coins to spend this turn.

        Args:
            card_class(:obj:`type(cards.Card)`): The class of card to buy. 
        '''
        # Buying a card uses one buy
        self.turn.buys_remaining -= 1
        # Gain the desired card
        self.game.broadcast(f'{self.player} bought {a(card_class.name)}.')
        self.player.gain(card_class, message=False)
        self.turn.coppers_remaining -= self.supply.card_stacks[card_class].modified_cost

    def buy_without_side_effects(self, max_cost, force, exact_cost=False):
        '''
        Buy a card from the Supply.

        The current player will gain the card.

        Remaining buys and coins for this turn are not affected.

        Args:
            card_class(:obj:`type(cards.Card)`): The class of card to buy. 
        '''
        prompt = f'You have {max_cost} $ to spend. Select a card to buy.'
        card_class = self.player.interactions.choose_card_class_from_supply(prompt=prompt, max_cost=max_cost, force=force, exact_cost=exact_cost)
        if card_class is None:
            self.game.broadcast(f'{self.player} did not buy anything.')
            return
        else:
            # Gain the desired card
            self.game.broadcast(f'{self.player} bought {a(card_class.name)}.')
            self.player.gain(card_class, message=False)


class CleanupPhase(Phase):
    '''
    Cleanup phase of the current Turn.

    Args:
        turn (:obj:`Turn`): The current turn.
    
    Attributes:
        player (:obj:`.player.Player`): The player whose turn it currently is.
        game (:obj:`.game.Game`): The game which is currently being played.
        supply (:obj:`.supply.Supply`): The supply for this game.
    ''' 
    def start(self):
        '''
        Start the cleanup phase.

        First, the player's played cards and hand are moved to their discard pile.
        The player draws a new hand, shuffling if necessary. Their new hand for
        the next turn is displayed.

        All cards in the Supply have their cost modifiers reset to the default.
        '''
        self.turn.current_phase = "Cleanup Phase"
        # Clean up the player's mat
        self.player.cleanup()
        # Show their hand for next turn
        self.player.interactions.send('Your hand for next turn:')
        self.player.interactions.display_hand()
        # Reset all card's cost modifiers
        self.supply.reset_costs()