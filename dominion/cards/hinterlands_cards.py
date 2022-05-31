from __future__ import annotations

import math

from gevent import Greenlet, joinall
from typing import TYPE_CHECKING, List, Deque

from .cards import CardType, ReactionType, Card, TreasureCard, ActionCard, AttackCard, ReactionCard, VictoryCard
from . import base_cards
from ..hooks import PostGainHook, PreCleanupHook, PostDiscardHook, PostBuyHook
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
                return None
            # Otherwise the player may gain a Duchess
            game.broadcast(f"{player.name} may gain a Duchess.")
            prompt = "You gained a Duchy and may gain a Duchess. Would you like to gain a Duchess?"
            if player.interactions.choose_yes_or_no(prompt):
                player.gain(Duchess)
            else:
                game.broadcast(f"{player.name} did not gain a Duchess.")
            return None

    def action(self):
        # Each player (including you) looks at the top card of their deck and may discard it
        def player_reaction(player: Player):
            top_card_of_deck = player.take_from_deck()
            if top_card_of_deck is None:
                self.game.broadcast(f"{player.name} has no cards in their deck.")
                return
            if player == self.owner:
                prompt = f'You played a Duchess and looked at the top card of your deck, {a(top_card_of_deck.name)}. Would you like to discard it?'
            else:
                prompt = f'{self.owner} played a Duchess and you looked at the top card of your deck, {a(top_card_of_deck.name)}. Would you like to discard it?'
            if player.interactions.choose_yes_or_no(prompt):
                self.game.broadcast(f"{player.name} discarded the top card of their deck, {a(top_card_of_deck.name)}.")
                player.discard(top_card_of_deck, message=False)
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
            return None

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
    def reacts_to(self):
        return [] # This card's reaction is governed by a post-gain hook


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
    pluralized = "Oases"
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
        self.owner.discard_from_hand(card_to_discard)


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
                player.discard(card, message=False)
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
                self.owner.discard(card, message=False)
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


