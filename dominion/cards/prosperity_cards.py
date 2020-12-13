import math
from .cards import CardType, Card, TreasureCard, ActionCard, AttackCard, ReactionCard, VictoryCard, CurseCard
from . import base_cards
from ..hooks import TreasureHook, PreBuyHook, PostGainHook
from ..grammar import a, s


# BASIC CARDS


class Platinum(TreasureCard):
    name = 'Platinum'
    cost = 9
    types = [CardType.TREASURE]
    image_path = ''
    description = '5 $'
    value = 5

class Colony(VictoryCard):
    name = 'Colony'
    cost = 11
    types = [CardType.VICTORY]
    description = '10 victory points'
    image_path = ''
    points = 10


BASIC_CARDS = [
    Platinum,
    Colony
]


# KINGDOM CARDS


class Loan(TreasureCard):
    name = 'Loan'
    cost = 3
    types = [CardType.TREASURE]
    image_path = ''

    value = 1

    description = '\n'.join(
        [
            '1 $',
            'When you play this, reveal cards from your deck until you reveal a Treasure. Discard it or trash it. Discard the other cards.'
        ]
    )

    def play(self):
        # Reveal cards from the owner's deck until they reveal a Treasure
        cards_revealed = []
        while True:
            card = self.owner.take_from_deck()
            if card is None:
                revealed_treasure = None
                break
            elif CardType.TREASURE in card.types:
                self.game.broadcast(f'{self.owner} revealed {a(card)}.')
                revealed_treasure = card
                break
            else:
                self.game.broadcast(f'{self.owner} revealed {a(card)}.')
                cards_revealed.append(card)
        # Ask if they want to discard or trash the revealed Treasure
        if revealed_treasure is not None:
            prompt = f'{self.owner}: You revealed {a(revealed_treasure.name)}. What would you like to do with it?'
            options = ['Trash', 'Discard']
            choice = self.interactions.choose_from_options(prompt=prompt, options=list(options), force=True)
            if choice == 'Trash':
                self.supply.trash(revealed_treasure)
                self.game.broadcast(f'{self.owner} trashed the revealed {card}.')
            elif choice == 'Discard':
                self.owner.discard_pile.append(revealed_treasure)
                self.game.broadcast(f'{self.owner} discarded the revealed {card}.')
        # Discard the other revealed cards
        if cards_revealed:
            self.owner.discard_pile.extend(cards_revealed)
            self.game.broadcast(f"{self.owner} discarded the other revealed cards: {', '.join(map(str, cards_revealed))}.")


class TradeRoute(ActionCard):
    name = 'Trade Route'
    cost = 3
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Buy',
            'Trash a card from your hand.',
            '+1 $ per Coin token on the Trade Route mat.'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 1
    extra_coppers = 0

    class TradeRoutePostGainHook(PostGainHook):
        persistent = False

        def __call__(self, player, card, where_it_went):
            game = player.game
            trade_route_before = game.supply.trade_route
            game.supply.trade_route += 1
            game.broadcast(f'{player} gained {a(self.card_class.name)} and moved a Coin token to the Trade Route mat ({trade_route_before} Coin tokens --> {game.supply.trade_route} Coin tokens).')
    
    def action(self):
        # Trash a card from your hand
        prompt = f'{self.owner}: Choose a card from your hand to trash.'
        card_to_trash = self.owner.interactions.choose_card_from_hand(prompt=prompt, force=True)
        if card_to_trash is None:
            self.game.broadcast(f'{self.owner} has no cards in their hand to trash.')
        else:
            self.owner.trash(card_to_trash)
        # +1 $ per Coin token on the Trade Route mat
        self.owner.turn.coppers_remaining += self.supply.trade_route
        self.game.broadcast(f'{self.owner} gets +{self.supply.trade_route} $ from the Coin tokens on the Trade Route mat.')


