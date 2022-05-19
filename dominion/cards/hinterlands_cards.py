from __future__ import annotations

import math

from gevent import Greenlet, joinall
from typing import TYPE_CHECKING, List

from .cards import CardType, Card, TreasureCard, ActionCard, AttackCard, ReactionCard, VictoryCard, CurseCard, ReactionType
from . import base_cards
from ..hooks import PostGainHook, PreCleanupHook
from ..grammar import a, s, it_or_them

if TYPE_CHECKING:
    from ..player import Player


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
        def player_reaction(player: Player):
            top_card_of_deck = player.take_from_deck()
            if top_card_of_deck is None:
                self.game.broadcast(f"{player.name} has no cards in their deck.")
                return
            if player == self.owner:
                prompt = f'You played a Duchess and revealed the top card of your deck, {a(top_card_of_deck.name)}. Would you like to discard it?'
            else:
                prompt = f'{self.owner} played a Duchess and you revealed the top card of your deck, {a(top_card_of_deck.name)}. Would you like to discard it?'
            if player.interactions.choose_yes_or_no(prompt):
                self.game.broadcast(f"{player.name} discarded the top card of their deck, {a(top_card_of_deck.name)}.")
                player.discard_pile.append(top_card_of_deck)
            else:
                self.game.broadcast(f"{player.name} did not discard the top card of their deck.")
                player.deck.append(top_card_of_deck)
        # Each player (including you) looks at the top card of their deck and may discard it
        greenlets = []
        for player in self.game.turn_order:
            # Simultaneous reactions are only allowed if they are enabled for the game
            if self.game.allow_simultaneous_reactions:
                greenlets.append(Greenlet.spawn(player_reaction, player))
            else:
                player_reaction(player)
        joinall(greenlets)