class Tunnel(VictoryCard, ReactionCard):
    name = "Tunnel"
    _cost = 3
    types = [CardType.VICTORY, CardType.REACTION]
    image_path = ''

    description = '\n'.join(
        [
            "2 victory points",
            "When you discard this other than during Clean-up, you may reveal it to gain a Gold.",
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    points = 2

    class TunnelPostDiscardHook(PostDiscardHook):
        persistent = True

        def __call__(self, player: Player):
            """
            When you discard this other than during Clean-up, you may reveal it to gain a Gold.
            """
            turn = self.game.current_turn
            if turn.current_phase == "Cleanup Phase":
                return
            if player.interactions.choose_yes_or_no(f"Would you like to reveal the Tunnel you just discarded to gain a Gold?"):
                player.gain(base_cards.Gold, message=False)
                self.game.broadcast(f"{player.name} discarded a Tunnel and revealed it to gain a Gold.")

    @property
    def reacts_to(self):
        return [] # This card's reaction is governed by a post-discard hook

    def action(self):
        pass


class JackOfAllTrades(ActionCard):
    name = "Jack of All Trades"
    pluralized = "Jacks of All Trades"
    _cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            "Gain a Silver.",
            "Look at the top card of your deck; you may discard it.",
            "Draw until you have 5 cards in hand.",
            "You may trash a non-Treasure card from your hand.",
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        # Gain a Silver
        self.owner.gain(base_cards.Silver)
        # Look at the top card of your deck; you may discard it
        top_card_of_deck = self.owner.take_from_deck()
        prompt = f"You played a Jack of All Trades and looked at the top card of your deck. It is {a(top_card_of_deck.name)}. Would you like to discard it?"
        if self.owner.interactions.choose_yes_or_no(prompt):
            self.owner.discard(top_card_of_deck, message=False)
            self.game.broadcast(f"{self.owner.name} discarded the top card of their deck, {a(top_card_of_deck)}.")
        else:
            self.owner.deck.append(top_card_of_deck)
            self.game.broadcast(f"{self.owner.name} did not discard the top card of their deck.")
        # Draw until you have 5 cards in hand
        num_cards_to_draw = 5 - len(self.owner.hand)
        self.owner.draw(num_cards_to_draw)
        # You may trash a non-Treasure card from your hand
        if all(CardType.TREASURE in card.types for card in self.owner.hand):
            self.owner.interactions.send(f"You have no non-Treasure cards in your hand to trash.")
            return
        treasure_cards_in_hand = [card for card in self.owner.hand if CardType.TREASURE in card.types]
        prompt = f"You played a Jack of All Trades. You may trash a non-Treasure card from your hand."
        card_to_trash = self.owner.interactions.choose_card_from_hand(prompt, force=False, invalid_cards=treasure_cards_in_hand)
        if card_to_trash is not None:
            self.owner.trash(card_to_trash)


class NobleBrigand(AttackCard):
    name = 'Noble Brigand'
    _cost = 4
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = '\n'.join(
        [
            # "+1 $",
            "When you buy or play this, each other player reveals the top 2 cards of their deck, trashes a revealed Silver or Gold you choose, discards the rest, and gains a Copper if they didn't reveal a Treasure. You gain the trashed cards.",
        ]
    )
    
    @property
    def prompt(self):
        return f"Other players must reveal the top 2 cards of their deck, trash a revealed Silver or Gold that {self.owner.name} chooses, discard the rest, and gain a Copper if they didn't reveal a Treasure. {self.owner.name} will gain the trashed cards."

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 1

    allow_simultaneous_reactions = False # The frontend cannot currently handle the attacker simultaneously reacting to multiple players' responses

    class NobleBrigandPostBuyHook(PostBuyHook):
        persistent = True

        def __call__(self, player: Player, purchased_card: NobleBrigand):
            # `player` is the player who bought the card. They will be the attacker.
            for other_player in player.other_players:
                purchased_card.attack_effect(player, other_player)

    def attack_effect(self, attacker: Player, player: Player):
        # Reveal the top 2 cards of their deck
        revealed_cards = []
        for _ in range(2):
            card = player.take_from_deck()
            if card is None:
                break
            revealed_cards.append(card) # These cards are now orphaned
        if revealed_cards:
            self.game.broadcast(f"{player.name} revealed the top {s(len(revealed_cards), 'card')} of their deck: {Card.group_and_sort_by_cost(revealed_cards)}.")
        any_treasures_revealed = any(CardType.TREASURE in card.types for card in revealed_cards)
        revealed_silvers = [card for card in revealed_cards if isinstance(card, base_cards.Silver)]
        revealed_golds = [card for card in revealed_cards if isinstance(card, base_cards.Gold)]
        # Trash a revealed Silver or Gold that the attacker chooses
        if revealed_silvers or revealed_golds:
            # If both a Silver and a Gold are revealed, the attacker chooses one
            if revealed_silvers and revealed_golds:
                prompt = f"{player.name} revealed a Silver and a Gold in response to your Noble Brigand. Which one would you like them to trash? (You will gain the trashed card.)"
                options = [
                    "Silver",
                    "Gold",
                ]
                choice = attacker.interactions.choose_from_options(prompt, options, force=True)
                if choice == "Silver":
                    card_to_trash = revealed_silvers[0]
                elif choice == "Gold":
                    card_to_trash = revealed_golds[0]
            # If one or two Silvers are revealed (but no Gold), choose a Silver
            elif revealed_silvers:
                card_to_trash = revealed_silvers[0]
            # If one or two Golds are revealed (but no Silver), choose a Gold
            elif revealed_golds:
                card_to_trash = revealed_golds[0]
            # The player trashes the Treasure and the attacker gains the trashed card
            revealed_cards.remove(card_to_trash)
            self.supply.trash(card_to_trash)
            self.game.broadcast(f"{player.name} trashed {a(card_to_trash.name)}.")
            attacker.gain_from_trash(type(card_to_trash), message=False)
            self.game.broadcast(f"{attacker.name} gained {player.name}'s trashed {card_to_trash.name}.")
        # Discard the rest
        player.discard(revealed_cards)
        # If the player did not reveal any Treasures, they gain a Copper
        if not any_treasures_revealed:
            player.gain(base_cards.Copper, message=False)
            self.game.broadcast(f"{player.name} gained a Copper since they revealed no Treasures in response to {attacker.name}'s Noble Brigand.")

    def action(self):
        pass


class NomadCamp(ActionCard):
    name = 'Nomad Camp'
    _cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # "+1 Buy",
            # "+2 $",
            "This is gained onto your deck (instead of to your discard pile).",
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 1
    extra_coppers = 2

    def action(self):
        pass

    @property
    def gain_to(self):
        return self.owner.deck


class SilkRoad(VictoryCard):
    name = 'Silk Road'
    _cost = 4
    types = [CardType.VICTORY]
    image_path = ''

    description = 'Worth 1 victory point for every 4 Victory cards you have (round down).'

    @property
    def points(self):
        victory_cards = [card for card in self.owner.all_cards if CardType.VICTORY in card.types]
        num_victory_cards = len(victory_cards)
        return math.floor(num_victory_cards / 4)


class SpiceMerchant(ActionCard):
    name = 'Spice Merchant'
    _cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            "You may trash a Treasure from your hand to choose one:",
            "<b>+2 Cards</b> and <b>+1 Action</b>;",
            "or <b>+1 Buy</b> and <b>+2 $</b>.",
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        prompt = """
            You played a Spice Merchant and may trash a Treasure from your hand. If you do, you will choose one:
            <br>
            <br>
            <div>
                <ul style="display: inline-block; padding-left: 0;">
                    <li><b>+2 Cards</b> and <b>+1 Action</b>.</li>
                    <li><b>+1 Buy</b> and <b>+2 $</b>.</li>
                </ul>
            </div>
        """
        if not any(CardType.TREASURE in card.types for card in self.owner.hand):
            self.game.broadcast(f"{self.owner.name} has no Treasures in their hand to trash.")
            return
        treasure_to_trash = self.owner.interactions.choose_specific_card_type_from_hand(prompt, CardType.TREASURE, )
        if treasure_to_trash is None:
            self.game.broadcast(f"{self.owner.name} chose not to trash a Treasure.")
            return
        self.owner.trash(treasure_to_trash)
        prompt = f"You played a Spice Merchant and trashed {a(treasure_to_trash.name)}. Which option would you like to choose?"
        options = [
            "+2 Cards and +1 Action",
            "+1 Buy and +2 $",
        ]
        choice = self.owner.interactions.choose_from_options(prompt, options, force=True)
        if choice == "+2 Cards and +1 Action":
            self.owner.draw(2)
            self.owner.turn.plus_actions(1)
        elif choice == "+1 Buy and +2 $":
            self.owner.turn.plus_buys(1)
            self.owner.turn.plus_coppers(2)


class Trader(ReactionCard):
    name = 'Trader'
    _cost = 4
    types = [CardType.ACTION, CardType.REACTION]
    image_path = ''

    description = '\n'.join(
        [
            "Trash a card from your hand. Gain a Silver per 1 $ it costs.",
            "When you gain a card, you may reveal this from your hand, to exchange the card for a Silver.",
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    @property
    def reacts_to(self):
        return [ReactionType.GAIN]

    def react_to_gain(self, gained_card: Card, where_it_went: Deque, gained_from_trash: bool = False):
        if where_it_went == self.owner.discard_pile:
            where_it_went_string = "their discard pile"
            self.owner.discard_pile.remove(gained_card)
            silver = self.owner.gain(base_cards.Silver, message=False, ignore_post_gain_actions=True)[0]
        elif where_it_went == self.owner.deck:
            where_it_went_string = "their deck"
            self.owner.deck.remove(gained_card)
            silver = self.owner.gain_to_deck(base_cards.Silver, message=False, ignore_post_gain_actions=True)[0]
        elif where_it_went == self.owner.hand:
            where_it_went_string = "their hand"
            self.owner.hand.remove(gained_card)
            silver = self.owner.gain_to_hand(base_cards.Silver, message=False, ignore_post_gain_actions=True)[0]
        elif where_it_went == self.supply.trash_pile:
            where_it_went_string = "the Trash"
            self.supply.trash_pile[type(gained_card)].pop()
            silver = self.owner.gain(base_cards.Silver, message=False, ignore_post_gain_actions=True)[0]
        if gained_from_trash:
            where_it_came_from_string = "Trash"
            self.supply.trash(gained_card)
        else:
            where_it_came_from_string = "Supply"
            self.supply.return_card(gained_card)
        self.game.broadcast(f"{self.owner.name}'s revealed a Trader to return the gained {gained_card.name} from {where_it_went_string} to the {where_it_came_from_string} and put a Silver in {where_it_went_string} instead.")
        ignore_card_class_next_time = True
        return silver, where_it_went, ignore_card_class_next_time

    def action(self):
        prompt = "You played a Trader and must choose a card from your hand to trash. You will gain a Silver per 1 $ it costs."
        card_to_trash = self.owner.interactions.choose_card_from_hand(prompt, force=True)
        if card_to_trash is not None:
            self.owner.trash(card_to_trash)
            if card_to_trash.cost > 0:
                self.owner.gain(base_cards.Silver, quantity=card_to_trash.cost, message=False)
                self.game.broadcast(f"{self.owner.name} trashed {a(card_to_trash.name)} with their Trader and gained {s(card_to_trash.cost, 'Silver')}.")


class Cache(TreasureCard):
    name = 'Cache'
    _cost = 5
    types = [CardType.TREASURE]
    image_path = ''

    value = 3

    description = '\n'.join(
        [
            '3 $',
            'When you gain this, gain 2 Coppers.',
        ]
    )

    class CachePostGainHook(PostGainHook):
        persistent = True

        def __call__(self, player, card, where_it_went):
            player.gain(base_cards.Copper, 2)
            return where_it_went

    def play(self):
        pass


class Cartographer(ActionCard):
    name = 'Cartographer'
    _cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # "+1 Card",
            # "+1 Action",
            "Look at the top 4 cards of your deck. Discard any number of them, then put the rest back in any order.",
        ]
    )

    extra_cards = 1
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        # Look at the top 4 cards of your deck
        cards_from_deck = []
        for _ in range(4):
            card = self.owner.take_from_deck()
            if card is not None:
                cards_from_deck.append(card)
        if not cards_from_deck:
            self.game.broadcast(f"{self.owner.name} has no cards in their deck.")
            return
        if len(cards_from_deck) < 4:
            self.game.broadcast(f"{self.owner.name} only had {len(cards_from_deck)} cards in their deck to reveal.")
        # Discard any number of them
        prompt = f"You played a Cartographer. These are the top {len(cards_from_deck)} cards of your deck. Choose any number of them to discard. You will then put the rest back in any order."
        cards_to_discard = self.owner.interactions.choose_cards_from_list(prompt, cards_from_deck, force=False, max_cards=len(cards_from_deck))
        if cards_to_discard:
            self.owner.discard(cards_to_discard, message=False)
            self.game.broadcast(f"{self.owner.name} discarded {Card.group_and_sort_by_cost(cards_to_discard)} from their deck with their Cartographer.")
        # Put the rest back in any order
        cards_to_put_back = [card for card in cards_from_deck if card not in cards_to_discard]
        if not cards_to_put_back:
            return
        # If there is only one card (or card class) left, do not bother asking the player for the order
        if len(set([type(card) for card in cards_to_put_back])) != 1:
            prompt = "You played a Cartographer and must return these revealed cards to your deck in any order. (The last card you choose will be the top card of your deck.)"
            cards_to_put_back = self.owner.interactions.choose_cards_from_list(prompt, cards_to_put_back, force=True, max_cards=len(cards_to_put_back), ordered=True)
        for card in cards_to_put_back:
            self.owner.deck.append(card)
        self.owner.interactions.send(f"You put {Card.group_and_sort_by_cost(cards_to_put_back)} back onto your deck.")
        self.game.broadcast(f"{self.owner.name} put {s(len(cards_to_put_back), 'card')} back on top of their deck.")
        

class Embassy(ActionCard):
    name = 'Embassy'
    pluralized = 'Embassies'
    _cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # "+5 Cards",
            "Discard 3 cards.",
            "When you gain this, each other player gains a Silver.",
        ]
    )

    extra_cards = 5
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    class EmbassyPostGainHook(PostGainHook):
        persistent = True

        def __call__(self, player, card, where_it_went):
            # Each other player gains a Silver
            self.game.broadcast(f"Each other player gains a Silver.")
            for other_player in player.other_players:
                other_player.gain(base_cards.Silver)
            return None

    def action(self):
        prompt = "You played an Embassy and must choose 3 cards to discard."
        cards_to_discard = self.owner.interactions.choose_cards_from_hand(prompt, force=True, max_cards=3)
        for card_to_discard in cards_to_discard:
            self.owner.discard_from_hand(card_to_discard, message=False)
        self.game.broadcast(f"{self.owner.name} discarded {Card.group_and_sort_by_cost(cards_to_discard)}.")