class Watchtower(ReactionCard):
    name = 'Watchtower'
    cost = 3
    types = [CardType.ACTION, CardType.REACTION]
    image_path = ''

    description = '\n'.join(
        [
            'Draw until you have 6 cards in hand.',
            'When you gain a card, you may reveal this from your hand, to either trash that card or put it onto your deck.',
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    class WatchtowerPostGainHook(PostGainHook):
        persistent = True

        def __call__(self, player, card, where_it_went):
            if card in where_it_went:
                game = player.game
                if any(isinstance(card, Watchtower) for card in player.hand):
                    prompt = f'You have a Reaction (Watchtower) in your hand. Would you like to play it?'
                    if player.interactions.choose_yes_or_no(prompt):
                        game.broadcast(f'{player} revealed a Watchtower. They may trash the {card} they just gained or put it onto their deck.')
                        prompt = f'Would you like to trash the {card} you just gained or put it onto your deck?'
                        options = ['Trash', 'Put on deck']
                        choice = player.interactions.choose_from_options(prompt, options, force=False)
                        if choice is None:
                            game.broadcast(f'{player} decided not to use their Watchtower.')
                        elif choice == 'Trash':
                            where_it_went.remove(card)
                            game.supply.trash(card)
                            game.broadcast(f'{player} trashed the {card}.')
                        elif choice == 'Put on deck':
                            where_it_went.remove(card)
                            player.deck.append(card)
                            game.broadcast(f'{player} put the {card} onto their deck.')

    @property
    def can_react(self):
        return False # This card's reaction is governed by a post-gain hook

    def react(self):
        pass

    def action(self):
        num_cards_to_draw = 6 - len(self.owner.hand)
        self.owner.draw(num_cards_to_draw)


class Bishop(ActionCard):
    name = 'Bishop'
    cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+1 $',
            '+1 Victory token',
            'Trash a card from your hand. +1 Victory token per 2 $ it costs (round down). Each other player may trash a card from their hand.'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 1
    
    def action(self):
        # +1 Victory token
        self.owner.victory_tokens += 1
        self.game.broadcast(f'{self.owner} took a Victory token.')
        # Trash a card from your hand. +1 Victory token per 2 $ it costs (round down)
        prompt = f'{self.owner}: Choose a card from your hand to trash for Victory tokens.'
        card_to_trash = self.owner.interactions.choose_card_from_hand(prompt=prompt, force=True)
        if card_to_trash is None:
            self.game.broadcast(f'{self.owner} has no cards in their hand to trash.')
        else:
            self.owner.trash(card_to_trash)
            victory_tokens = math.floor(card_to_trash.cost / 2)
            self.owner.victory_tokens += victory_tokens
            self.game.broadcast(f"{self.owner} took {s(victory_tokens, 'Victory token')}.")
        # Each other player may trash a card from their hand
        for player in self.owner.other_players:
            prompt = f'{player}: You may trash a card from your hand.'
            card_to_trash = player.interactions.choose_card_from_hand(prompt=prompt, force=False)
            if card_to_trash is not None:
                player.trash(card_to_trash)


class Monument(ActionCard):
    name = 'Monument'
    cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+2 $',
            '+1 Victory token',
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 2
    
    def action(self):
        self.owner.victory_tokens += 1
        self.game.broadcast(f'{self.owner} took a Victory token.')


class Quarry(TreasureCard):
    name = 'Quarry'
    cost = 4
    types = [CardType.TREASURE]
    image_path = ''

    value = 1

    description = '\n'.join(
        [
            '1 $',
            'While this is in play, Action cards cost 2 $ less, but not less than 0 $.'
        ]
    )

    def play(self):
        # Modify Action card costs
        action_card_classes = [card_class for card_class in self.supply.card_stacks if CardType.ACTION in card_class.types]
        for card_class in action_card_classes:
            self.supply.modify_cost(card_class, -2)


class Talisman(TreasureCard):
    name = 'Talisman'
    cost = 4
    types = [CardType.TREASURE]
    image_path = ''

    value = 1

    description = '\n'.join(
        [
            '1 $',
            'While this is in play, when you buy a non-Victory card costing 4 $ or less, gain a copy of it.'
        ]
    )

    class TalismanPostGainHook(PostGainHook):
        persistent = True

        def __call__(self, player, card, where_it_went):
            game = player.game
            game.broadcast(f'{player} gains an extra {self.card_class.name} from their Talisman.')
            player.gain_without_hooks(self.card_class)


    def play(self):
        # All non-Victory cards costing 4 $ or less get a post gain hook added this turn
        for card_class in self.supply.card_stacks:
            if card_class.cost <= 4 and CardType.VICTORY not in card_class.types:
                post_gain_hook = self.TalismanPostGainHook(card_class)
                self.owner.turn.add_post_gain_hook(post_gain_hook, card_class) 


class WorkersVillage(ActionCard):
    name = "Worker's Village"
    cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Card',
            '+2 Actions',
            '+1 Buy'
        ]
    )

    extra_cards = 1
    extra_actions = 2
    extra_buys = 1
    extra_coppers = 0
    
    def action(self):
        pass


