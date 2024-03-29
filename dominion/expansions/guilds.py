from __future__ import annotations

from typing import TYPE_CHECKING, Callable, List, Optional, Tuple, Type

from .expansion import Expansion
from ..cards import guilds_cards
from ..grammar import s, GrammaticalPerson, format_pronouns
from ..hooks import PostBuyHook

if TYPE_CHECKING:
    from ..cards.cards import Card
    from ..player import Player


class OverpayPostBuyHook(PostBuyHook):
    """
    A general use post buy hook that is automatically added to any card
    in the supply which can be overpaid for.

    This hook handles asking the player whether they would like to overpay,
    as well as calling the `overpay` method of the card they purchased.
    """
    persistent = True

    def __call__(self, player: Player, purchased_card: Card):
        # `player` is the player who bought the card
        # Check if the player has enough coppers left this turn to overpay
        if player.turn.coppers_remaining == 0:
            return
        # Ask the player if they would like to overpay
        player_description = format_pronouns(purchased_card.overpay_description, GrammaticalPerson.SECOND_PERSON)
        prompt = f"You bought a {purchased_card} and may overpay for it in order to{player_description} By how much would you like to overpay?"
        amount_overpaid = player.interactions.choose_from_range(prompt, minimum=1, maximum=player.turn.coppers_remaining, force=False)
        if amount_overpaid is None or amount_overpaid == 0:
            return
        # Subtract the amount overpaid from the remaining coppers this turn
        self.game.current_turn.coppers_remaining -= amount_overpaid
        broadcast_description = format_pronouns(purchased_card.overpay_description, GrammaticalPerson.THIRD_PERSON)
        self.game.broadcast(f"{player} overpaid for their {purchased_card} by {amount_overpaid} $ and may{broadcast_description}")
        # Call the `overpay` method of the purchased card
        purchased_card.overpay(amount_overpaid)


class GuildsExpansion(Expansion):
    name = "Guilds"

    def __init__(self, game):
        super().__init__(game)
        self.coffers_cache = None

    @property
    def basic_card_piles(self) -> List[Tuple[Type[Card], int]]:
        return []

    @property
    def kingdom_card_classes(self) -> List[Type[Card]]:
       return guilds_cards.KINGDOM_CARDS

    @property
    def game_end_conditions(self) -> List[Callable[[], Tuple[bool, Optional[str]]]]:
        return []

    def additional_setup(self):
        # Each player starts off with no coffers
        player: Player
        for player in self.game.players:
            player.coffers: int = 0
        # If the Baker is in the Supply, each player gets +1 Coffers
        if guilds_cards.Baker in self.supply.card_stacks:
            self.game.broadcast("The Baker is in the Supply so each player gets +1 Coffers.")
            for player in self.game.players:
                player.coffers += 1
        # Add an `OverpayPostBuyHook` to any card in the supply that can be overpaid for.
        overpay_post_buy_hook = OverpayPostBuyHook(self.game)
        for card_class in self.supply.card_stacks:
            if card_class.can_overpay:
                self.game.add_post_buy_hook(overpay_post_buy_hook, card_class)

    def heartbeat(self):
        pass

    def scoring(self, player: Player) -> int:
        return 0

    def additional_pre_buy_phase_actions(self):
        # TODO: Ask the player whether they would like to use any coffers
        player = self.game.current_turn.player
        if player.coffers > 0:
            prompt = f"You have {player.coffers} Coffers. How many would you like to use for this Buy phase?"
            coffers_to_use = player.interactions.choose_from_range(prompt, minimum=1, maximum=player.coffers, force=False)
            if coffers_to_use is None:
                return
            elif coffers_to_use > 0:
                self.game.broadcast(f"{player} used {s(coffers_to_use, 'Coffer')}.")
                self.game.current_turn.plus_coppers(coffers_to_use)
                player.coffers -= coffers_to_use
