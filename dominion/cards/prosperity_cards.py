import math
from .cards import CardType, Card, TreasureCard, ActionCard, AttackCard, ReactionCard, VictoryCard, CurseCard


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
                self.game.broadcast(f'{self.owner} revealed a {card}.')
                revealed_treasure = card
                break
            else:
                self.game.broadcast(f'{self.owner} revealed a {card}.')
                cards_revealed.append(card)
        # Ask if they want to discard or trash the revealed Treasure
        if revealed_treasure is not None:
            prompt = f'{self.owner}: You revealed a {revealed_treasure.name}. What would you like to do with it?'
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
    
    def action(self):
        # Trash a card from your hand
        prompt = f'{self.owner}: Choose a card from your hand to trash.'
        card_to_trash = self.owner.interactions.choose_card_from_hand(prompt=prompt, force=True)
        if card_to_trash is None:
            self.game.broadcast(f'{self.owner} has no cards in their hand to trash.')
        else:
            self.owner.trash(card_to_trash)
            self.game.broadcast(f'{self.owner} trashed a {card_to_trash}.')
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
    
    def action(self):
        pass


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
            self.game.broadcast(f'{self.owner} trashed a {card_to_trash}.')
            victory_tokens = math.floor(card_to_trash.cost / 2)
            self.owner.victory_tokens += victory_tokens
            if victory_tokens > 1:
                self.game.broadcast(f'{self.owner} took {victory_tokens} Victory tokens.')
            elif victory_tokens == 1:
                self.game.broadcast(f'{self.owner} took a Victory token.')
        # Each other player may trash a card from their hand
        for player in self.owner.other_players:
            pass



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
        pass


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
        pass


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

    def play(self):
        pass


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
    name = 'CardName'
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
        pass


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
        pass


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
        pass


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
    
    def action(self):
        pass


class Mountebank(AttackCard):
    name = 'CardName'
    cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+2 $',
            "Each other player may discard a Curse. If they don't, they gain a Curse and a Copper",
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 2
    
    def action(self):
        pass

    def attack_effect(self, attacker, player):
        pass



class Rabble(AttackCard):
    name = 'Rabble'
    cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+3 Cards',
            'Each other player reveals the top 3 cards of their deck, discards the Actions and Treasures, and puts the rest back in any order they choose.',
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0
    
    def action(self):
        pass

    def attack_effect(self, attacker, player):
        pass


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

    def play(self):
        pass


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
        pass


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
        pass


class Goons(AttackCard):
    name = 'Goons'
    cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Buy',
            '+2 $',
            'Each other player discards down to 3 cards in hand.',
            'While this is in play, when you buy a card, +1 Victory token.'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 1
    extra_coppers = 2
    
    def action(self):
        pass

    def attack_effect(self, attacker, player):
        pass


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

    def play(self):
        pass


class Bank(TreasureCard):
    name = 'Bank'
    cost = 7
    types = [CardType.TREASURE]
    image_path = ''

    @property
    def value(self):
        pass

    description = '\n'.join(
        [
            "When you play this, it's worth $1 per Treasure you have in play (counting this)."
        ]
    )

    def play(self):
        pass


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
        pass


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
        pass


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
        pass


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
    
    def action(self):
        pass


KINGDOM_CARDS = [
    Loan,
    TradeRoute,
    # Watchtower,
    # Bishop,
    # Monument,
    # Quarry,
    # Talisman,
    WorkersVillage,
    # City,
    # Contraband,
    # CountingHouse,
    # Mint,
    # Mountebank,
    # Rabble,
    # RoyalSeal,
    # Vault,
    # Venture,
    # Goons,
    # GrandMarket,
    # Hoard,
    # Bank,
    # Expand,
    # Forge,
    # KingsCourt,
    # Peddler
]