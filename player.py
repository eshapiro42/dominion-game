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

    def choose_card_from_hand(self, force):
        hand = self.player_mat.hand
        if not hand:
            return None
        while True:
            try:
                self.player_mat.print_hand()
                if force:
                    card_num = int(input(f'Enter choice 1-{len(hand)}: '))
                    card_chosen = hand[card_num - 1]
                else:
                    card_num = int(input(f'Enter choice 1-{len(hand)} (0 to skip): '))
                    if card_num == 0:
                        return None
                    else:
                        card_chosen = hand[card_num - 1]
                return card_chosen
            except:
                print('That is not a valid choice.\n')

    def choose_card_from_discard_pile(self, force):
        discard_pile = self.player_mat.discard_pile
        if not discard_pile:
            return None
        while True:
            try:
                self.player_mat.print_discard_pile()
                if force:
                    card_num = int(input(f'Enter choice 1-{len(discard_pile)}: '))
                    card_chosen = discard_pile[card_num - 1]
                else:
                    card_num = int(input(f'Enter choice 1-{len(discard_pile)} (0 to skip): '))
                    if card_num == 0:
                        return None
                    else:
                        card_chosen = discard_pile[card_num - 1]
                return card_chosen
            except:
                print('That is not a valid choice.\n')


    @property
    def current_victory_points(self):
        return self.player_mat.current_victory_points