class FoolsGold(TreasureCard, ReactionCard):
    name = "Fool's Gold"
    _cost = 2
    types = [CardType.TREASURE, CardType.REACTION]
    image_path = ''

    description = '\n'.join(
        [
            "Worth 1 $ if it's the first time you played a Fool's Gold this turn, otherwise worth 4 $.",
            "When another player gains a Province, you may trash this from your hand, to gain a Gold onto your deck.",
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    value = 0 # The value is computed and added in the play() method.

    class FoolsGoldPostGainHook(PostGainHook):
        persistent = True

        def __call__(self, player, card, where_it_went):
            def other_player_reaction(other_player: Player):
                while any(isinstance(card, FoolsGold) for card in other_player.hand):
                    prompt = f"{player.name} gained a Province and you have a Reaction (Fool's Gold) in your hand. Would you like to trash the Fool's Gold to gain a Gold onto your deck?"
                    if other_player.interactions.choose_yes_or_no(prompt):
                        fools_golds_in_hand = [card for card in other_player.hand if isinstance(card, FoolsGold)]
                        fools_gold_to_trash = fools_golds_in_hand[0]
                        self.game.broadcast(f"{other_player.name} trashed a Fool's Gold to gain a Gold onto their deck.")
                        other_player.trash(fools_gold_to_trash, message=False)
                        other_player.gain_to_deck(base_cards.Gold, message=False)
                    else:
                        # Choosing not to trash a Fool's Gold ends the loop even if there are multiple remaining in the player's hand.
                        break
            # Each other player may trash Fool's Golds from their hand to gain Golds onto their decks.
            greenlets = []
            for other_player in player.other_players:
                # Simultaneous reactions are only allowed if they are enabled for the game
                if self.game.allow_simultaneous_reactions:
                    greenlets.append(Greenlet.spawn(other_player_reaction, other_player))
                else:
                    other_player_reaction(other_player)
            joinall(greenlets)

    def play(self):
        # Worth 1 $ if it's the first time you played a Fool's Gold this turn, otherwise worth 4 $.
        if not hasattr(self.owner.turn, "played_fools_gold"):
            value = 1
            self.owner.turn.played_fools_gold = True
        else:
            value = 4
        self.game.broadcast(f"{self.owner.name} gets +{value} $ from their Fool's Gold.")
        self.owner.turn.coppers_remaining += value

    def action(self):
        pass

    @property
    def can_react(self):
        return False # This card's reaction is governed by a post-gain hook

    def react(self):
        # React to an attack
        pass


class Develop(ActionCard):
    name = "Develop"
    _cost = 3
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            "Trash a card from your hand. Gain two cards onto your deck, with one costing exactly 1 $ more than it, and one costing exactly 1 $ less than it, in either order.",
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        prompt = f"You played a Develop and must trash a card from your hand. You will then gain two cards onto your deck, one costing exactly 1 $ more than it, and one costing exactly 1 $ less than it, in either order. Which card would you like to trash?"
        card_to_trash = self.owner.interactions.choose_card_from_hand(prompt, force=True)
        if card_to_trash is None:
            self.game.broadcast(f"{self.owner.name} had no cards in their hand to trash.")
            return
        self.owner.trash(card_to_trash, message=False)
        self.game.broadcast(f"{self.owner.name} trashed {a(card_to_trash.name)} with their Develop.")
        # Check whether there are cards of each cost in the Supply
        lower_cost = card_to_trash.cost - 1
        higher_cost = card_to_trash.cost + 1
        any_lower_cost_cards = any(card_class for card_class in self.game.supply.card_stacks if self.owner.turn.get_cost(card_class) == lower_cost)
        any_higher_cost_cards = any(card_class for card_class in self.game.supply.card_stacks if self.owner.turn.get_cost(card_class) == higher_cost)
        # If cards of each cost exist, ask the player to choose which order to gain the cards
        if any_lower_cost_cards and any_higher_cost_cards:
            prompt = f"You played a Develop and trashed {a(card_to_trash.name)}. You must gain two cards onto your deck, one costing exactly {card_to_trash.cost + 1} $, and one costing exactly {card_to_trash.cost - 1} $, in either order. Which would you like to gain first? (The first card gained will generally end up beneath the second on your deck, unless gaining them triggers other effects.)"
            options = [
                f"A card costing {lower_cost} $",
                f"A card costing {higher_cost} $",
            ]
            choice = self.owner.interactions.choose_from_options(prompt, options, force=True)
            if choice == options[0]:
                cost_order = [card_to_trash.cost + 1, card_to_trash.cost - 1]
            else:
                cost_order = [card_to_trash.cost - 1, card_to_trash.cost + 1]
        elif any_lower_cost_cards:
            self.game.broadcast(f"There are no cards in the Supply costing {higher_cost} $ for {self.owner.name} to gain.")
            cost_order = [lower_cost]
        elif any_higher_cost_cards:
            self.game.broadcast(f"There are no cards in the Supply costing {lower_cost} $ for {self.owner.name} to gain.")
            cost_order = [higher_cost]
        else:
            self.game.broadcast(f"There are no cards in the Supply costing either {lower_cost} $ or {higher_cost} $ for {self.owner.name} to gain.")
            cost_order = []
        for cost in cost_order:
            prompt = f"You played a Develop and trashed {a(card_to_trash.name)}. You must gain a card costing exactly {cost} $."
            card_class_to_gain = self.owner.interactions.choose_card_class_from_supply(prompt, max_cost=cost, force=True, exact_cost=True)
            if card_class_to_gain is not None:
                self.owner.gain_to_deck(card_class_to_gain, message=True)


class Oasis(ActionCard):
    name = "Oasis"
    _cost = 3
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # "+1 Card",
            # "+1 Action",
            # "+1 $",
            "Discard a card.",
        ]
    )

    extra_cards = 1
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 1

    def action(self):
        prompt = f"You played an Oasis and must discard a card."
        card_to_discard = self.owner.interactions.choose_card_from_hand(prompt, force=True)
        if card_to_discard is None:
            self.game.broadcast(f"{self.owner.name} had no cards in their hand to discard.")
            return
        self.owner.discard(card_to_discard, message=True)


