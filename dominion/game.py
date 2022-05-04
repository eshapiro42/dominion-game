from __future__ import annotations

import itertools
import random

from collections import defaultdict
from typing import TYPE_CHECKING, Callable, Optional, Dict, List, Tuple, Type

from .cards.cards import Card, CardType
from .expansions import BaseExpansion, ProsperityExpansion, IntrigueExpansion
from .grammar import s
from .interactions import CLIInteraction
from .player import Player
from .supply import Supply
from .turn import Turn

if TYPE_CHECKING:
    from flask_socketio import SocketIO
    from .expansions.expansion import Expansion
    from .hooks import TreasureHook, PreBuyHook
    from .interactions.interaction import Interaction


class GameStartedError(Exception):
    '''
    Raised when the game has already started.
    '''
    def __init__(self):
        message = f'The game has already started'
        super().__init__(message)


class Game:
    '''
    Dominion Game object.

    All components of the game, as well as all game logic and
    the game state, are instantiated and contained within this
    class. The game loop is also run from here.

    Args:
        socketio: A Socket.IO server instance.
        room: The room ID for this game.
    '''
    def __init__(self, socketio: Optional[SocketIO] = None, room: Optional[str] = None, test: bool = False):
        self._socketio = socketio
        self._test = test # If not running tests, slows down CPU interactions to simulate thought
        self._room = room
        self._player_names = []
        self._player_sids = []
        self._player_interactions_classes = []
        self._players = []
        self._startable = False
        self._started = False
        self._kill_scheduled = False
        self._killed = False
        self._current_turn = None
        self._treasure_hooks = defaultdict(list)
        self._pre_buy_hooks = defaultdict(list)
        self._game_end_conditions = []
        self._expansions = set()
        self._allow_simultaneous_reactions = False
        self._distribute_cost = False
        self._disable_attack_cards = False
        self._require_plus_two_action = False
        self._require_drawer = False
        self._require_buy = False
        self._require_trashing = False

        self.add_expansion(BaseExpansion) # This must always be here or the game will not work
        # self.add_expansion(IntrigueExpansion)
        # self.add_expansion(ProsperityExpansion)

    @property
    def socketio(self) -> Optional[SocketIO]:
        '''
        The Socket.IO server instance.
        '''
        return self._socketio

    @property
    def test(self) -> bool:
        '''
        Whether the game is running in test mode.

        At present, test mode simply means the CPU players
        do not take unnecessary time to simulate thinking.
        '''
        return self._test

    @property
    def room(self) -> Optional[str]:
        '''
        The room ID for this game.
        '''
        return self._room

    @property
    def player_names(self) -> List[str]:
        '''
        A list of the names of players in the game.
        '''
        return self._player_names

    @player_names.setter
    def player_names(self, player_names: List[str]):
        self._player_names = player_names

    @property
    def player_sids(self) -> List[str]:
        '''
        A list of SIDs corresponding to each player in the game (these lists share an index).
        '''
        return self._player_sids

    @player_sids.setter
    def player_sids(self, player_sids: List[str]):
        self._player_sids = player_sids

    @property
    def player_interactions_classes(self) -> List[Type[Interaction]]:
        '''
        A list of interaction classes corresponding to each player in the game (these lists share an index).
        '''
        return self._player_interactions_classes

    @player_interactions_classes.setter
    def player_interactions_classes(self, player_interactions_classes: List[Type[Interaction]]):
        self._player_interactions_classes = player_interactions_classes

    @property
    def players(self) -> List[Player]:
        '''
        A list of Player objects corresponding to the players in this game.
        '''
        return self._players

    @players.setter
    def players(self, players: List[Player]):
        self._players = players

    @property
    def startable(self) -> bool:
        '''
        Whether the game can be started. This changes to True automatically when two players have joined.
        '''
        return self._startable

    @startable.setter
    def startable(self, startable: bool):
        self._startable = startable

    @property
    def started(self) -> bool:
        '''
        Whether the game has been started. This changes to True automatically when the game starts.
        '''
        return self._started

    @started.setter
    def started(self, started: bool):
        self._started = started

    @property
    def kill_scheduled(self) -> bool:
        '''
        Whether the game is scheduled to be killed.

        This changes to True automatically when all human players
        are disconnected from ther server. Once this happens, a
        timeout (currently 30 seconds) begins, after which the game
        will be killed if no human players have rejoined or this
        property is set back to False by some other means.
        '''
        return self._kill_scheduled

    @kill_scheduled.setter
    def kill_scheduled(self, kill_scheduled: bool):
        self._kill_scheduled = kill_scheduled

    @property
    def killed(self) -> bool:
        '''
        Whether the game has been killed.

        This changes to True automatically when the game is killed.
        '''
        return self._killed

    @killed.setter
    def killed(self, killed: bool):
        self._killed = killed
        
    @property
    def current_turn(self) -> Optional[Turn]:
        '''
        The Turn object corresponding to the current turn of the game.
        '''
        return self._current_turn

    @current_turn.setter
    def current_turn(self, current_turn: Turn):
        self._current_turn = current_turn

    @property
    def treasure_hooks(self) -> Dict[Type[Card], List[TreasureHook]]:
        '''
        A dictionary of game-wide :obj:`TreasureHook` instances, indexed by Card class.

        The values are lists of treasure hooks, since multiple treasure hooks can be registered to a single card.
        '''
        return self._treasure_hooks

    @treasure_hooks.setter
    def treasure_hooks(self, treasure_hooks: Dict[Type[Card], List[TreasureHook]]):
        self._treasure_hooks = treasure_hooks

    @property
    def pre_buy_hooks(self) -> Dict[Type[Card], List[PreBuyHook]]:
        '''
        A dictionary of game-wide :obj:`PreBuyHook` instances, indexed by Card class.

        The values are lists of pre-buy hooks, since multiple pre-buy hooks can be registered to a single card.
        '''
        return self._pre_buy_hooks

    @pre_buy_hooks.setter
    def pre_buy_hooks(self, pre_buy_hooks: Dict[Type[Card], List[PreBuyHook]]):
        self._pre_buy_hooks = pre_buy_hooks

    @property
    def game_end_conditions(self) -> List[Callable[[], Tuple[bool, Optional[str]]]]:
        """
        A list of functions that take no arguments and return
        a tuple of a boolean and an optional string. The boolean
        indicates whether the game has ended and the string is
        a message containing the reason why the game ended and
        which will be displayed to users.

        If the boolean returned is :obj:`False`, the game has
        not ended and so the second argument should be :obj:`None`.

        If the boolean returned is :obj:`True`, the second (string)
        argument must be provided.
        """
        return self._game_end_conditions

    @game_end_conditions.setter
    def game_end_conditions(self, game_end_conditions: List[Callable[[], Tuple[bool, Optional[str]]]]):
        self._game_end_conditions = game_end_conditions
    
    @property
    def expansions(self) -> List[Type[Expansion]]:
        """
        A list of expansion classes to be added into the game.
        """
        return self._expansions

    @expansions.setter
    def expansions(self, expansions: List[Type[Expansion]]):
        self._expansions = expansions

    @property
    def allow_simultaneous_reactions(self) -> bool:
        """
        Whether to allow simultaneous reactions for this game.

        When toggled, allows attacked players to react to the attack
        simultaneously (when sensible).
        """
        return self._allow_simultaneous_reactions

    @allow_simultaneous_reactions.setter
    def allow_simultaneous_reactions(self, allow_simultaneous_reactions: bool):
        self._allow_simultaneous_reactions = allow_simultaneous_reactions

    @property
    def distribute_cost(self) -> bool:
        """
        Whether to force a balanced distribution of card costs in the Supply.

        When toggled, ensures there are at least two cards each of cost {2, 3, 4, 5}.
        """
        return self._distribute_cost

    @distribute_cost.setter
    def distribute_cost(self, distribute_cost: bool):
        self._distribute_cost = distribute_cost

    @property
    def disable_attack_cards(self) -> bool:
        """
        Whether to disable attack cards.

        When toggled, attack cards are not allowed in the Supply.
        """
        return self._disable_attack_cards

    @disable_attack_cards.setter
    def disable_attack_cards(self, disable_attack_cards: bool):
        self._disable_attack_cards = disable_attack_cards

    @property
    def require_plus_two_action(self) -> bool:
        """
        Whether to require a card with +2 actions.

        If toggled, ensures there is at least one card in the Supply giving '+2 Actions'.
        """
        return self._require_plus_two_action

    @require_plus_two_action.setter
    def require_plus_two_action(self, require_plus_two_action: bool):
        self._require_plus_two_action = require_plus_two_action

    @property
    def require_drawer(self) -> bool:
        """
        Whether to require a card with >= +1 Card

        If toggled, ensures there is at least one card in the Supply giving '>= +1 Card'.
        """
        return self._require_drawer

    @require_drawer.setter
    def require_drawer(self, require_drawer: bool):
        self._require_drawer = require_drawer

    @property
    def require_buy(self) -> bool:
        """
        Whether to require a card with >= +1 Buy

        If toggled, ensures there is at least one card in the Supply giving '>= +1 Buy'.
        """
        return self._require_buy

    @require_buy.setter
    def require_buy(self, require_buy: bool):
        self._require_buy = require_buy

    @property
    def require_trashing(self) -> bool:
        """
        Whether to require a card that allows trashing.

        If toggled, ensures there is at least one card in the Supply that mentions "trash" in its description.
        It is possible that this is not a foolproof method, in which case a more robust method may be needed.
        """
        return self._require_trashing

    @require_trashing.setter
    def require_trashing(self, require_trashing: bool):
        self._require_trashing = require_trashing

    def add_treasure_hook(self, treasure_hook: TreasureHook, card_class: Type[Card]):
        '''
        Add a game-wide treasure hook to a specific card class.

        Args:
            treasure_hook: The treasure hook to add.
            card_class : The card class which should activate the treasure hook.
        '''
        self.treasure_hooks[card_class].append(treasure_hook)

    def add_pre_buy_hook(self, pre_buy_hook: PreBuyHook, card_class: Type[Card]):
        '''
        Add a game-wide pre-buy hook to a specific card class.

        Args:
            treasure_hook: The pre-buy hook to add.
            card_class: The card class which should activate the pre-buy hook.
        '''
        self.pre_buy_hooks[card_class].append(pre_buy_hook)

    def add_expansion(self, expansion: Type[Expansion]):
        '''
        Add an expansion into the game.

        Args:
            expansion: The expansion class to add into the game.
        '''
        self.expansions.add(expansion)

    def add_player(self, name: Optional[str] = None, sid: Optional[str] = None, interactions_class: Type[Interaction] = CLIInteraction):
        '''
        Add a new player into the game.
        
        Will fail if the game has already started.

        Will set :obj:`Game.startable` to :obj:`True` when the second player is added.

        Args:
            name: The player's name. If :obj:`None`, the player will be called a "Player N", where N is their player number.
            sid: The player's Socket.IO SID. Required for networked play.
            interactions_class: The player's interaction class. Defaults to :class:`~.cli.CLIInteraction`.
        '''
        # Players can only be added before the game starts
        if self.started:
            raise GameStartedError()
        if name is None:
            name = f'Player {self.num_players + 1}'
        self.player_names.append(name)
        self.player_sids.append(sid)
        self.player_interactions_classes.append(interactions_class)
        # If there are two players, the game is joinable
        if len(self.player_names) == 2:
            self.startable = True

    def start(self, debug: bool = False):
        '''
        Start the game.

        This method creates and sets up the supply, player objects, adds in desired expansions,
        decides turn order and runs the game loop.

        Args:
            debug: If :obj:`True`, does not run the game loop. Defaults to :obj:`False`. 
        '''
        # NOTE: THE ORDER OF EVENTS HERE IS EXTREMELY IMPORTANT!
        self.started = True
        # Create the supply
        self.supply = Supply(num_players=self.num_players)
        # Create each player object
        for player_name, player_sid, player_interactions_class in zip(self.player_names, self.player_sids, self.player_interactions_classes):
            player = Player(game=self, name=player_name, interactions_class=player_interactions_class, socketio=self.socketio, sid=player_sid)
            self.players.append(player)
            player.interactions.start()
        # Add in the desired expansions
        for expansion in self.expansions:
            expansion_instance = expansion(self)
            self.supply.customization.expansions.add(expansion_instance)
            self.game_end_conditions += expansion_instance.game_end_conditions
        expansion_names = sorted([expansion.name for expansion in self.expansions if expansion != BaseExpansion])
        if len(expansion_names) > 1:
            # Join the last two with "and" for easier readability
            expansion_names[-2] = f"{expansion_names[-2]} and {expansion_names[-1]}"
            expansion_names.pop()
            expansions_string = ", ".join(expansion_names)
            self.broadcast(f"Using {expansions_string} expansions.")
        elif len(expansion_names) == 1:
            expansion_name = expansion_names[0]
            self.broadcast(f"Using {expansion_name} expansion.")
        # Notify players if simultaneous reactions are allowed
        if self.allow_simultaneous_reactions:
            self.broadcast("Simultaneous reactions are allowed.")
        # Add in other supply customizations
        self.supply.customization.distribute_cost = self.distribute_cost
        self.supply.customization.disable_attack_cards = self.disable_attack_cards
        self.supply.customization.require_plus_two_action = self.require_plus_two_action
        self.supply.customization.require_drawer = self.require_drawer
        self.supply.customization.require_buy = self.require_buy
        self.supply.customization.require_trashing = self.require_trashing
        # Set up the supply
        self.supply.setup()
        # Print out the supply
        for player in self.players:
            player.interactions.display_supply()
        # Randomly decide turn order
        self.turn_order = random.sample(self.players, len(self.players))
        # Each player figures out the turn order of the other players
        for player in self.players:
            player.get_other_players()
        # Print out each player's hand (other than the starting player)
        for player in self.turn_order[1:]:
            player.interactions.display_hand()
        # Start the game loop!
        if not debug:
            self.game_loop()

    def game_loop(self):
        '''
        The main game loop. Cycles through turns for each player and checks for
        game end conditions after each turn.
        '''
        for player in itertools.cycle(self.turn_order):
            self.current_turn = Turn(player)
            self.current_turn.start()
            # Check if the game ended after each turn
            ended, explanation = self.ended
            if ended:
                # Game is over. Print out info.
                self.broadcast(explanation)
                self.broadcast('Game over!')
                victory_points_dict, turns_played_dict, winners = self.scores
                scores_str = ', '.join([f'{k}: {v}' for k, v in victory_points_dict.items()])
                self.broadcast(f'Scores: {scores_str}')
                turns_str = ', '.join([f'{k}: {v}' for k, v in turns_played_dict.items()])
                self.broadcast(f'Turns played: {turns_str}')
                winners_str = ', '.join(map(str, winners))
                self.broadcast(f'{s(len(winners), "Winner").split(" ")[-1]}: {winners_str}.')
                for player in self.players:
                    victory_cards = [card for card in player.all_cards if CardType.VICTORY in card.types]
                    other_cards = [card for card in player.all_cards if CardType.VICTORY not in card.types]
                    victory_cards_string = Card.group_and_sort_by_cost(victory_cards)
                    other_cards_string = Card.group_and_sort_by_cost(other_cards)
                    if victory_cards and other_cards:
                        all_cards_string = ", ".join((victory_cards_string, other_cards_string))
                        self.broadcast(f"{player}'s cards: {all_cards_string}.")
                    elif victory_cards:
                        self.broadcast(f"{player}'s cards: {victory_cards_string}.")
                    elif other_cards:
                        self.broadcast(f"{player}'s cards: {other_cards_string}.")
                if self.socketio is not None:
                    # Send formatted game end info to players
                    newsection = "<br><br>"
                    prompt = f"""
                        <b>Game over!</b>
                        {explanation}
                        {newsection}
                        <b>{s(len(winners), "Winner").split(" ")[-1]}:</b> {winners_str}
                        {newsection}
                        <b>Scores:</b> {scores_str}
                        {newsection}
                        <b>Turns played:</b> {turns_str}
                    """
                    self.socketio.emit(
                        'game over',
                        {'prompt': prompt},
                    )
                break

    def broadcast(self, message: str):
        '''
        Broadcast a message to each player in the game.

        Args:
            message: The message to broadcast to each player.
        '''
        for player in self.players:
            player.interactions.send(message)
        
    @property
    def ended(self) -> Tuple[bool, Optional[str]]:
        '''
        Check whether the game has ended.
        
        A tuple containing:

            game_ended: :obj:`True` if the game has ended, :obj:`False` otherwise.
            explanation: An explanation for why the game has ended, or :obj:`None` if the game has not ended.
        '''
        # Check if any game end condition has been met
        for game_end_condition in self.game_end_conditions:
            game_ended, explanation = game_end_condition()
            if game_ended:
                return True, explanation
        else:
            return False, None

    @property
    def scores(self) -> Tuple[Dict[Player, int], Dict[Player, int], List[str]]:
        '''
        The scores of each player.

        A tuple containing:

            victory_points_dict: A dictionary of scores indexed by Player.
            turns_played_dict: A dictionary of turns played indexed by Player.
            winners: A list of Player's names who won the game.
        '''
        # Count up victory points for each player
        victory_points_dict = {player: player.current_victory_points for player in self.players}
        # Count up turns played per player
        turns_played_dict = {player: player.turns_played for player in self.players}
        # Figure out the most victory points attained
        most_victory_points = max(victory_points_dict.values())
        # Figure out which players got that many victory points
        players_with_most_victory_points = []
        for player, victory_points in victory_points_dict.items():
            if victory_points == most_victory_points:
                players_with_most_victory_points.append(player)
        # If there was a tie, the winner is the player with the fewest turns played
        fewest_turns_played = min(player.turns_played for player in players_with_most_victory_points)
        winners = [player.name for player in players_with_most_victory_points if player.turns_played == fewest_turns_played]
        return victory_points_dict, turns_played_dict, winners

    @property
    def num_players(self) -> int:
        '''
        The number of players in the game.
        '''
        return len(self.player_names)


if __name__ == '__main__':
    game = Game()
    game.add_player()
    game.add_player()
    game.add_player()
    game.add_player()
    game.start(debug=True)
