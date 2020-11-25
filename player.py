from playermat import PlayerMat

class Player:
    def __init__(self, game, name):
        self.game = game
        self.name = name

    def start(self):
        self.player_mat = PlayerMat(player=self)
 
    def __repr__(self):
        return f'Player({self.name})'

    def __str__(self):
        return self.name

    @property
    def current_victory_points(self):
        return self.player_mat.current_victory_points