class Oracle(AttackCard):
    name = 'Oracle'
    _cost = 3
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = '\n'.join(
        [
            "Each player (including you) reveals the top 2 cards of their deck, and discards them or puts them back, your choice (they choose the order).",
            "Then, <b>+2 Cards</b>.",
        ]
    )
    
    @property
    def prompt(self):
        return f"Other players must reveal the top 2 cards of their deck, and discard them or put them back, {self.owner}'s choice (they choose the order)."

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    allow_simultaneous_reactions = False # The frontend cannot currently handle the attacker simultaneously reacting to multiple players' responses

    def attack_effect(self, attacker, player):
        # Reveal the top 2 cards of the player's deck
        revealed_cards: List[Card] = []
        for _ in range(2):
            revealed_card = player.take_from_deck()
            if revealed_card is None:
                break
            revealed_cards.append(revealed_card)
        if len(revealed_cards) == 2:
            message = f"{player.name} revealed the top 2 cards of their deck: {Card.group_and_sort_by_cost(revealed_cards)}."
        elif len(revealed_cards) == 1:
            message = f"{player.name} revealed the top card of their deck: {a(revealed_cards[0].name)}."
        else:
            message = f"{player.name} had no cards in their deck to reveal."
        self.game.broadcast(message)
        if not revealed_cards:
            return
        # Ask the attacker to discard or put the revealed cards back
        prompt = f"{message} Would you like to discard {it_or_them(len(revealed_cards))} or put them back?"
        options = [
            f"Discard {it_or_them(len(revealed_cards))}",
            f"Put {it_or_them(len(revealed_cards))} back onto their deck",
        ]
        choice = attacker.interactions.choose_from_options(prompt, options, force=True)
        if choice == options[0]:
            for card in revealed_cards:
                player.discard_pile.append(card)
            self.game.broadcast(f"{player.name} discarded their revealed {s(len(revealed_cards), 'card', print_number=False)}.")
        else:
            if len(revealed_cards) == 1 or revealed_cards[0].name == revealed_cards[1].name:
                player.deck.extend(revealed_cards)
                self.game.broadcast(f"{player.name} put their revealed {s(len(revealed_cards), 'card', print_number=False)} back on their deck.")
            elif len(revealed_cards) == 2:
                prompt = f"You must return the revealed cards to your deck. Which one do you want to be on top?"
                options = [card.name for card in revealed_cards]
                choice = player.interactions.choose_from_options(prompt, options, force=True)
                index = options.index(choice)
                top_card = revealed_cards[index]
                bottom_card = revealed_cards[1 - index]
                player.deck.append(bottom_card)
                player.deck.append(top_card)
                self.game.broadcast(f"{player.name} put their revealed cards back on their deck with the {top_card} on top and the {bottom_card} beneath it.")

    def action(self):
        # Reveal the top 2 cards of the player's deck
        revealed_cards: List[Card] = []
        for _ in range(2):
            revealed_card = self.owner.take_from_deck()
            if revealed_card is None:
                break
            revealed_cards.append(revealed_card)
        if len(revealed_cards) == 2:
            message = f"{self.owner.name} revealed the top 2 cards of their deck: {Card.group_and_sort_by_cost(revealed_cards)}."
        elif len(revealed_cards) == 1:
            message = f"{self.owner.name} revealed the top card of their deck: {a(revealed_cards[0].name)}."
        else:
            message = f"{self.owner.name} had no cards in their deck to reveal."
        self.game.broadcast(message)
        if not revealed_cards:
            return
        # Ask the attacker to discard or put the revealed cards back
        prompt = f"{message.replace(self.owner.name, 'You').replace('their', 'your')} Would you like to discard {it_or_them(len(revealed_cards))} or put them back?"
        options = [
            f"Discard {it_or_them(len(revealed_cards))}",
            f"Put {it_or_them(len(revealed_cards))} back onto your deck",
        ]
        choice = self.owner.interactions.choose_from_options(prompt, options, force=True)
        if choice == options[0]:
            for card in revealed_cards:
                self.owner.discard_pile.append(card)
            self.game.broadcast(f"{self.owner.name} discarded their revealed {s(len(revealed_cards), 'card', print_number=False)}.")
        else:
            if len(revealed_cards) == 1 or revealed_cards[0].name == revealed_cards[1].name:
                self.owner.deck.extend(revealed_cards)
                self.game.broadcast(f"{self.owner.name} put their revealed {s(len(revealed_cards), 'card', print_number=False)} back on their deck.")
            elif len(revealed_cards) == 2:
                prompt = f"You must return the revealed cards to your deck. Which one do you want to be on top?"
                options = [card.name for card in revealed_cards]
                choice = self.owner.interactions.choose_from_options(prompt, options, force=True)
                index = options.index(choice)
                top_card = revealed_cards[index]
                bottom_card = revealed_cards[1 - index]
                self.owner.deck.append(bottom_card)
                self.owner.deck.append(top_card)
                self.game.broadcast(f"{self.owner.name} put their revealed cards back on their deck with the {top_card} on top and the {bottom_card} beneath it.")

    def post_attack_action(self):
        self.owner.draw(quantity=2, message=True)


class Scheme(ActionCard):
    name = "Scheme"
    _cost = 3
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # "+1 Card",
            # "+1 Action",
            "This turn, you may put one of your Action cards onto your deck when you discard it from play.",
        ]
    )

    extra_cards = 1
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    class SchemePreCleanupHook(PreCleanupHook):
        persistent = False

        def __call__(self):
            """
            You may put one of your played Action cards back onto your deck.
            """
            player = self.game.current_turn.player
            prompt = f"You played a Scheme this turn and may put one of your played Action cards back onto your deck."
            action_card = player.interactions.choose_specific_card_type_from_played_cards(prompt, CardType.ACTION)
            if action_card is None:
                return
            player.played_cards.remove(action_card)
            player.deck.append(action_card)
            self.game.broadcast(f"{player.name} put a played {action_card.name} back on their deck with their Scheme.")

    def action(self):
        pre_cleanup_hook = self.SchemePreCleanupHook(self.game)
        self.game.current_turn.add_pre_cleanup_hook(pre_cleanup_hook)
        self.game.broadcast(f"At the end of this turn, {self.owner.name} may put one of their played Action cards back onto their deck.")


KINGDOM_CARDS = [
    Crossroads,
    Duchess,
    FoolsGold,
    Develop,
    Oasis,
    Oracle,
    Scheme,
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