class Haggler(ActionCard):
    name = 'Haggler'
    _cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # "+2 $",
            "While this is in play, when you buy a card, gain a cheaper non-Victory card.",
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 2

    class HagglerPostBuyHook(PostBuyHook):
        persistent = True

        def __call__(self, player, card):
            max_cost = card.cost - 1
            prompt = f"You bought a {card.name} and have a Haggler in play. Choose a non-Victory card costing up to {max_cost} $ to gain."
            # Gain a cheaper non-Victory card for each Haggler in play
            hagglers_in_play = [card for card in player.played_cards if isinstance(card, Haggler)]
            hagglers_already_used = []
            while hagglers_in_play:
                haggler = hagglers_in_play[0]
                invalid_card_classes = [card_class for card_class in self.game.supply.card_stacks if CardType.VICTORY in card_class.types]
                card_class_to_gain = player.interactions.choose_card_class_from_supply(prompt, max_cost=max_cost, force=True, invalid_card_classes=invalid_card_classes)
                if card_class_to_gain is not None:
                    self.game.broadcast(f"{player.name} had a Haggler in play and gained a {card_class_to_gain.name}.")
                    player.gain(card_class_to_gain, message=False)
                hagglers_already_used.append(haggler)
                hagglers_in_play = [played_card for played_card in player.played_cards if isinstance(played_card, Haggler) and played_card not in hagglers_already_used]

    def action(self):
        pass


