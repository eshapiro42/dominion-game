import itertools
import random
import time
from prettytable import PrettyTable
from .cards import base_cards
from .expansions import BaseExpansion, ProsperityExpansion
from .interactions import interactions
from .player import Player
from .supply import Supply
from .turn import Turn


class GameStartedError(Exception):
    '''Raised when the game has already started'''
    def __init__(self):
        message = f'The game has already started'
        super().__init__(message)


class Game:
    def __init__(self, socketio=None, room=None):
        self.socketio = socketio
        self.room = room
        self.player_names = []
        self.player_sids = []
        self.player_interactions_classes = []
        self.players = []
        self.startable = False
        self.started = False
        self.game_end_conditions = []
        self.expansions = set()
        self.add_expansion(BaseExpansion)
        # TODO: Remove this and allow customization
        self.add_expansion(ProsperityExpansion)

    def add_expansion(self, expansion):
        self.expansions.add(expansion)

    def add_player(self, name=None, sid=None, interactions_class=interactions.CLIInteraction):
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
        # Start the game loop!
        if not debug:
            self.game_loop()

    def game_loop(self):
        for player in itertools.cycle(self.turn_order):
            turn = Turn(player)
            # Check if the game ended after each turn
            ended, explanation = self.ended
            if ended:
                # Game is over. Print out info.
                self.broadcast(explanation)
                self.broadcast('Game over!')
                victory_points_dict, turns_played_dict, winners = self.scores
                self.broadcast(f'\tScores: {victory_points_dict}')
                self.broadcast(f'\tTurns played: {turns_played_dict}')
                self.broadcast(f'\tWinners: {winners}.')
                for player in self.players:
                    self.broadcast(f"{player}'s cards: {list(player.all_cards)}")
                break

    def broadcast(self, message):
        for player in self.players:
            player.interactions.send(message)

    @property
    def ended(self):
        # Check if any game end condition has been met
        for game_end_condition in self.game_end_conditions:
            game_ended, explanation = game_end_condition()
            if game_ended:
                return True, explanation
        else:
            return False, None

    @property
    def scores(self):
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
        return len(self.player_names)


if __name__ == '__main__':
    game = Game()
    game.add_player()
    game.add_player()
    game.add_player()
    game.add_player()
    game.start(debug=True)
