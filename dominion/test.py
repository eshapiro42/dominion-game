import os
import sys
import time
import traceback
from contextlib import redirect_stdout, redirect_stderr
from multiprocessing import Process
from .cards import cards
from .game import Game
from .interactions import AutoInteraction


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


def with_timeout(timeout):
    def inner_decorator(func):
        def wrapper(*args, **kwargs):
            proc = Process(target=func, args=args, kwargs=kwargs)
            proc.start()
            proc.join(timeout=timeout)
            proc.terminate()
        return wrapper
    return inner_decorator
    

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

@with_timeout(60)
def test_stability(logdir, num_players):
    timestamp = time.time()
    stdoutfile = os.path.join(logdir, f'test_stability_{timestamp}_stdout.txt')
    stderrfile = os.path.join(logdir, f'test_stability_{timestamp}_stderr.txt')
    with open(stdoutfile, 'w') as of, open(stderrfile, 'w') as ef:
        with redirect_stdout(of), redirect_stderr(ef):
            try:
                game = Game()
                for _ in range(num_players):
                    game.add_player(interactions_class=AutoInteraction)
                game.start()
            except Exception as e:
                ef.write(str(e))
                ef.write(traceback.format_exc())
    # If there were no errors, discard the log files
    if os.stat(stderrfile).st_size == 0:
        os.remove(stdoutfile)
        os.remove(stderrfile)


if __name__ == '__main__':
    logdir = create_logdir()
    test_instantiate_cards(logdir)
    counter = 0
    while True:
        for num_players in range(2, 5):
            counter += 1
            print(f'Stability test {counter}')
            test_stability(logdir, num_players)

