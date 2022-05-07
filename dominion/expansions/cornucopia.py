from .expansion import Expansion
from ..cards import cornucopia_cards

class CornucopiaExpansion(Expansion):
    name = 'Cornucopia'

    def __init__(self, game):
        super().__init__(game)
        self.prizes = [prize() for prize in cornucopia_cards.PRIZES]
        print(self.prizes)

    @property
    def basic_card_piles(self):
        return []

    @property
    def kingdom_card_classes(self):
        return cornucopia_cards.KINGDOM_CARDS

    def additional_setup(self):
        pass

    def heartbeat(self):
        # Display prizes
        if cornucopia_cards.Tournament in self.game.supply.card_stacks:
            self.game.socketio.emit(
                "prizes",
                {
                    "cards": [card.json for card in self.prizes]
                },
                room=self.game.room,
            )
            
    @property
    def game_end_conditions(self):
        return []

    def scoring(self, player):
        return 0