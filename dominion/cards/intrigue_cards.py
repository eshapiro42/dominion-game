import math
from .cards import CardType, Card, TreasureCard, ActionCard, AttackCard, ReactionCard, VictoryCard, CurseCard
from . import base_cards
from ..hooks import TreasureHook, PreBuyHook, PostGainHook


# KINGDOM CARDS

class Courtyard(ActionCard):
    name = 'Courtyard'
    cost = 2
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+3 Cards',
            'Put a card from your hand onto your deck.'
        ]
    )

    extra_cards = 3
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        # Choose a card from your hand
        prompt = f'Choose a card from your hand to put onto your deck.'
        card = self.interactions.choose_card_from_hand(prompt, force=True)
        # Put that card onto your deck
        if card is not None:
            self.owner.hand.remove(card)
            self.owner.deck.append(card)
            self.game.broadcast(f'{self.owner} put a card from their hand onto their deck.')


class Lurker(ActionCard):
    name = 'Lurker'
    cost = 2
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Action',
            'Choose one: Trash an Action card from the Supply; or gain an Action card from the trash.'
        ]
    )

    extra_cards = 0
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        # Choose one
        prompt = f'Which would you like to do?'
        options = [
            'Trash an Action card from the Supply',
            'Gain an Action card from the trash'
        ]
        choice = self.interactions.choose_from_options(prompt, options, force=True)
        if choice == 'Trash an Action card from the Supply':
            prompt = f'Choose an Action card from the Supply to trash.'
            card_class = self.interactions.choose_specific_card_type_from_supply(prompt, max_cost=math.inf, card_type=CardType.ACTION, force=True)
            if card_class is not None:
                card_to_trash = self.supply.draw(card_class)
                self.supply.trash(card_to_trash)
                self.game.broadcast(f'{self.owner} trashed a {card_to_trash} from the Supply.')
        elif choice == 'Gain an Action card from the trash':
            prompt = f'Choose an Action card from the trash to gain.'
            # TODO: FINISH IMPLEMENTING THIS
        

class Pawn(ActionCard):
    name = 'Pawn'
    cost = 2
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            'Choose two: +1 Card; +1 Action; +1 Buy; +1 $. The choices must be different.'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        options = [
            '+1 Card',
            '+1 Action',
            '+1 Buy',
            '1 $'
        ]
        # First, the choices are selected
        choices = []
        prompt = f'Which would you like to choose first?'
        choice = self.interactions.choose_from_options(prompt, options, force=True)
        choices.append(choice)
        options.remove(choice) # The same option cannot be chosen again
        prompt = f'Which would you like to choose second?'
        choice = self.interactions.choose_from_options(prompt, options, force=True)
        choices.append(choice)
        self.game.broadcast(f"{self.owner} chose: {', '.join(choices)}.")
        # Then the selected choices are executed
        for choice in choices:
            if choice == '+1 Card':
                cards_drawn = self.owner.draw(1)
                if cards_drawn:
                    card = cards_drawn[0]
                    self.game.broadcast(f'+1 card --> {len(self.owner.hand)} cards in hand.')
                    self.interactions.send(f'You drew: {card}.')
            elif choice == '+1 Action':
                self.owner.turn.actions_remaining += 1
                self.game.broadcast(f'+1 action --> {self.owner.turn.actions_remaining} actions.')
            elif choice == '+1 Buy':
                self.owner.turn.buys_remaining += 1
                self.game.broadcast(f'+1 buy --> {self.owner.turn.buys_remaining} buys.')
            elif choice == '1 $':
                self.owner.turn.coppers_remaining += 1
                self.game.broadcast(f'+1 $ --> {self.owner.turn.coppers_remaining} $.')


class Masquerade(ActionCard):
    name = 'Masquerade'
    cost = 3
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+2 Cards',
            'Each player with any cards in hand passes one to the next such player to their left at once. Then you may trash a card from your hand.'
        ]
    )

    extra_cards = 2
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        # TODO: Remember to set .owner attribute of each card after they trade hands!
        pass


