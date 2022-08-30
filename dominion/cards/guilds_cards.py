from __future__ import annotations

import math

from gevent import Greenlet, joinall
from typing import TYPE_CHECKING, List, Deque, Type

from .cards import CardType, ReactionType, Card, TreasureCard, ActionCard, AttackCard, ReactionCard, VictoryCard
from . import base_cards
from ..hooks import PostGainHook, PreCleanupHook, PostDiscardHook, PostBuyHook, PostBuyPhaseHook
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
            "<b>+1 Coffers</b>",
        ]
    )

    extra_cards = 0
    extra_actions = 1
    extra_buys = 1
    extra_coppers = 0

    def action(self):
        self.game.broadcast(f"{self.owner} received +1 Coffers.")
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
            gainable_card_classes = [card_class for card_class in self.supply.card_stacks if CardType.ACTION in card_class.types and card_class.cost == amount_overpaid]
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
        prompt = f"You played a Doctor. Please name a card. You will then reveal the top 3 cards of your deck, trash the matches and put the rest back in any order."
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


class Masterpiece(TreasureCard):
    name = 'Masterpiece'
    _cost = 3
    types = [CardType.TREASURE]
    image_path = ''

    value = 1

    description = '\n'.join(
        [
            "1 $",
            "Overpay: Gain a Silver per $ overpaid.",
        ]
    )

    can_overpay = True
    overpay_description = " gain a Silver per $ overpaid."

    def overpay(self, amount_overpaid: int):
        self.owner.gain(base_cards.Silver, quantity=amount_overpaid)


class Advisor(ActionCard):
    name = 'Advisor'
    _cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # "+1 Action",
            "Reval the top 3 cards of your deck. The player to your left chooses one of them. Discard that card and put the rest into your hand.",
        ]
    )

    extra_cards = 0
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        # Reveal the top 3 cards of your deck
        revealed_cards = [card for _ in range(3) if (card := self.owner.take_from_deck()) is not None]
        if not revealed_cards:
            self.game.broadcast(f"{self.owner} had no cards left in their deck to reveal.")
            return
        self.game.broadcast(f"{self.owner} revealed {Card.group_and_sort_by_cost(revealed_cards)}.")
        # The player to your left chooses one of them
        if len(set([type(card) for card in revealed_cards])) == 1:
            # If there's only one type of card, don't bother asking which should be discarded
            card_to_discard = revealed_cards[0]
        else:
            player_to_left = self.owner.other_players[0]
            self.game.broadcast(f"{player_to_left} must choose a revealed card for {self.owner} to discard.")
            prompt = f"{self.owner} played an Advisor and revealed these cards. You are the player to their left. Which card should {self.owner} discard? They will put the rest into their hand."
            card_to_discard = player_to_left.interactions.choose_cards_from_list(prompt, revealed_cards, force=True)[0]
        # Discard that card and put the rest into your hand
        self.owner.discard(card_to_discard)
        revealed_cards.remove(card_to_discard)
        self.owner.hand.extend(revealed_cards)
        self.game.broadcast(f"{self.owner} put {Card.group_and_sort_by_cost(revealed_cards)} into their hand.")


class Herald(ActionCard):
    name = 'Herald'
    _cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # "+1 Card",
            # "+1 Action",
            "Reveal the top card of your deck. If it's an Action, play it.",
            "Overpay: Per $ overpaid, put any card from your discard pile onto your deck.",
        ]
    )

    can_overpay = True
    overpay_description = ", per $$ overpaid, put any card from $POSSESSIVE_ADJECTIVE discard pile onto $POSSESSIVE_ADJECTIVE deck."

    extra_cards = 1
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        # Reveal the top card of your deck
        if (revealed_card := self.owner.take_from_deck()) is None:
            self.game.broadcast(f"{self.owner} has no more cards in their deck.") 
            return
        # If it's an Action, play it
        if CardType.ACTION in revealed_card.types:
            self.game.broadcast(f"{self.owner} revealed {a(revealed_card)} with their Herald and plays it since it is an Action.")
            self.owner.turn.action_phase.play(revealed_card)
        else:
            self.game.broadcast(f"{self.owner} revealed {a(revealed_card)} but it is not an action.")
            self.owner.deck.append(revealed_card)

    def overpay(self, amount_overpaid: int):
        if not self.owner.discard_pile:
            self.game.broadcast(f"{self.owner} had no cards in their discard pile.")
            return
        max_cards = min(amount_overpaid, len(self.owner.discard_pile))
        # Per $ overpaid
        for num in range(max_cards):
            # Choose any card from your discard pile
            prompt = f"Please choose a card ({num + 1} of {max_cards}) from your discard pile to put onto your deck."
            card = self.owner.interactions.choose_card_from_discard_pile(prompt, force=True)
            # Put that card onto your deck
            self.owner.discard_pile.remove(card)
            self.owner.deck.append(card)
        # TODO: Create `choose_cards_from_discard_pile` with an `ordered` parameter to avoid this for loop
        # prompt = f"Please choose {max_cards} cards from your discard pile to put onto your deck. (The last card chosen will be on top.)
        # cards = self.owner.interactions.choose_cards_from_discard_pile(prompt, max_cards=max_cards, ordered=True, force=True)
        # for card in cards:
            # self.owner.discard.remove(card)
        # self.owner.deck.extend(cards)


