import itertools
from player import Player
from supply import Supply
from turn import Turn


class Game:
    def __init__(self):
        self.players = []

    def add_player(self, name=None):
        if name is None:
            name = f'Player {self.num_players}'
        player = Player(game=self, name=name)
        self.players.append(player)

    def start(self):
        self.supply = Supply(num_players=self.num_players)
        print(self.supply)
        for player in self.players:
            player.start()
        self.game_loop()

    def game_loop(self):
        for player in itertools.cycle(self.players):
            turn = Turn(player)

    @property
    def num_players(self):
        return len(self.players)