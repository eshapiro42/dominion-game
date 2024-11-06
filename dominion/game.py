from __future__ import annotations

import itertools
import random

from collections import defaultdict, Counter
from typing import TYPE_CHECKING, Any, Callable, Optional, Dict, List, Tuple, Type

from .cards.cards import Card, CardType, CardJSON
from .expansions import BaseExpansion, DominionExpansion, ProsperityExpansion, IntrigueExpansion, CornucopiaExpansion, HinterlandsExpansion, GuildsExpansion
from .game_log import GameLog
from .grammar import s
from .interactions import AutoInteraction, BrowserInteraction
from .player import Player
from .supply import Supply
from .turn import Turn

if TYPE_CHECKING:
    from flask_socketio import SocketIO
    from .expansions.expansion import Expansion
    from .hooks import TreasureHook, PreBuyHook, PreTurnHook, PostDiscardHook, PostBuyHook
    from .interactions.interaction import Interaction
    from .cards.custom_sets import CustomSet
    from .cards.recommended_sets import RecommendedSet


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
        self._socketio: SocketIO = socketio
        self._test: bool = test # If not running tests, slows down CPU interactions to simulate thought
        self._room: str = room
        self._future_human_players: List[Dict[str, Any]] = []
        self._future_cpus: int = 0
        self._players: List[Player] = []
        self._startable: bool = False
        self._started: bool = False
        self._kill_scheduled: bool = False
        self._killed: bool = False
        self._current_turn: Turn | None = None
        self._treasure_hooks = defaultdict(list)
        self._pre_buy_hooks = defaultdict(list)
        self._pre_turn_hooks: List[PreTurnHook] = []
        self._post_discard_hooks = defaultdict(list)
        self._post_buy_hooks = defaultdict(list)
        self._game_end_conditions = []
        self._game_log: GameLog = GameLog(self)
        self._recommended_set = None
        self._custom_set = None
        self._expansions = set()
        self._allow_simultaneous_reactions = False
        self._distribute_cost = False
        self._disable_attack_cards = False
        self._require_plus_two_action = False
        self._require_drawer = False
        self._require_buy = False
        self._require_trashing = False
        self._ended = False

        self.add_expansion(BaseExpansion) # This must always be here or the game will not work
        # self.add_expansion(DominionExpansion)
        # self.add_expansion(IntrigueExpansion)
        # self.add_expansion(ProsperityExpansion)
        # self.add_expansion(CornucopiaExpansion)
        # self.add_expansion(HinterlandsExpansion)
        # self.add_expansion(GuildsExpansion)

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
    def game_log(self) -> GameLog:
        '''
        The game log for this game.
        '''
        return self._game_log

    @property
    def future_players(self) -> List[Dict[str, Any]]:
        '''
        A combined list of human and CPU players that are
        planned for inclusion in the game.
        '''
        cpu_players = [
            {
                "name": f"CPU {str(num + 1)}",
                "sid": None,
                "interactions_class": AutoInteraction,
            }
            for num in range(0, self._future_cpus)
        ]
        return self._future_human_players + cpu_players

    @property
    def future_player_names(self) -> List[str]:
        '''
        A list of names of all human and CPU players that
        are planned for inclusion in the game.
        '''
        return [player["name"] for player in self.future_players]

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
    def pre_turn_hooks(self) -> List[PreTurnHook]:
        '''
        A list of game-wide :obj:`PreTurnHook` instances.
        '''
        return self._pre_turn_hooks

    @pre_turn_hooks.setter
    def pre_turn_hooks(self, pre_turn_hooks: List[PreTurnHook]):
        self._pre_turn_hooks = pre_turn_hooks

    @property
    def post_discard_hooks(self) -> Dict[Type[Card], List[PostDiscardHook]]:
        '''
        A dictionary of game-wide :obj:`PostDiscardHook` instances, indexed by Card class.

        The values are lists of post-discard hooks, since multiple post-discard hooks can be registered to a single card.
        '''
        return self._post_discard_hooks

    @post_discard_hooks.setter
    def post_discard_hooks(self, post_discard_hooks: Dict[Type[Card], List[PostDiscardHook]]):
        self._post_discard_hooks = post_discard_hooks

    @property
    def post_buy_hooks(self) -> Dict[Type[Card], List[PostBuyHook]]:
        '''
        A dictionary of game-wide :obj:`PostBuyHook` instances, indexed by Card class.

        The values are lists of post-buy hooks, since multiple post-buy hooks can be registered to a single card.
        '''
        return self._post_buy_hooks

    @post_buy_hooks.setter
    def post_buy_hooks(self, post_buy_hooks: Dict[Type[Card], List[PostBuyHook]]):
        self._post_buy_hooks = post_buy_hooks

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
    def recommended_set(self) -> Type[RecommendedSet] | None:
        """
        A recommended set to use for the supply.

        If this is not None, no other supply customizations or expansions
        outside the recommended set will be considered for inclusion.
        """
        return self._recommended_set

    @recommended_set.setter
    def recommended_set(self, recommended_set: Type[RecommendedSet] | None):
        self.expansions = set()
        expansion: Type[Expansion]
        for expansion in recommended_set.expansions:
            self.add_expansion(expansion)
        self._recommended_set = recommended_set

    @property
    def custom_set(self) -> Type[CustomSet] | None:
        """
        A custom set to use for the supply.

        If this is not None, no other supply customizations or expansions
        outside the custom set will be considered for inclusion.
        """
        return self._custom_set

    @custom_set.setter
    def custom_set(self, custom_set: Type[CustomSet] | None):
        self.expansions = set()
        expansion: Type[Expansion]
        for expansion in custom_set.expansions:
            self.add_expansion(expansion)
        self._custom_set = custom_set

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

    def add_pre_turn_hook(self, pre_turn_hook: PreTurnHook):
        '''
        Add a game-wide pre-turn hook.
        '''
        self.pre_turn_hooks.append(pre_turn_hook)

    def add_post_discard_hook(self, post_discard_hook: PostDiscardHook, card_class: Type[Card]):
        '''
        Add a game-wide post-discard hook to a specific card class.

        Args:
            post_discard_hook: The post-discard hook to add.
            card_class: The card class which should activate the post-discard hook.
        '''
        self.post_discard_hooks[card_class].append(post_discard_hook)

    def add_post_buy_hook(self, post_buy_hook: PostBuyHook, card_class: Type[Card]):
        '''
        Add a game-wide post-buy hook to a specific card class.

        Args:
            post_buy_hook: The post-buy hook to add.
            card_class: The card class which should activate the post-buy hook upon being bought.
        '''
        self.post_buy_hooks[card_class].append(post_buy_hook)

    def add_expansion(self, expansion: Type[Expansion]):
        '''
        Add an expansion into the game.

        Args:
            expansion: The expansion class to add into the game.
        '''
        if self.recommended_set is not None:
            pass
        self.expansions.add(expansion)

    def add_player(self, name: str, sid: str):
        '''
        Add a new player into the game.
        
        Will fail if the game has already started.

        Will set :obj:`Game.startable` to :obj:`True` when the second player is added.

        Args:
            name: The player's name.
            sid: The player's Socket.IO SID. Required for networked play.
        '''
        # Players can only be added before the game starts
        if self.started:
            raise GameStartedError()
        self._future_human_players.append(
            {
                "name": name,
                "sid": sid,
                "interactions_class": BrowserInteraction,
            }
        )
        # If there are two players, the game is startable
        if self.num_players >= 2:
            self.startable = True

    def add_cpu(self):
        '''
        Add a new CPU player into the game.
        
        Will fail if the game has already started.

        Will set :obj:`Game.startable` to :obj:`True` when the second player is added.
        '''
        # Players can only be added before the game starts
        if self.started:
            raise GameStartedError()
        self._future_cpus += 1
        # If there are two players, the game is startable
        if self.num_players >= 2:
            self.startable = True

    def remove_player(self, name: str) -> bool:
        '''
        Remove a player from the game.
        
        Will fail if the game has already started.

        Will set :obj:`Game.startable` to :obj:`False` if only one player is left afterward.

        Args:
            name: The player's name.
        '''
        # Players can only be removed before the game starts
        if self.started:
            raise GameStartedError()
        try:
            if "CPU" in name:
                self._future_cpus -= 1
            else:
                player_to_remove = [player for player in self._future_human_players if player["name"] == name][0]
                self._future_human_players.remove(player_to_remove)
        except Exception as exception:
            print(exception)
        # If there are fewer than two players, the game is not startable
        if self.num_players < 2:
            self.startable = False

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
        self.supply = Supply(num_players=len(self.future_players)) # Can't use self.num_players because the Player objects don't exist yet
        # Create each player object
        for future_player in self.future_players:
            player = Player(game=self, name=future_player["name"], interactions_class=future_player["interactions_class"], socketio=self.socketio, sid=future_player["sid"])
            self.players.append(player)
            player.interactions.start()
        # Initiate start-of-game logging
        if debug:
            game_start_log_entry = self.game_log.add_entry("The game has started in debug mode.")
        else:
            game_start_log_entry = self.game_log.add_entry("The game has started.")
        # Add in the selected recommended set, if any
        if self.recommended_set is not None:
            self.game_log.add_entry(f'Using "{self.recommended_set.name}" Recommended Kingdom.', parent=game_start_log_entry)
            self.broadcast(f'Using "{self.recommended_set.name}" Recommended Kingdom.')
            self.supply.customization.recommended_set = self.recommended_set(self)
            for expansion_instance in self.supply.customization.recommended_set.expansion_instances:
                self.supply.customization.expansions.add(expansion_instance)
                self.game_end_conditions += expansion_instance.game_end_conditions
        # Add in the custom set, if any
        elif self.custom_set is not None:
            game_creator_name = self.players[0].name
            self.game_log.add_entry(f"Using {game_creator_name}'s Custom Kingdom.", parent=game_start_log_entry)
            self.broadcast(f"Using {game_creator_name}'s Custom Kingdom.")
            self.supply.customization.custom_set = self.custom_set(self)
            for expansion_instance in self.supply.customization.custom_set.expansion_instances:
                self.supply.customization.expansions.add(expansion_instance)
                self.game_end_conditions += expansion_instance.game_end_conditions
            print(self.supply.customization.custom_set.expansion_instances)
        # Otherwise, the supply will need to be randomly generated based on the selected expansions and customizations
        else:
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
                self.game_log.add_entry(f"Using {expansions_string} expansions.", parent=game_start_log_entry)
                self.broadcast(f"Using {expansions_string} expansions.")
            elif len(expansion_names) == 1:
                expansion_name = expansion_names[0]
                self.game_log.add_entry(f"Using {expansion_name} expansion.", parent=game_start_log_entry)
                self.broadcast(f"Using {expansion_name} expansion.")
            # Add in other supply customizations
            self.supply.customization.distribute_cost = self.distribute_cost
            self.supply.customization.disable_attack_cards = self.disable_attack_cards
            self.supply.customization.require_plus_two_action = self.require_plus_two_action
            self.supply.customization.require_drawer = self.require_drawer
            self.supply.customization.require_buy = self.require_buy
            self.supply.customization.require_trashing = self.require_trashing
        # Notify players if simultaneous reactions are allowed
        if self.allow_simultaneous_reactions:
            self.game_log.add_entry("Simultaneous reactions are allowed.", parent=game_start_log_entry)
            self.broadcast("Simultaneous reactions are allowed.")
        # Set up the supply
        self.supply.setup()
        # Randomly decide turn order
        self.turn_order = random.sample(self.players, len(self.players))
        # Each player figures out the turn order of the other players
        for player in self.players:
            player.get_other_players()
        # Start the game loop!
        if not debug:
            self.game_loop()

    def end(self, explanation: str):
        print(self.scores)
        # Game is over. Print out info.
        game_over_log_entry = self.game_log.add_entry("Game over!")
        self.game_log.add_entry(explanation, parent=game_over_log_entry)
        self.broadcast('Game over!')
        self.broadcast(explanation)
        victory_points_dict, turns_played_dict, winners = self.scores
        winners_str = ', '.join(map(str, winners))
        winners_str = f'{s(len(winners), "Winner").split(" ")[-1]}: {winners_str}.'
        self.game_log.add_entry(winners_str, parent=game_over_log_entry)
        self.broadcast(winners_str)
        end_game_data = {
            "explanation": explanation,
            "winners": winners_str,
            "playerData": [],
            "showVictoryTokens": ProsperityExpansion in self.expansions and any(player.victory_tokens > 0 for player in self.players),
        }
        for player in self.players:
            card_class_counter: Counter[Type[Card]] = Counter([type(card) for card in player.all_cards])
            player_cards_json: List[CardJSON] = []
            for card_class, quantity in card_class_counter.items():
                card_example = next(card for card in player.all_cards if isinstance(card, card_class))
                card_json = card_example.json
                card_json["quantity"] = quantity
                player_cards_json.append(card_json)
            end_game_data["playerData"].append(
                {
                    "name": player.name,
                    "score": victory_points_dict[player],
                    "turns": turns_played_dict[player],
                    "cards": player_cards_json,
                    "victoryTokens": player.victory_tokens if end_game_data["showVictoryTokens"] else None,
                }
            )
        print(end_game_data)
        if self.socketio is not None:
            self.socketio.emit(
                'game over',
                {'endGameData': end_game_data},
                room=self.room,
            )

    def game_loop(self):
        '''
        The main game loop. Cycles through turns for each player and checks for
        game end conditions after each turn.
        '''
        for player in itertools.cycle(self.turn_order):
            self.current_turn = Turn(player)
            self.current_turn.start()
            # Check if the game ended after each turn
            ended, explanation = self.end_condition_met
            if ended:
                self.end(explanation)
                self.ended = True
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
    def end_condition_met(self) -> Tuple[bool, Optional[str]]:
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
    def ended(self) -> bool:
        '''
        Whether the game has ended.
        '''
        return self._ended
    
    @ended.setter
    def ended(self, ended: bool):
        self._ended = ended

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
        players_with_most_victory_points: List[Player] = []
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
        if not self.started:
            return len(self.future_players)
        return len(self.players)
