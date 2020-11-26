import itertools
import random
import cards
from player import Player
from supply import Supply
from turn import Turn


class GameStartedError(Exception):
    '''Raised when the game has already started'''
    def __init__(self):
        message = f'The game has already started'
        super().__init__(message)


class Game:
    def __init__(self):
        self.player_names = []
        self.players = []
        self.started = False

    def add_player(self, name=None):
        # Players can only be added before the game starts
        if self.started:
            raise GameStartedError()
        if name is None:
            name = f'Player {self.num_players}'
        self.player_names.append(name)

    def start(self):
        self.started = True
        # Create the supply
        self.supply = Supply(num_players=self.num_players)
        print(self.supply)
        # Create each player object
        for player_name in self.player_names:
            player = Player(game=self, name=player_name)
            self.players.append(player)
            player.interactions.start()
        # Start the game loop!
        self.game_loop()

    def game_loop(self):
        self.turn_order = random.sample(self.players, len(self.players))
        for player in itertools.cycle(self.turn_order):
            turn = Turn(player)
            # Check if the game ended after each turn
            if self.ended:
                victory_points_dict, winners = self.scores
                print('Game over!')
                print(f'\tScores: {victory_points_dict}')
                print(f'\tWinners: {winners}.')
                break

    @property
    def ended(self):
        # Check if all provinces are gone
        if self.supply.card_stacks[cards.Province].is_empty:
            return True
        # Check if three supply stacks are gone
        elif self.supply.num_empty_stacks >= 3:
            return True
        # Otherwise, the game is not over
        else:
            return False

    @property
    def scores(self):
        # Count up victory points for each player
        victory_points_dict = {player: player.current_victory_points for player in self.players}
        # Figure out the most victory points attained
        most_victory_points = max(victory_points_dict.values())
        # Figure out which players got that many victory points
        winners = []
        for player, victory_points in victory_points_dict.items():
            if victory_points == most_victory_points:
                winners.append(player)
        return victory_points_dict, winners
        # # Print out winners
        # if len(winners) == 1:
        #     winner_string = winners[0]
        #     print(f'The winner is {winner_string}!')
        # else:
        #     winners_string = f"{', '.join(map(str, winners[:-1]))} and {winners[-1]}"
        #     print(f"It's a tie! The winners are {winners_string}!")

    @property
    def num_players(self):
        return len(self.players)


if __name__ == '__main__':
    game = Game()
    game.add_player('Eric')
    game.add_player('Brendon')
    game.start()
