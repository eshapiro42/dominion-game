import cards
import itertools
import interactions
import random
import time
from player import Player
from supply import Supply
from turn import Turn


class GameStartedError(Exception):
    '''Raised when the game has already started'''
    def __init__(self):
        message = f'The game has already started'
        super().__init__(message)


class Game:
    class GameEndConditions:
        NO_MORE_PROVINCES = 1
        THREE_SUPPLY_PILES_EMPTY = 2

    def __init__(self, interactions_class=interactions.CLIInteraction, broadcast_class=interactions.CLIBroadcast, socketio=None, room=None):
        # Interaction objects need to be instantiated later, one for each player
        self.interactions_class = interactions_class
        # Broadcast object needs to be instantiated later, just once for the whole game
        self.broadcast_class = broadcast_class
        self.socketio = socketio
        self.room = room
        self.player_names = []
        self.player_sids = []
        self.players = []
        self.startable = False
        self.started = False

    def add_player(self, name=None, sid=None):
        # Players can only be added before the game starts
        if self.started:
            raise GameStartedError()
        if name is None:
            name = f'Player {self.num_players + 1}'
        self.player_names.append(name)
        self.player_sids.append(sid)
        # If there are two players, the game is joinable
        if len(self.player_names) == 2:
            self.startable = True

    def start(self):
        self.started = True
        # Create the supply
        self.supply = Supply(num_players=self.num_players)
        self.supply.setup()
        self.broadcast = self.broadcast_class(game=self, socketio=self.socketio, room=self.room)
        # Create each player object
        for player_name, player_sid in zip(self.player_names, self.player_sids):
            player = Player(game=self, name=player_name, interactions_class=self.interactions_class, socketio=self.socketio, sid=player_sid)
            self.players.append(player)
            player.interactions.start()
        # Print out the supply
        self.broadcast(str(self.supply))
        if self.socketio is not None:
            time.sleep(0.5)
        # Start the game loop!
        self.game_loop()

    def game_loop(self):
        self.turn_order = random.sample(self.players, len(self.players))
        for player in itertools.cycle(self.turn_order):
            turn = Turn(player)
            # Check if the game ended after each turn
            ended = self.ended
            if ended:
                # Game is over. Print out info.
                if ended == self.GameEndConditions.NO_MORE_PROVINCES:
                    self.broadcast('All provinces have been bought.')
                elif ended == self.GameEndConditions.THREE_SUPPLY_PILES_EMPTY:
                    empty_piles = [stack for stack in self.supply.card_stacks.values() if stack.is_empty]
                    self.broadcast(f"Three supply piles are empty: {', '.join(map(str, empty_piles))}")
                self.broadcast('Game over!')
                victory_points_dict, winners = self.scores
                self.broadcast(f'\tScores: {victory_points_dict}')
                self.broadcast(f'\tWinners: {winners}.')
                for player in self.players:
                    self.broadcast(f"{player}'s cards: {list(player.all_cards)}")
                break

    @property
    def ended(self):
        # Check if all provinces are gone
        if self.supply.card_stacks[cards.Province].is_empty:
            return self.GameEndConditions.NO_MORE_PROVINCES
        # Check if three supply stacks are gone
        elif self.supply.num_empty_stacks >= 3:
            return self.GameEndConditions.THREE_SUPPLY_PILES_EMPTY
        # Otherwise, the game is not over
        else:
            return False

    @property
    def scores(self):
        # Count up victory points for each player
        victory_points_dict = {player.name: player.current_victory_points for player in self.players}
        # Figure out the most victory points attained
        most_victory_points = max(victory_points_dict.values())
        # Figure out which players got that many victory points
        winners = []
        for player_name, victory_points in victory_points_dict.items():
            if victory_points == most_victory_points:
                winners.append(player_name)
        return victory_points_dict, winners

    @property
    def num_players(self):
        return len(self.player_names)


if __name__ == '__main__':
    # game = Game()
    game = Game(interactions_class=interactions.AutoInteraction, broadcast_class=interactions.AutoBroadcast)
    game.add_player()
    game.add_player()
    game.start()
