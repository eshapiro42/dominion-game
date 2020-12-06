import math
from .cards import CardType, Card, TreasureCard, ActionCard, AttackCard, ReactionCard, VictoryCard, CurseCard
from ..turn import PreBuyHook


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
            prompt = f'You revealed a {revealed_treasure.name}. What would you like to do with it?'
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
        pass


KINGDOM_CARDS = [
    Loan,
    # TradeRoute,
]