class Plaza(ActionCard):
    name = 'Plaza'
    _cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # "+1 Card",
            # "+2 Actions",
            "You may discard a Treasure for <b>+1 Coffers.</b>",
        ]
    )

    extra_cards = 1
    extra_actions = 2
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        # You may discard a Treasure card
        prompt = f"You played a Plaza and may discard a Treasure for +1 Coffers."
        treasure_to_discard = self.owner.interactions.choose_specific_card_type_from_hand(prompt, card_type=CardType.TREASURE)
        if treasure_to_discard is None:
            self.game.broadcast(f"{self.owner} did not discard a Treasure.")
            return
        self.owner.discard_from_hand(treasure_to_discard)
        # If you do, +1 Coffers
        self.game.broadcast(f"{self.owner} received +1 Coffers.")
        self.owner.coffers += 1


class Taxman(AttackCard):
    name = 'Taxman'
    pluralized = 'Taxmen'
    _cost = 4
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = '\n'.join(
        [
            "You may trash a Treasure from your hand. Each other player with 5 or more cards in hand discards a copy of it (or reveals they can't). Gain a Treasure onto your deck costing up to 3 $ more than it.",
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    allow_simultaneous_reactions = True

    prompt = None # This is necessary but gets overwritten by the action() method

    def action(self):
        # You may trash a Treasure from your hand
        prompt = f"You played a Taxman and may trash a Treasure from your hand. If you do, each other player with 5 or more cards in hand will discard a copy of it if they can, and you will gain a Treasure onto your deck costing up to 3 $ more than the Treasure you trashed."
        treasure_to_trash = self.owner.interactions.choose_specific_card_type_from_hand(prompt, card_type=CardType.TREASURE)
        if treasure_to_trash is None:
            self.game.broadcast(f"{self.owner} did not trash a Treasure.")
            self.prompt = f"Other players need not discard anything."
            return
        self.owner.trash(treasure_to_trash)
        prompt = f"Other players with 5 or more cards in hand must discard {a(treasure_to_trash)} or reveal that they cannot."
        return type(treasure_to_trash)

    def attack_effect(self, attacker: Player, player: Player, trashed_treasure_class: Type[Card] | None):
        if trashed_treasure_class is None:
            return
        # Each other player with 5 or more cards in hand discards a copy of it (or reveals they can't)
        if len(player.hand) < 5:
            self.game.broadcast(f"{player} has fewer than 5 cards in hand.")
            return
        if any(isinstance(card, trashed_treasure_class) for card in player.hand):
            for card in player.hand:
                if isinstance(card, trashed_treasure_class):
                    player.discard_from_hand(card)
                    break
        else:
            self.game.broadcast(f"{player.name} revealed their hand: {Card.group_and_sort_by_cost(player.hand)}.")

    def post_attack_action(self, trashed_treasure_class: Type[Card] | None):
        if trashed_treasure_class is None:
            return
        # Gain a Treasure onto your deck costing up to 3 $ more than it
        max_cost = self.game.current_turn.get_cost(trashed_treasure_class) + 3
        prompt = f"You trashed {a(trashed_treasure_class.name)} with your Taxman and must gain a Treasure onto your deck costing up to {max_cost} $."
        treasure_class_to_gain = self.owner.interactions.choose_specific_card_type_from_supply(prompt=prompt, max_cost=max_cost, card_type=CardType.TREASURE, force=True)
        if treasure_class_to_gain is not None:
            self.owner.gain_to_deck(treasure_class_to_gain)


class Baker(ActionCard):
    name = 'Baker'
    _cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # "+1 Card",
            # "+1 Action",
            "<b>+1 Coffers</b>",
            "Setup: Each player gets <b>+1 Coffers</b>."
        ]
    )

    extra_cards = 1
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        self.owner.coffers += 1
        self.game.broadcast(f"{self.owner} received +1 Coffers.")