class ShantyTown(ActionCard):
    name = 'Shanty Town'
    cost = 3
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+2 Actions',
            'Reveal your hand. If you have no Action cards in hand, +2 Cards.'
        ]
    )

    extra_cards = 0
    extra_actions = 2
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        self.game.broadcast(f"{self.owner} reveals their hand: {', '.join(map(str, self.owner.hand))}")
        if not any(CardType.ACTION in card.types for card in self.owner.hand):
            self.game.broadcast(f'{self.owner} has no Action cards in their hand, so they draw 2 cards.')
            cards_drawn = self.owner.draw(2)
            if cards_drawn:
                self.game.broadcast(f'{self.owner} drew {len(cards_drawn)} cards.')
                self.interactions.send(f"You drew: {', '.join(map(str, cards_drawn))}.")
            else:
                self.game.broadcast(f'{self.owner} has no more cards to draw from.')
        else:
            self.game.broadcast(f'{self.owner} has Action cards in their hand.')


class Steward(ActionCard):
    name = ''
    cost = 3
    types = [CardType.ACTION]
    image_path = 'Steward'

    description = '\n'.join(
        [
            'Choose one: +2 Cards; or +2 $; or trash 2 cards from your hand.'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        pass


class Swindler(AttackCard):
    name = 'Swindler'
    cost = 3
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = '\n'.join(
        [
            '+2 $',
            'Each other player trashes the top card of their deck and gains a card with the same cost that you choose.'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 2

    @property
    def prompt(self):
        return f'Each other player trashes the top card of their deck and gains a card with the same cost that {self.owner} chooses.'

    def attack_effect(self, attacker, player):
        pass

    def action(self):
        pass


class WishingWell(ActionCard):
    name = 'Wishing Well'
    cost = 3
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Card',
            '+1 Action',
            'Name a card, then reveal the top card of your deck. If you named it, put it into your hand.'
        ]
    )

    extra_cards = 1
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        pass


class Baron(ActionCard):
    name = 'Baron'
    cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Buy',
            "You may discard an Estate for +4 $. If you don't, gain an Estate."
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 1
    extra_coppers = 0

    def action(self):
        pass


class Bridge(ActionCard):
    name = 'Bridge'
    cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Buy',
            '+1 $',
            'This turn, cards (everywhere) cost 1 $ less, but not less than 0 $.'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 1
    extra_coppers = 1

    def action(self):
        pass


class Conspirator(ActionCard):
    name = 'Conspirator'
    cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+2 $',
            "If you've played 3 or more Actions this turn (counting this), +1 Card and +1 Action."
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 2

    def action(self):
        pass


class Diplomat(ReactionCard):
    name = 'Diplomat'
    cost = 4
    types = [CardType.ACTION, CardType.REACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+2 Cards',
            'If you have 5 or fewer cards in hand (after drawing), +2 Actions.',
            'When another player plays an Attack card, you may first reveal this from a hand of 5 or more cards, to draw 2 cards then discard 3.'
        ]
    )

    extra_cards = 2
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def react(self):
        pass

    def action(self):
        pass


class Ironworks(ActionCard):
    name = 'Ironworks'
    cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            'Gain a card costing up to 4 $. If the gained card is an...',
            'Action card, +1 Action',
            'Treasure card, +1 $',
            'Victory card, +1 Card'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        pass


class Mill(ActionCard, VictoryCard):
    name = 'Mill'
    cost = 4
    types = [CardType.ACTION, CardType.VICTORY]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Card',
            '+1 Action',
            'You may discard 2 cards, for +2 $',
            '1 victory point'
        ]
    )

    extra_cards = 1
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        pass

    @property
    def points(self):
        pass


class MiningVillage(ActionCard):
    name = 'Mining Village'
    cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Card',
            '+2 Actions',
            'You may trash this for +2 $.'
        ]
    )

    extra_cards = 1
    extra_actions = 2
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        pass


class SecretPassage(ActionCard):
    name = 'Secret Passage'
    cost = 4
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+2 Cards',
            '+1 Action',
            'Take a card from your hand and put it anywhere in your deck.'
        ]
    )

    extra_cards = 2
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        pass


