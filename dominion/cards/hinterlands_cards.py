

import math

from gevent import Greenlet, joinall

from .cards import CardType, Card, TreasureCard, ActionCard, AttackCard, ReactionCard, VictoryCard, CurseCard, ReactionType
from . import base_cards
from ..hooks import PostGainHook
from ..grammar import a, s


# KINGDOM CARDS


class Crossroads(ActionCard):
    name = 'Crossroads'
    pluralized = 'Crossroads'
    _cost = 2
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            "Reveal your hand. <b>+1 Card</b> per Victory card revealed. If this is the first time you played a Crossroads this turn, <b>+3 Actions</b>.",
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        # Reveal your hand
        self.game.broadcast(f"{self.owner.name} revealed their hand: {Card.group_and_sort_by_cost(self.owner.hand)}.")
        # +1 Card per Victory card revealed
        num_victories = sum(1 for card in self.owner.hand if CardType.VICTORY in card.types)
        self.game.broadcast(f"{self.owner.name} has {s(num_victories, 'Victory card')} in their hand.")
        self.owner.draw(quantity=num_victories)
        # If this is the first time you played a Crossroads this turn, +3 Actions
        if not hasattr(self.owner.turn, "played_crossroads"):
            self.game.broadcast(f"This is the first Crossroads that {self.owner.name} has played this turn, so they receive +3 Actions.")
            self.owner.turn.played_crossroads = True
            self.owner.turn.plus_actions(3)


class Duchess(ActionCard):
    name = 'Duchess'
    pluralized = 'Duchesses'
    _cost = 2
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # "+2 $",
            "Each player (including you) looks at the top card of their deck and may discard it.",
            "In games using this, when you gain a Duchy, you may gain a Duchess.",
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 2

    class DuchessPostGainHook(PostGainHook):
        # This post gain hook is bound to the Duchy, so it will be called when a Duchy is gained.
        persistent = True

        def __call__(self, player, card, where_it_went):
            game = player.game
            # If there are no Duchesses remaining, nothing happens
            if game.supply.card_stacks[Duchess].is_empty:
                game.broadcast("There are no Duchesses remaining in the Supply so one cannot be gained.")
                return
            # Otherwise the player may gain a Duchess
            game.broadcast(f"{player.name} may gain a Duchess.")
            prompt = "You gained a Duchy and may gain a Duchess. Would you like to gain a Duchess?"
            if player.interactions.choose_yes_or_no(prompt):
                player.gain(Duchess)
            else:
                game.broadcast(f"{player.name} did not gain a Duchess.")


    def action(self):
        # Each player (including you) looks at the top card of their deck and may discard it
        pass
        # When you gain a Duchy, you may gain a Duchess
        pass


KINGDOM_CARDS = [
    Crossroads,
    Duchess,
    # FoolsGold,
    # Develop,
    # Oasis,
    # Oracle,
    # Scheme,
    # Tunnel,
    # JackOfAllTrades,
    # NobleBrigand,
    # NomadCamp,
    # SilkRoad,
    # SpiceMerchant,
    # Trader,
    # Cache,
    # Cartographer,
    # Embassy,
    # Haggler,
    # Highway,
    # IllGottenGains,
    # Inn,
    # Mandarin,
    # Margrave,
    # Stables,
    # BorderVillage,
    # Farmland,
]


for card_class in KINGDOM_CARDS:
    card_class.expansion = "Hinterlands"