class Butcher(ActionCard):
    name = 'Butcher'
    _cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            "<b>+2 Coffers</b>",
            "You may trash a card from your hand. If you do, remove any number of tokens from your Coffers and gain a card costing up to the cost of the trashed card plus 1 $ per token removed.",
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        # +2 Coffers
        self.owner.coffers += 2
        self.game.broadcast(f"{self.owner} received +2 Coffers.")
        # You may trash a card from your hand
        prompt = "You played a Butcher and may trash a card from your hand and remove any number of tokens from your Coffers in order to gain a card costing up to the cost of the trashed card plus 1 $ per token removed."
        card_to_trash = self.owner.interactions.choose_card_from_hand(prompt=prompt, force=False)
        if card_to_trash is None:
            self.game.broadcast(f"{self.owner} did not trash a card.")
            return
        self.owner.trash(card_to_trash)
        # Remove any number of tokens from your Coffers
        if self.owner.coffers > 0:
            prompt = f"You played a Butcher and trashed {a(card_to_trash)}. You may remove any number of tokens from your Coffers. You will then gain a card costing up to {card_to_trash.cost} $ plus 1 $ per token removed."
            coffers_to_use = self.owner.interactions.choose_from_range(prompt, minimum=1, maximum=self.owner.coffers, force=False)
            if coffers_to_use is None:
                coffers_to_use = 0
                self.game.broadcast(f"{self.owner} did not remove any tokens from their Coffers.")
            else:
                self.game.broadcast(f"{self.owner} removed {coffers_to_use} tokens from their Coffers.")
            self.owner.coffers -= coffers_to_use
        # Gain a card costing up to the cost of the trashed card plus 1 $ per token removed
        max_cost = card_to_trash.cost + coffers_to_use
        if coffers_to_use > 0:
            prompt = f"You played a Butcher, trashed {a(card_to_trash)} and removed {coffers_to_use} tokens from your Coffers. You must gain a card costing up to {max_cost} $."
        else:
            prompt = f"You played a Butcher and trashed {a(card_to_trash)}. You must gain a card costing up to {max_cost} $."
        card_class_to_gain = self.owner.interactions.choose_card_class_from_supply(prompt=prompt, max_cost=max_cost, force=True)
        if card_class_to_gain is None:
            self.game.broadcast(f"There are no cards available for {self.owner} to gain costing up to {max_cost}.")
            return
        self.owner.gain(card_class_to_gain)


class Journeyman(ActionCard):
    name = 'Journeyman'
    pluralized = 'Journeymen'
    _cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            "Name a card. Reveal cards from your deck until you reveal 3 cards without that name. Put those cards into your hand and discard the rest."
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        # Name a card
        all_cards = [card_class for card_class in self.supply.card_stacks]
        prompt = 'You played a Journeyman. Name a card. You will then reveal cards from your deck until you reveal 3 cards without that name, put those cards into your hand and discard the rest.'
        named_card_class = self.interactions.choose_from_options(prompt, options=all_cards, force=True)
        self.game.broadcast(f'{self.owner} named {named_card_class.name}.')
        # Reveal cards from your deck until you reveal 3 cards without that name
        cards_to_discard = []
        cards_to_keep = []
        while len(cards_to_keep) < 3:
            if (card := self.owner.take_from_deck()) is None:
                self.game.broadcast(f'{self.owner} has no more cards to draw from.')
                break
            if isinstance(card, named_card_class):
                cards_to_discard.append(card)
            else:
                cards_to_keep.append(card)
        # Put those cards into your hand and discard the rest
        self.owner.hand.extend(cards_to_keep)
        self.owner.discard_pile.extend(cards_to_discard)
        self.game.broadcast(f"{self.owner} put {Card.group_and_sort_by_cost(cards_to_keep)} into their hand and discarded {Card.group_and_sort_by_cost(cards_to_discard)}.")


class MerchantGuild(ActionCard):
    name = 'Merchant Guild'
    _cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # "+1 Buy",
            # "+1 $",
            "At the end of your Buy phase this turn, <b>+1 Coffers</b> per card you gained in it.",
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 1
    extra_coppers = 1

    class MerchantGuildPostBuyPhaseHook(PostBuyPhaseHook):
        persistent = False # Pertains only to the current turn

        def __call__(self):
            player = self.game.current_turn.player
            cards_gained = self.game.current_turn.buy_phase.cards_gained
            # At the end of your Buy phase this turn, +1 Coffers per card you gained in it
            if cards_gained > 0:
                player.coffers += cards_gained
                self.game.broadcast(f"{player} gained {s(cards_gained, 'card')} during their Buy phase this turn and gets +{cards_gained} Coffers from their Merchant Guild.")       

    def action(self):
        # Add post buy phase hook
        post_buy_phase_hook = self.MerchantGuildPostBuyPhaseHook(self.game)
        self.owner.turn.add_post_buy_phase_hook(post_buy_phase_hook)


class Soothsayer(AttackCard):
    name = 'Soothsayer'
    _cost = 6
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = '\n'.join(
        [
            "Gain a Gold. Each other player gains a Curse, and if they did, draws a card.",
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    allow_simultaneous_reactions = False # In case the Curse supply pile runs out, must be resolved in player order

    prompt = None # This is necessary but gets overwritten by the action() method

    def action(self):
        # Gain a Gold
        self.owner.gain(base_cards.Gold)

    def attack_effect(self, attacker: Player, player: Player):
        # Each other player gains a Curse, and if they did, draws a card
        gained_cards = player.gain(base_cards.Curse, message=False)
        if gained_cards:
            player.draw(message=False)
            self.game.broadcast(f"{player} gained a Curse and drew a card.")
        else:
            self.game.broadcast(f'{self.name} could not gain Curse (or draw a card) since that supply pile is empty.')


KINGDOM_CARDS = [
    CandlestickMaker,
    Stonemason,
    Doctor,
    Masterpiece,
    Advisor,
    Herald,
    Plaza,
    Taxman,
    Baker,
    Butcher,
    Journeyman,
    MerchantGuild,
    Soothsayer,
]


for card_class in KINGDOM_CARDS:
    card_class.expansion = "Guilds"