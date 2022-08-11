from __future__ import annotations

import math

from gevent import Greenlet, joinall
from typing import TYPE_CHECKING, List, Deque, Type

from .cards import CardType, ReactionType, Card, TreasureCard, ActionCard, AttackCard, ReactionCard, VictoryCard
from . import base_cards
from ..hooks import PostGainHook, PreCleanupHook, PostDiscardHook, PostBuyHook
from ..grammar import a, s, it_or_them

if TYPE_CHECKING:
    from ..player import Player


# KINGDOM CARDS


class CandlestickMaker(ActionCard):
    name = 'Candlestick Maker'
    _cost = 2
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # "+1 Action",
            # "+1 Buy",
            "+1 Coffers",
        ]
    )

    extra_cards = 0
    extra_actions = 1
    extra_buys = 1
    extra_coppers = 0

    def action(self):
        self.owner.coffers += 1


class Stonemason(ActionCard):
    name = 'Stonemason'
    _cost = 2
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            "Trash a card from your hand. Gain 2 cards each costing less than it.",
            "Overpay: Gain 2 Action cards each costing the amount overpaid.",
        ]
    )

    can_overpay = True

    overpay_description = "gain two Action cards each costing the amount overpaid."

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        # Trash a card from your hand
        prompt = f"You played a Stonemason. Choose a card from your hand to trash. You will then gain two cards each costing less than the trashed card (if possible)."
        card_to_trash = self.owner.interactions.choose_card_from_hand(prompt, force=True)
        if card_to_trash is None:
            self.game.broadcast(f"{self.owner} did not trash a card.")
            return
        self.owner.trash(card_to_trash)
        # Gain 2 cards each costing less than it
        max_cost = card_to_trash.cost - 1
        for num in range(2):
            gainable_card_classes = [card_class for card_class in self.supply.card_stacks if self.owner.turn.get_cost(card_class) <= max_cost]
            if not gainable_card_classes:
                self.game.broadcast(f"There are no available cards for {self.owner} to gain costing less than {max_cost + 1} $.")
                return
            prompt = f"You played a Stonemason and trashed {a(card_to_trash)}. Please choose a card ({num + 1} of 2) to gain costing at most {max_cost} $."
            card_class_to_gain = self.owner.interactions.choose_card_class_from_supply(prompt, max_cost, force=True)
            if card_class_to_gain is None:
                return
            self.owner.gain(card_class_to_gain)

    def overpay(self, amount_overpaid: int):
        # Gain two action cards each costing the amount overpaid
        for num in range(2):
            gainable_card_classes = [card_class for card_class in self.supply.card_stacks if CardType.ACTION in card_class.types]
            if not gainable_card_classes:
                self.game.broadcast(f"There are no available Action cards for {self.owner} to gain costing {amount_overpaid} $.")
                return
            prompt = f"You overpaid for your purchased Stonemason by {amount_overpaid} $. Please choose an Action card ({num + 1} of 2) to gain costing {amount_overpaid} $."
            # TODO: Add `exact_cost` parameter to `Interaction.choose_specific_card_type_from_supply` to avoid this sort of hack
            invalid_card_classes = [card_class for card_class in self.supply.card_stacks if CardType.ACTION not in card_class.types]
            card_class_to_gain = self.owner.interactions.choose_card_class_from_supply(
                prompt=prompt,
                max_cost=amount_overpaid,
                invalid_card_classes=invalid_card_classes,
                exact_cost=True,
                force=True,
            )
            if card_class_to_gain is None:
                return
            self.owner.gain(card_class_to_gain)
                        

KINGDOM_CARDS = [
    CandlestickMaker,
    Stonemason,
    # Doctor,
    # Masterpiece,
    # Advisor,
    # Herald,
    # Plaza,
    # Taxman,
    # Baker,
    # Butcher,
    # Journeyman,
    # MerchantGuild,
    # Soothsayer,
]


for card_class in KINGDOM_CARDS:
    card_class.expansion = "Guilds"