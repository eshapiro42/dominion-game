from playermat import PlayerMat

class Player:
    def __init__(self, game, name):
        self.game = game
        self.name = name

    def start(self):
        self.player_mat = PlayerMat(player=self)

    def __repr__(self):
        return self.name