class City(ActionCard):
    name = 'City'
    cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Card',
            '+2 Actions',
            'If there are one or more empty Supply piles, +1 Card. If there are two or more, +1 Buy and +1 $.'
        ]
    )

    extra_cards = 1
    extra_actions = 2
    extra_buys = 0
    extra_coppers = 0
    
    def action(self):
        if self.supply.num_empty_stacks >= 1:
            self.game.broadcast(f'{self.owner} draws a card since there are one or more empty Supply piles.')
            self.owner.draw(1)
        if self.supply.num_empty_stacks >= 2:
            self.game.broadcast(f'{self.owner} gets +1 buy and +1 $ since there are two or more empty Supply piles.')
            self.turn.plus_buys(1)
            self.turn.plus_coppers(1)


class Contraband(TreasureCard):
    name = 'Contraband'
    cost = 5
    types = [CardType.TREASURE]
    image_path = ''

    value = 3

    description = '\n'.join(
        [
            '3 $',
            '+1 Buy',
            "When you play this, the player to your left names a card. You can't buy that card this turn."
        ]
    )

    def play(self):
        # +1 Buy (this must be done manually here since it is a Treasure card)
        self.turn.plus_buys(1)
        # The player to your left names a card
        player_to_left = self.owner.other_players[0]
        prompt = f'{player_to_left}: Which card should {self.owner} be forbidden from buying this turn?'
        forbidden_card_class = player_to_left.interactions.choose_card_class_from_supply(prompt, max_cost=math.inf, force=True) # max_cost=math.inf because any card can be named
        self.owner.turn.invalid_card_classes.append(forbidden_card_class)
        self.game.broadcast(f'{self.owner} cannot buy {a(forbidden_card_class.name)} this turn.')


class CountingHouse(ActionCard):
    name = 'Counting House'
    cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            'Look through your discard pile, reveal any number of Coppers from it, and put them into your hand.',
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0
    
    def action(self):
        coppers_in_discard_pile = [card for card in self.owner.discard_pile if isinstance(card, base_cards.Copper)]
        if coppers_in_discard_pile:
            prompt = f"{self.owner}: You have {s(len(coppers_in_discard_pile), 'Copper')} in your discard pile. How many would you like to put into your hand?"
            options = list(range(1, len(coppers_in_discard_pile) + 1))
            num_coppers = self.owner.interactions.choose_from_options(prompt, options, force=False)
            if num_coppers:
                for _ in range(num_coppers):
                    copper = coppers_in_discard_pile.pop()
                    self.owner.discard_pile.remove(copper)
                    self.owner.hand.append(copper)
                self.game.broadcast(f"{self.owner} put {s(num_coppers, 'Copper')} from their discard pile into their hand.")
            else:
                self.game.broadcast(f'{self.owner} did not put any Coppers from their discard pile into their hand.')


