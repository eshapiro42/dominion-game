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

    overpay_description = " gain two Action cards each costing the amount overpaid."

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


class Doctor(ActionCard):
    name = 'Doctor'
    _cost = 3
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            "Name a card. Reveal the top 3 cards of your deck. Trash the matches. Put the rest back in any order.",
            "Overpay: Per $ overpaid, look at the top card of your deck; trash it, discard it, or put it back.",
        ]
    )

    can_overpay = True

    overpay_description = ", per $$ overpaid, look at the top card of $POSSESSIVE_ADJECTIVE deck and either trash it, discard it, or put it back."

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        # Name a card
        prompt = f"You played a Doctor. Please name a card. You will then reveal the top 3 cards, trash the matches and put the rest back in and order."
        options = list(self.supply.card_stacks.keys())
        named_card_class = self.interactions.choose_from_options(prompt, options, force=True)
        self.game.broadcast(f'{self.owner} named {named_card_class.name}.')
        # Reveal the top 3 cards of your deck
        top_three_cards = [card for _ in range(3) if (card := self.owner.take_from_deck()) is not None]
        remaining_cards = list(top_three_cards) # make a shallow copy
        self.game.broadcast(f"{self.owner} revealed {Card.group_and_sort_by_cost(top_three_cards)}.")
        # Trash the matches
        matches = [card for card in top_three_cards if isinstance(card, named_card_class)]
        if matches:
            for card in matches:
                self.supply.trash(card)
                remaining_cards.remove(card)
            self.game.broadcast(f"{self.owner} trashed {Card.group_and_sort_by_cost(matches)}.")  
        # Put the rest back in any order
        if not remaining_cards:
            return
        # If there is only one card (or card class) left, do not bother asking the player for the order
        if len(set([type(card) for card in remaining_cards])) != 1:
            prompt = "You played a Doctor and must return these revealed cards to your deck in any order. (The last card you choose will be the top card of your deck.)"
            remaining_cards = self.interactions.choose_cards_from_list(prompt, remaining_cards, force=True, max_cards=len(remaining_cards), ordered=True)
        for card in remaining_cards:
            self.owner.deck.append(card)
        self.game.broadcast(f"{self.owner} put {Card.group_and_sort_by_cost(remaining_cards)} back on top of their deck.")


    def overpay(self, amount_overpaid: int):
        # Per $ overpaid
        for num in range(amount_overpaid):
            # Look at the top card of your deck
            if (top_card := self.owner.take_from_deck()) is None:
                self.game.broadcast(f"{self.owner} has no more cards in their deck.") 
                return
            # Trash it, discard it, or put it back
            prompt = f"You overpaid for your purchased Doctor by {amount_overpaid} $. You revealed {a(top_card)} from the top of your deck ({num + 1} of {amount_overpaid}). What would you like to do with it?"
            options = [
                "Trash it",
                "Discard it",
                "Put it back",
            ]
            choice = self.owner.interactions.choose_from_options(prompt, options, force=True)
            if choice == "Trash it":
                self.supply.trash(top_card)
                self.game.broadcast(f"{self.owner} trashed {a(top_card)}.")
            elif choice == "Discard it":
                self.owner.discard(top_card)
            else:
                self.owner.deck.append(top_card)


KINGDOM_CARDS = [
    CandlestickMaker,
    Stonemason,
    Doctor,
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