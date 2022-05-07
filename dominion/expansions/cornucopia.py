from .expansion import Expansion
from ..cards import cornucopia_cards
from ..grammar import s, it_or_them

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
            
    def order_treasures(self, player, treasures):
        # If any Horns of Plenty are in the played treasures, allow the player to play them last
        if any(isinstance(treasure, cornucopia_cards.HornOfPlenty) for treasure in treasures):
            # Find all played Horns of Plenty
            horns_of_plenty = [treasure for treasure in treasures if isinstance(treasure, cornucopia_cards.HornOfPlenty)]
            # Ask the player if they want to play them last
            prompt = f"You played {s(len(horns_of_plenty), cornucopia_cards.HornOfPlenty)}. Would you like to play {it_or_them(len(horns_of_plenty))} last to maximize the number of differently named cards played this turn?"
            if player.interactions.choose_yes_or_no(prompt):
                # Remove the Horns of Plenty from the list of played treasures
                treasures = [treasure for treasure in treasures if not isinstance(treasure, cornucopia_cards.HornOfPlenty)]
                # Add the Horns of Plenty to the end of the list of played treasures
                treasures.extend(horns_of_plenty)
        return treasures


    @property
    def game_end_conditions(self):
        return []

    def scoring(self, player):
        return 0