class Mint(ActionCard):
    name = 'Mint'
    cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            'You may reveal a Treasure card from your hand. Gain a copy of it.',
            'When you buy this, trash all Treasures you have in play.',
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0
    
    class MintPostGainHook(PostGainHook):
        persistent = True

        def __call__(self, player, card, where_it_went):
            game = player.game
            treasures_in_play = [card for card in player.played_cards if CardType.TREASURE in card.types]
            for treasure in treasures_in_play:
                player.trash_played_card(treasure)

    def action(self):
        # You may reveal a Treasure card from your hand.
        prompt = f'{self.owner}: You may reveal a Treasure card from your hand to gain a copy of it.'
        treasure_card = self.owner.interactions.choose_specific_card_type_from_hand(prompt, CardType.TREASURE)
        if treasure_card is not None:
            treasure_card_class = type(treasure_card)
            self.owner.gain_without_hooks(treasure_card_class, message=False)
            self.game.broadcast(f'{self.owner} revealed {a(treasure_card)} and gained a copy of it.')

        

class Mountebank(AttackCard):
    name = 'Mountebank'
    cost = 5
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = '\n'.join(
        [
            '+2 $',
            "Each other player may discard a Curse. If they don't, they gain a Curse and a Copper.",
        ]
    )
    prompt = "Each other player may discard a Curse. If they don't, they gain a Curse and a Copper."


    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 2
    
    def action(self):
        pass

    def attack_effect(self, attacker, player):
        # Check if the other player has a Curse in their hand
        curses_in_hand = [card for card in player.hand if isinstance(card, base_cards.Curse)]
        # If they do, ask if they would like to discard it
        if curses_in_hand and player.interactions.choose_yes_or_no(prompt=f'{player}: You have a Curse in your hand. Would you like to reveal and discard it?'):
            curse = curses_in_hand[0]
            player.discard(curse)
        else:
            player.gain(base_cards.Curse)
            player.gain(base_cards.Copper)


class Rabble(AttackCard):
    name = 'Rabble'
    cost = 5
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = '\n'.join(
        [
            '+3 Cards',
            'Each other player reveals the top 3 cards of their deck, discards the Actions and Treasures, and puts the rest back in any order they choose.',
        ]
    )
    prompt = 'Each other player reveals the top 3 cards of their deck, discards the Actions and Treasures, and puts the rest back in any order they choose.'

    extra_cards = 3
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0
    
    def action(self):
        pass

    def attack_effect(self, attacker, player):
        # Player reveals the top 3 cards of their deck
        revealed_actions_and_treasures = []
        revealed_other_cards = []
        for _ in range(3):
            card = player.take_from_deck()
            if card is None:
                self.game.broadcast(f'{player} has no more cards to draw from.')
                break
            else:
                self.game.broadcast(f'{player} revealed {a(card)}.')
                if CardType.TREASURE in card.types or CardType.ACTION in card.types:
                    revealed_actions_and_treasures.append(card)
                else:
                    revealed_other_cards.append(card)
        # Player discards Actions and Treasures
        if revealed_actions_and_treasures:
            player.discard_pile.extend(revealed_actions_and_treasures)
            self.game.broadcast(f"{player} discarded: {', '.join(map(str, revealed_actions_and_treasures))}.")
        # Player puts the rest back on their deck in any order they choose
        if len(revealed_other_cards) == 1:
            # If there's only one card, put it back on top of the deck
            card = revealed_other_cards[0]
            self.game.broadcast(f'{player} put {a(card)} back on top of their deck.')
            player.deck.append(card)
        elif len(revealed_other_cards) == 2:
            # If there are two, ask which should be on top
            prompt = f"You must return these cards to the top of your deck: {', '.join(map(str, revealed_other_cards))}. Which card would you like to be on top?"
            top_card = player.interactions.choose_from_options(prompt=prompt, options=revealed_other_cards, force=True)
            revealed_other_cards.remove(top_card)
            bottom_card = revealed_other_cards[0]
            player.deck.append(bottom_card)
            player.deck.append(top_card)
            self.game.broadcast(f'{player} put {a(bottom_card)} and {a(top_card)} back on top of their deck.')
        elif len(revealed_other_cards) == 3:
            # If there are three, ask which should be on top and in the middle
            prompt = f"You must return these cards to the top of your deck: {', '.join(map(str, revealed_other_cards))}. Which card would you like to be on top?"
            top_card = player.interactions.choose_from_options(prompt=prompt, options=revealed_other_cards, force=True)
            revealed_other_cards.remove(top_card)
            prompt = f"Which card would you like to be in the middle?"
            middle_card = player.interactions.choose_from_options(prompt=prompt, options=revealed_other_cards, force=True)
            revealed_other_cards.remove(middle_card)
            bottom_card = revealed_other_cards[0]
            player.deck.append(bottom_card)
            player.deck.append(middle_card)
            player.deck.append(top_card)
            self.game.broadcast(f'{player} put {a(bottom_card)}, {a(middle_card)} and {a(top_card)} back on top of their deck.')