class Highway(ActionCard):
    name = 'Highway'
    _cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # "+1 Card",
            # "+1 Action",
            "While this is in play, cards cost 1 $ less, but not less than 0 $.",
        ]
    )

    extra_cards = 1
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        # Modify card costs
        for card_class in self.supply.card_stacks:
            self.game.current_turn.modify_cost(card_class, -1)


class IllGottenGains(TreasureCard):
    name = 'Ill-Gotten Gains'
    pluralized = 'Ill-Gotten Gains'
    _cost = 5
    types = [CardType.TREASURE]
    image_path = ''

    value = 1

    description = '\n'.join(
        [
            "1 $",
            "When you play this, you may gain a Copper to your hand.",
            "When you gain this, each other player gains a Curse."
        ]
    )

    class IllGottenGainsPostGainHook(PostGainHook):
        persistent = True

        def __call__(self, player, card, where_it_went):
            # Each other player gains a Curse
            self.game.broadcast(f"Each other player gains a Curse.")
            for other_player in player.other_players:
                other_player.gain(base_cards.Curse)
            return None

    def play(self):
        prompt = "You played an Ill-Gotten Gains. Would you like to gain a Copper to your hand?"
        if self.owner.interactions.choose_yes_or_no(prompt):
            self.owner.gain_to_hand(base_cards.Copper)