class Courtier(ActionCard):
    name = 'Courtier'
    cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            'Reveal a card from your hand. For each type it has (Action, Attack, etc.), choose one: +1 Action; or +1 Buy; or +3 $; or gain a Gold. The choices must be different.'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        pass


class Duke(VictoryCard):
    name = 'Duke'
    cost = 5
    types = [CardType.VICTORY]
    image_path = ''

    description = '\n'.join(
        [
            'Worth 1 victory point per Duchy you have.'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    @property
    def points(self):
        pass


class Minion(AttackCard):
    name = 'Minion'
    cost = 5
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Action',
            'Choose one: +2 $; or discard your hand, +4 Cards, and each other player with at least 5 cards in hand discards their hand and draws 4 cards.'
        ]
    )
    prompt = 'Each other player with at least 5 cards in hand discards their hand and draws 4 cards.'

    extra_cards = 0
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def attack_effect(self):
        pass

    def action(self):
        pass


class Patrol(ActionCard):
    name = 'Patrol'
    cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+3 Cards',
            'Reveal the top 4 cards of your deck. Put the Victory cards and Curses into your hand. Put the rest back in any order.'
        ]
    )

    extra_cards = 3
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        pass


class Replace(AttackCard):
    name = 'Replace'
    cost = 5
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = '\n'.join(
        [
            "Trash a card from your hand. Gain a card costing up to 2 $ more than it. If the gained card is an Action or Treasure, put it onto your deck; if it's a Victory card, each other player gains a Curse."
        ]
    )
    prompt = 'Each other player gains a curse.'

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def attack_effect(self):
        pass

    def action(self):
        pass


class Torturer(AttackCard):
    name = 'Torturer'
    cost = 5
    types = [CardType.ACTION, CardType.ATTACK]
    image_path = ''

    description = '\n'.join(
        [
            '+3 Cards',
            "Each other player either discards 2 cards or gains a Curse to their hand, their choice. (They may pick an option they can't do)."
        ]
    )
    prompt = "Each other player either discards 2 cards or gains a Curse to their hand, their choice. (They may pick an option they can't do)."

    extra_cards = 3
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def attack_effect(self):
        pass

    def action(self):
        pass


class TradingPost(ActionCard):
    name = 'Trading Post'
    cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            'Trash 2 cards from your hand. If you did, gain a Silver to your hand.'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        pass


class Upgrade(ActionCard):
    name = 'Upgrade'
    cost = 5
    types = [CardType.ACTION]
    image_path = ''

    description = '\n'.join(
        [
            '+1 Card',
            '+1 Action',
            'Trash a card from your hand. Gain a card costing exactly 1 $ more than it.'
        ]
    )

    extra_cards = 1
    extra_actions = 1
    extra_buys = 0
    extra_coppers = 0

    def action(self):
        pass


class Harem(TreasureCard, VictoryCard):
    name = 'Harem'
    cost = 6
    types = [CardType.TREASURE, CardType.VICTORY]
    image_path = ''

    description = '\n'.join(
        [
            '2 $',
            '2 victory points'
        ]
    )

    value = 2
    points = 2


class Nobles(ActionCard, VictoryCard):
    name = 'Nobles'
    cost = 6
    types = [CardType.ACTION, CardType.VICTORY]
    image_path = ''

    description = '\n'.join(
        [
            'Choose one: +3 Card; or +2 Actions.'
        ]
    )

    extra_cards = 0
    extra_actions = 0
    extra_buys = 0
    extra_coppers = 0

    points = 2

    def action(self):
        pass


KINGDOM_CARDS = [
    Courtyard,
    # Lurker,
    Pawn,
    # Masquerade,
    ShantyTown,
    # Steward,
    # Swindler,
    # WishingWell,
    # Baron,
    # Bridge,
    # Conspirator,
    # Diplomat,
    # Ironworks,
    # Mill,
    # MiningVillage,
    # SecretPassage,
    # Courtier,
    # Duke,
    # Minion,
    # Patrol,
    # Replace,
    # Torturer,
    # TradingPost,
    # Upgrade,
    # Harem,
    # Nobles
]