class RoyalSeal(TreasureCard):
    name = 'Royal Seal'
    cost = 5
    types = [CardType.TREASURE]
    image_path = ''

    value = 2

    description = '\n'.join(
        [
            '2 $',
            'While this is in play, when you gain a card, you may put that card onto your deck.'
        ]
    )

    class RoyalSealPostGainHook(PostGainHook):
        persistent = True

        def __call__(self, player, card, where_it_went):
            if card in where_it_went: # Need this in case a Watchtower or other card has already moved the card
                game = player.game
                prompt = f'{player}: Would you like to put the {card} you just gained onto your deck?'
                if player.interactions.choose_yes_or_no(prompt):
                    where_it_went.remove(card)
                    player.deck.append(card)
                    game.broadcast(f'{player} put the {card} onto their deck.')

    def play(self):
        # All cards get a post gain hook added this turn (but only one!)
        for card_class in self.supply.card_stacks:
            if not any(isinstance(hook, self.RoyalSealPostGainHook) for hook in self.owner.turn.post_gain_hooks[card_class]):
                post_gain_hook = self.RoyalSealPostGainHook(card_class)
                self.owner.turn.add_post_gain_hook(post_gain_hook, card_class) 


class Vault(ActionCard):
    name = 'Vault'
    cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+2 Cards',
            'Discard any number of cards for +1 $ each.',
            'Each other player may discard 2 cards, to draw a card.'
        ]
    )

    extra_cards = 2
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0
    
    def action(self):
        # Discard any number of cards for +1 $ each
        discarded_card_count = 0
        while True:
            prompt = 'Choose a card from your hand to discard.'
            card_to_discard = self.interactions.choose_card_from_hand(prompt=prompt, force=False)
            if card_to_discard is None:
                break
            else:
                discarded_card_count += 1
                self.owner.discard(card_to_discard)
        coppers_before = self.owner.turn.coppers_remaining
        self.turn.plus_coppers(discarded_card_count)
        # Each other player may discard 2 cards, to draw a card.
        for player in self.owner.other_players:
            if len(player.hand) < 2:
                self.game.broadcast(f'{player} does not have 2 cards in their hand.')
            else:
                prompt = f'{player}: Would you like to discard 2 cards to draw a card?'
                if player.interactions.choose_yes_or_no(prompt):
                    for discard_num in range(2):
                        prompt = f'{player}: Choose card {discard_num + 1}/2 to discard.'
                        card_to_discard = player.interactions.choose_card_from_hand(prompt, force=True)
                        if card_to_discard is not None:
                            player.discard(card_to_discard)
                    player.draw(1)
                else:
                    self.game.broadcast(f'{player} chose not to discard 2 cards.')