class Inn(ActionCard):
    name = 'Inn'
    _cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # "+2 Cards",
            # "+2 Actions",
            "Discard 2 cards.",
            "When you gain this, look through your discard pile, reveal any number of Action cards from it (which can include this), and shuffle them into your deck.",
        ]
    )

    extra_cards = 2
    extra_actions = 2
    extra_buys = 0
    extra_coppers = 0

    class InnPostGainHook(PostGainHook):
        persistent = True

        def __call__(self, player, card, where_it_went):
            # Look through your discard pile, reveal any number of Action cards from it (which can include this), and shuffle them into your deck.
            prompt = "You gained an Inn. You may reveal any number of Action cards from your discard pile to shuffle into your deck."
            cards_to_shuffle = player.interactions.choose_cards_of_specific_type_from_discard_pile(prompt, force=False, card_type=CardType.ACTION, max_cards=None)
            if not cards_to_shuffle:
                self.game.broadcast(f"{player.name} did not reveal any Action cards from their discard pile.")
                return where_it_went
            for card_to_shuffle in cards_to_shuffle:
                player.discard_pile.remove(card_to_shuffle)
            player.deck.extend(cards_to_shuffle)
            player.shuffle_deck(message=False)
            self.game.broadcast(f"{player.name} revealed {Card.group_and_sort_by_cost(cards_to_shuffle)} from their discard pile and shuffled {it_or_them(len(cards_to_shuffle))} into their deck.")
            if card in cards_to_shuffle:
                return player.deck
            return where_it_went

    def action(self):
        prompt = "You played an Inn. Select 2 cards to discard."
        if (cards := self.owner.interactions.choose_cards_from_hand(prompt, force=True, max_cards=2)) is not None:
            for card in cards:
                self.owner.discard_from_hand(card, message=False)
            self.game.broadcast(f"{self.owner} discarded {Card.group_and_sort_by_cost(cards)}.")
        else:
            self.game.broadcast(f"{self.owner} did not have any cards to discard.")


