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
        if player.turn.coppers_remaining == 0:
            return
        player_description = format_pronouns(purchased_card.overpay_description, GrammaticalPerson.SECOND_PERSON)
        prompt = f"You bought a {purchased_card} and may overpay for it in order to{player_description} By how much would you like to overpay?"
        amount_overpaid = player.interactions.choose_from_range(prompt, minimum=1, maximum=player.turn.coppers_remaining, force=False)
        if amount_overpaid is None or amount_overpaid == 0:
            return
        broadcast_description = format_pronouns(purchased_card.overpay_description, GrammaticalPerson.THIRD_PERSON)
        self.game.broadcast(f"{player} overpaid for their {purchased_card} by {amount_overpaid} $ and may{broadcast_description}")
        purchased_card.overpay(amount_overpaid)


class GuildsExpansion(Expansion):
    name = "Guilds"

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
            # TODO: Set this to 0
            player.coffers: int = 2
        # Add an `OverpayPostBuyHook` to any card in the supply that can be overpaid for.
        overpay_post_buy_hook = OverpayPostBuyHook(self.game)
        for card_class in self.supply.card_stacks:
            if card_class.can_overpay:
                self.game.add_post_buy_hook(overpay_post_buy_hook, card_class)


    def heartbeat(self):
        # Send coffers info for each player
        self.game.socketio.emit(
            "coffers",
            {
                "coffers": [player.coffers for player in self.game.players],
            },
            room=self.game.room
        )

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
