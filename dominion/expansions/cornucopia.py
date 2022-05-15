from __future__ import annotations

import random

from typing import TYPE_CHECKING, Type

from .expansion import Expansion
from ..cards import cards, cornucopia_cards
from ..grammar import s, it_or_them
from ..supply import FiniteSupplyStack

if TYPE_CHECKING:
    from ..cards.cards import Card

class CornucopiaExpansion(Expansion):
    name = 'Cornucopia'

    def __init__(self, game, bane_card_class: Type[Card] | None = None):
        super().__init__(game)
        self.bane_card_class = bane_card_class
        self.prizes = [prize() for prize in cornucopia_cards.PRIZES]

    @property
    def basic_card_piles(self):
        return []

    @property
    def kingdom_card_classes(self):
        return cornucopia_cards.KINGDOM_CARDS

    def add_additional_kingdom_cards(self):
        # If the Young Witch is in the Supply, it adds an extra Kingdom card pile costing 2 $ or 3 $ to the Supply. Cards from that pile are Bane cards.
        if cornucopia_cards.YoungWitch in self.supply.card_stacks:
            # If a Bane card is specified (e.g. by a recommended set), use that one
            if self.bane_card_class:
                bane_card_class = self.bane_card_class
            # Otherwise, randomly choose a card class costing 2 $ or 3 $ to be the Bane card
            else:
                possible_bane_card_classes = [card_class for card_class in self.supply.possible_kingdom_card_classes if card_class not in self.supply.card_stacks and card_class.cost in [2, 3]]
                bane_card_class = random.choice(possible_bane_card_classes)
            self.game.broadcast(f"The Young Witch is in play this game. {s(10, bane_card_class.name, print_number=False)} are Bane cards.")
            # Add the Bane card class to the Supply and modify its example card
            self.supply.card_stacks[bane_card_class] = FiniteSupplyStack(bane_card_class, 10)
            self.supply.card_stacks[bane_card_class].example.types += [cards.CardType.BANE]
        # If the Tournament is in the Supply, it adds Prizes
        if cornucopia_cards.Tournament in self.supply.card_stacks:
            self.game.broadcast("The Tournament is in play this game. Prizes are available.")

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