class Mandarin(ActionCard):
    name = 'Mandarin'
    _cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            # "+3 $",
            "Put a card from your hand onto your deck.",
            "When you gain this, put all Treasures you have in play onto your deck in any order.",
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 3

    class MandarinPostGainHook(PostGainHook):
        persistent = True

        def __call__(self, player, card, where_it_went):
            # Put all Treasures you have in play onto your deck in any order.
            treasures_in_play = [played_card for played_card in player.played_cards if CardType.TREASURE in played_card.types]
            if not treasures_in_play:
                self.game.broadcast(f"{player.name} did not have any Treasures in play.")
                return where_it_went
            elif len(set(type(treasure) for treasure in treasures_in_play)) == 1:
                # If all Treasures are the same type, do not ask for the order
                self.game.broadcast(f"{player.name} returned all their played Treasures ({Card.group_and_sort_by_cost(treasures_in_play)}) to their deck.")
                return where_it_went
            prompt = f"You gained a Mandarin and must return all your played Treasures to your deck. Please select the order in which you would like to return them. (The last Treasure you select will be on the top of your deck.)"
            treasures_to_put_on_deck = player.interactions.choose_cards_of_specific_type_from_played_cards(prompt, force=True, card_type=CardType.TREASURE, max_cards=len(treasures_in_play), ordered=True)
            for treasure in treasures_to_put_on_deck:
                player.played_cards.remove(treasure)
                player.deck.append(treasure)
            self.game.broadcast(f"{player.name} returned all their played Treasures ({Card.group_and_sort_by_cost(treasures_in_play)}) to their deck.")
            return where_it_went

    def action(self):
        # Put a card from your hand onto your deck
        prompt = "You played a Mandarin and must select a card to put onto your deck."
        card_to_put_back = self.owner.interactions.choose_card_from_hand(prompt, force=True)
        if card_to_put_back is None:
            self.game.broadcast(f"{self.owner} did not have any cards in their hand to put onto their deck.")
            return
        self.owner.hand.remove(card_to_put_back)
        self.owner.deck.append(card_to_put_back)
        self.game.broadcast(f"{self.owner} put {a(card_to_put_back)} from their hand onto their deck with their Mandarin.")


KINGDOM_CARDS = [
    Crossroads,
    Duchess,
    FoolsGold,
    Develop,
    Oasis,
    Oracle,
    Scheme,
    Tunnel,
    JackOfAllTrades,
    NobleBrigand,
    NomadCamp,
    SilkRoad,
    SpiceMerchant,
    Trader,
    Cache,
    Cartographer,
    Embassy,
    Haggler,
    Highway,
    IllGottenGains,
    Inn,
    Mandarin,
    # Margrave,
    # Stables,
    # BorderVillage,
    # Farmland,
]


for card_class in KINGDOM_CARDS:
    card_class.expansion = "Hinterlands"