class Venture(TreasureCard):
    name = 'Venture'
    cost = 5
    types = [CardType.TREASURE]
    image_path = ''

    value = 1

    description = '\n'.join(
        [
            '1 $',
            'When you play this, reveal cards from your deck until you reveal a Treasure. Discard the other cards. Play that Treasure.'
        ]
    )

    def play(self):
        cards_to_discard = []
        revealed_treasure = None
        while True:
            card = self.owner.take_from_deck()
            if card is None:
                self.game.broadcast(f'{self.owner} has no more cards to draw from.')
                break
            else:
                self.game.broadcast(f'{self.owner} revealed {a(card)}.')
            if CardType.TREASURE in card.types:
                revealed_treasure = card
                break
            else:
                cards_to_discard.append(card)
        if cards_to_discard:
            self.owner.discard_pile.extend(cards_to_discard)
            self.game.broadcast(f"{self.owner} discarded: {', '.join(map(str, cards_to_discard))}.")
        if revealed_treasure is not None:
            self.owner.turn.buy_phase.play_treasure(revealed_treasure)


class Goons(AttackCard):
    name = 'Goons'
    cost = 5
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Buy',
            '+2 $',
            'Each other player discards down to 3 cards in hand.',
            'While this is in play, when you buy a card, +1 Victory token.'
        ]
    )
    prompt = 'Each other player discards down to 3 cards in hand.'

    extra_cards = 0
    extra_actions = 0
    extra_buys = 1
    extra_coppers = 2

    class GoonsPostGainHook(PostGainHook):
        persistent = True

        def __call__(self, player, card, where_it_went):
            game = player.game
            game.broadcast(f'{player} takes a Victory token from their Goons.')
            player.victory_tokens += 1


    def action(self):
        # All cards get a post gain hook added this turn
        for card_class in self.supply.card_stacks:
            post_gain_hook = self.GoonsPostGainHook(card_class)
            self.owner.turn.add_post_gain_hook(post_gain_hook, card_class) 

    def attack_effect(self, attacker, player):
        number_to_discard = len(player.hand) - 3
        self.game.broadcast(f"{player} must discard {s(number_to_discard, 'card')}.")
        for card_num in range(number_to_discard):
            prompt = f'{player}: Choose card {card_num + 1} of {number_to_discard} to discard.'
            card_to_discard = player.interactions.choose_card_from_hand(prompt=prompt, force=True)
            player.discard(card_to_discard)


class GrandMarket(ActionCard):
    name = 'Grand Market'
    cost = 6
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Card',
            '+1 Action',
            '+1 Buy',
            '+2 $',
            "You can't buy this if you have any Coppers in play."
        ]
    )

    extra_cards = 1
    extra_actions = 1
    extra_buys = 1
    extra_coppers = 2

    class GrandMarketTreasureHook(TreasureHook):
        persistent = True

        def __call__(self):
            player = self.game.current_turn.player
            turn = self.game.current_turn
            # If the current player has played any Coppers, they cannot buy a Grand Market this turn
            if any(isinstance(card, base_cards.Copper) for card in player.played_cards):
                turn.invalid_card_classes.append(GrandMarket)

    def action(self):
        pass


class Hoard(TreasureCard):
    name = 'Hoard'
    cost = 6
    types = [CardType.TREASURE]
    image_path = ''

    value = 2

    description = '\n'.join(
        [
            '2 $',
            'While this is in play, when you buy a Victory card, gain a Gold'
        ]
    )

    class HoardPostGainHook(PostGainHook):
        persistent = True

        def __call__(self, player, card, where_it_went):
            game = player.game
            game.broadcast(f'{player} gains a Gold from their Hoard.')
            player.gain_without_hooks(base_cards.Gold)


    def play(self):
        # All Victory cards get a post gain hook added this turn
        for card_class in self.supply.card_stacks:
            if CardType.VICTORY in card_class.types:
                post_gain_hook = self.HoardPostGainHook(card_class)
                self.owner.turn.add_post_gain_hook(post_gain_hook, card_class) 


