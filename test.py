import cards
import os
import sys
import time
import traceback
from contextlib import redirect_stdout, redirect_stderr
from game import Game
from interactions import AutoBroadcast, AutoInteraction


####################
# HELPER FUNCTIONS #
####################


def create_logdir():
    timestamp = time.time()
    logdir = f'test_logs/test_run_{timestamp}/'
    try:
        os.makedirs(logdir)
    except OSError:
        pass
    return logdir
    

##############
# TEST CASES #
##############


def test_instantiate_cards(logdir):
    timestamp = time.time()
    stdoutfile = os.path.join(logdir, f'test_instantiate_cards_{timestamp}_stdout.txt')
    stderrfile = os.path.join(logdir, f'test_instantiate_cards_{timestamp}_stderr.txt')
    with open(stdoutfile, 'w') as of, open(stderrfile, 'w') as ef:
        with redirect_stdout(of), redirect_stderr(ef):
            for card_class in cards.BASIC_CARDS:
                card = card_class()
            for card_class in cards.KINGDOM_CARDS:
                card = card_class()


def test_stability(logdir, num_players):
    timestamp = time.time()
    stdoutfile = os.path.join(logdir, f'test_stability_{timestamp}_stdout.txt')
    stderrfile = os.path.join(logdir, f'test_stability_{timestamp}_stderr.txt')
    with open(stdoutfile, 'w') as of, open(stderrfile, 'w') as ef:
        with redirect_stdout(of), redirect_stderr(ef):
            try:
                game = Game(interactions_class=AutoInteraction, broadcast_class=AutoBroadcast)
                for _ in range(num_players):
                    game.add_player()
                game.start()
            except Exception as e:
                ef.write(str(e))
                ef.write(traceback.format_exc())


if __name__ == '__main__':
    logdir = create_logdir()
    test_instantiate_cards(logdir)
    while True:
        for num_players in range(2, 5):
            test_stability(logdir, num_players)

