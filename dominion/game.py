import itertools
import random

from collections import defaultdict

from .cards.cards import Card, CardType
from .expansions import BaseExpansion, ProsperityExpansion, IntrigueExpansion
from .grammar import s
from .interactions import CLIInteraction
from .player import Player
from .supply import Supply
from .turn import Turn


class GameStartedError(Exception):
    '''Raised when the game has already started'''
    def __init__(self):
        message = f'The game has already started'
        super().__init__(message)


class Game:
    '''Dominion Game object.

    All components of the game are instantiated by this class.
    The game loop is also run from here.

    Args:
        socketio (:obj:`socketio.Server`, optional): A Socket.IO server instance.
        room (:obj:`str`, optional): The room ID for this game.

    Parameters:
        player_names (:obj:`list` of :obj:`str`): A list of the names of players in the game.
        player_sids (:obj:`list` of :obj:`str`): A list of SIDs corresponding to each player in the game (these lists share an index).
        player_interaction_classes (:obj:`list` of :obj:`.interactions.Interaction`): A list of interaction classes corresponding to each player in the game (these lists share an index).
        players (:obj:`list` of :obj:`.player.Player`): A list of Player objects.
        startable (:obj:`bool`): Whether the game can be started. This changes to True automatically when two players have joined.
        started (:obj:`bool`): Whether the game has been started. This changes to True automatically when the game starts.
        current_turn (:obj:`.turn.Turn`): The Turn object corresponding to the current turn of the game.
        treasure_hooks (:obj:`dict` with keys :obj:`type(cards.Card)` and values :obj:`list` of :obj:`.hooks.TreasureHook`): A dictionary of game-wide TreasureHook instances, indexed by card_class.
        pre_buy_hooks (:obj:`dict` with keys :obj:`type(cards.Card)` and values :obj:`list` of :obj:`.hooks.PreBuyHook`): A dictionary of game-wide PreBuyHook instances, indexed by card_class.
        game_end_conditions (:obj:`list` of :obj:`func`): A list of functions to run which each determine a specific game-end criterion.
        expansions (:obj:`set` of :obj:`.expansion.Expansion`): A set of Expansion classes. This must always include :obj:`.expansion.BaseExpansion` for the game to work. 
        supply (:obj:`.supply.Supply`): The Supply for this game.
    '''
    def __init__(self, socketio=None, room=None, test=False):
        self.socketio = socketio
        self.test = test # If not running tests, slows down CPU interactions to simulate thought
        self.room = room
        self.player_names = []
        self.player_sids = []
        self.player_interactions_classes = []
        self.players = []
        self.startable = False
        self.started = False
        self.kill_scheduled = False
        self.killed = False
        self.current_turn = None
        self.treasure_hooks = defaultdict(list)
        self.pre_buy_hooks = defaultdict(list)
        self.game_end_conditions = []
        self.expansions = set()
        self.allow_simultaneous_reactions = False # If toggled, allows attacked players to react to attacks simultaneously (when sensible)
        self.distribute_cost = False # If toggled, ensures there are at least two cards each of cost {2, 3, 4, 5}
        self.disable_attack_cards = False # If toggled, Attack cards are not allowed
        self.require_plus_two_action = False # If toggled, ensures there is at least one card with '+2 Actions'
        self.require_drawer = False # If toggled, ensures there is at least one card with '>= +1 Cards'
        self.require_buy = False # If toggled, ensures there is at least one card with '>= +1 Buys'
        self.require_trashing = False # If toggled, ensures there is at least one card that mentions trashing

        self.add_expansion(BaseExpansion) # This must always be here or the game will not work
        # self.add_expansion(IntrigueExpansion)
        # self.add_expansion(ProsperityExpansion)

    def add_treasure_hook(self, treasure_hook, card_class):
        '''
        Add a Game-wide Treasure Hook to a specific card_class.

        Args:
            treasure_hook (:obj:`.hooks.TreasureHook`): The Treasure Hook to add.
            card_class (:obj:`type(cards.Card)`): The card_class which should activate the Treasure Hook.
        '''
        self.treasure_hooks[card_class].append(treasure_hook)

    def add_pre_buy_hook(self, pre_buy_hook, card_class):
        '''
        Add a Game-wide Pre Buy Hook to a specific card_class.

        Args:
            treasure_hook (:obj:`.hooks.PreBuyHook`): The Pre Buy Hook to add.
            card_class (:obj:`type(cards.Card)`): The card_class which should activate the Treasure Hook.
        '''
        self.pre_buy_hooks[card_class].append(pre_buy_hook)

    def add_expansion(self, expansion):
        '''
        Add an expansion into the game.

        Args:
            expansion (:obj:`type(expansion.Expansion)`): The Expansion class to add into the game.
        '''
        self.expansions.add(expansion)

    def add_player(self, name=None, sid=None, interactions_class=CLIInteraction):
        '''
        Add a new player into the game.
        
        Will fail if the game has already started.

        Will set :obj:`Game.startable` to :obj:`True` when the second player is added.

        Args:
            name (:obj:`str`, optional): The player's name.
            sid (:obj:`str`, optional): The player's socketio SID. Required for networked play.
            interactions_class (:obj:`type(interactions.Interaction)`): The player's Interaction class.
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

    def start(self, debug=False):
        '''
        Start the game.

        This method creates and sets up the supply, player objects, adds in desired expansions,
        decides turn order and runs the game loop.

        Args:
            debug (:obj:`bool`): Defaults to :obj:`False`. If :obj:`True`, does not run the game loop.
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

    def broadcast(self, message):
        '''
        Broadcast a message to each player in the game.

        Args:
            message (:obj:`str`): The message to broadcast to each player.
        '''
        for player in self.players:
            player.interactions.send(message)
        
    @property
    def ended(self):
        '''
        Check whether the game has ended.
        
        Returns:
            game_ended (:obj:`bool`): :obj:`True` if the game has ended, :obj:`False` otherwise.
            explanation (:obj:`str`): An explanation for why the game has ended, or :obj:`None` if the game has not ended.
        '''
        # Check if any game end condition has been met
        for game_end_condition in self.game_end_conditions:
            game_ended, explanation = game_end_condition()
            if game_ended:
                return True, explanation
        else:
            return False, None

    @property
    def scores(self):
        '''
        The scores of each player.

        Returns:
            victory_points_dict (:obj:`dict` with keys :obj:`.player.Player` and values :obj:`int`): A dictionary of scores indexed by Player.
            turns_played_dict (:obj:`dict` with keys :obj:`.player.Player` and values :obj:`int`): A dictionary of turns played indexed by Player.
            winners (:obj:`list` of :obj:`str`): A list of Player's names who won the game.
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
    def num_players(self):
        '''The number of players in the game.
        
        Returns:
            num_players (:obj:`int`): The number of players in the game.
        '''
        return len(self.player_names)


if __name__ == '__main__':
    game = Game()
    game.add_player()
    game.add_player()
    game.add_player()
    game.add_player()
    game.start(debug=True)