class Bank(TreasureCard):
    name = 'Bank'
    cost = 7
    types = [CardType.TREASURE]
    image_path = ''

    value = None

    description = '\n'.join(
        [
            "When you play this, it's worth $1 per Treasure you have in play (counting this)."
        ]
    )

    def play(self):
        # Worth 1 $ per Treasure in play
        self.value = len([card for card in self.owner.played_cards if CardType.TREASURE in card.types])


class Expand(ActionCard):
    name = 'Expand'
    cost = 7
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            'Trash a card from your hand. Gain a card costing up to 3 $ more than it.'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0
    
    def action(self):
        prompt = 'Choose a card from your hand to trash.'
        card_to_trash = self.interactions.choose_card_from_hand(prompt=prompt, force=True)
        if card_to_trash is not None:
            self.owner.trash(card_to_trash)
            max_cost = card_to_trash.cost + 3
            self.owner.turn.buy_phase.buy_without_side_effects(max_cost=max_cost, force=True)


class Forge(ActionCard):
    name = 'Forge'
    cost = 7
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            'Trash any number of cards from your hand. Gain a card with cost exactly equal to the total cost of the trashed cards'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0
    
    def action(self):
        current_value = 0
        # Trash any number of cards from your hand
        while self.owner.hand:
            prompt = f'You may choose a card from your hand to trash (current value: {current_value}).'
            card_to_trash = self.interactions.choose_card_from_hand(prompt=prompt, force=False)
            if card_to_trash is None:
                break
            else:
                self.owner.trash(card_to_trash)
                current_value += card_to_trash.cost
        # Gain a card with cost exactly equal to the total cost of the trashed cards
        self.owner.turn.buy_phase.buy_without_side_effects(max_cost=current_value, force=True, exact_cost=True)
        

class KingsCourt(ActionCard):
    name = "King's Court"
    cost = 7
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            'You may play an Action card from your hand three times.'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0
    
    def action(self):
        prompt = 'Select an action card to play three times.'
        card = self.interactions.choose_specific_card_type_from_hand(prompt=prompt, card_type=CardType.ACTION)
        if card is not None:
            # Playing the card should not use any actions, so we use a special method
            # The first time, add the card to the played cards area
            self.owner.play(card)
            self.game.broadcast(f"{self.owner} plays {a(card.name)} for the first time, thanks to their King's Court.")
            self.owner.turn.action_phase.play_without_side_effects(card)
            self.game.broadcast(f"{self.owner} plays {a(card.name)} for the second time, thanks to their King's Court.")
            self.owner.turn.action_phase.play_without_side_effects(card)
            self.game.broadcast(f"{self.owner} plays {a(card.name)} for the third time, thanks to their King's Court.")
            self.owner.turn.action_phase.play_without_side_effects(card)
        else:
            self.game.broadcast(f"{self.owner} has no other Actions cards to use with their King's Court.")


class Peddler(ActionCard):
    name = 'Peddler'
    cost = 8
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Card',
            '+1 Action',
            '+1 $',
            'During your Buy phase, this costs 2 $ less per Action card you have in play, but not less than 0 $.'
        ]
    )

    extra_cards = 1
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 1

    class PeddlerPreBuyHook(PreBuyHook):
        persistent = True

        def __call__(self):
            player = self.game.current_turn.player
            turn = self.game.current_turn
            num_actions = len([card for card in player.played_cards if CardType.ACTION in card.types])
            self.game.supply.modify_cost(Peddler, -2 * num_actions)

    def action(self):
        pass


KINGDOM_CARDS = [
    Loan,
    TradeRoute,
    Watchtower,
    Bishop,
    Monument,
    Quarry,
    Talisman,
    WorkersVillage,
    City,
    Contraband,
    CountingHouse,
    Mint,
    Mountebank,
    Rabble,
    RoyalSeal,
    Vault,
    Venture,
    Goons,
    GrandMarket,
    Hoard,
    Bank,
    Expand,
    Forge,
    KingsCourt,
    Peddler
]