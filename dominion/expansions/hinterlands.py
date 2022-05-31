from __future__ import annotations

import random

from typing import TYPE_CHECKING, Type

from .expansion import Expansion
from ..cards import cards, base_cards, hinterlands_cards
from ..grammar import s, it_or_them
from ..supply import FiniteSupplyStack

if TYPE_CHECKING:
    from ..cards.cards import Card


class HinterlandsExpansion(Expansion):
    name = 'Hinterlands'

    @property
    def basic_card_piles(self):
        return []

    @property
    def kingdom_card_classes(self):
        return hinterlands_cards.KINGDOM_CARDS

    def additional_setup(self):
        # If the Duchess is in the Supply, add its post-gain hook to the Duchy
        if hinterlands_cards.Duchess in self.supply.card_stacks:
            post_gain_hook = hinterlands_cards.Duchess.DuchessPostGainHook(self.game, base_cards.Duchy)
            self.supply.add_post_gain_hook(post_gain_hook, base_cards.Duchy)
        # If the Fool's Gold is in the Supply, add its post-gain hook to the Province
        if hinterlands_cards.FoolsGold in self.supply.card_stacks:
            post_gain_hook = hinterlands_cards.FoolsGold.FoolsGoldPostGainHook(self.game, base_cards.Province)
            self.supply.add_post_gain_hook(post_gain_hook, base_cards.Province)
        # If the Tunnel is in the Supply, add its post-discard hook
        if hinterlands_cards.Tunnel in self.supply.card_stacks:
            post_discard_hook = hinterlands_cards.Tunnel.TunnelPostDiscardHook(self.game)
            self.game.add_post_discard_hook(post_discard_hook, hinterlands_cards.Tunnel)
        # If the Noble Brigand is in the Supply, add its post-buy hook
        if hinterlands_cards.NobleBrigand in self.supply.card_stacks:
            post_buy_hook = hinterlands_cards.NobleBrigand.NobleBrigandPostBuyHook(self.game)
            self.game.add_post_buy_hook(post_buy_hook, hinterlands_cards.NobleBrigand)
        # If the Cache is in the Supply, add its post-gain hook
        if hinterlands_cards.Cache in self.supply.card_stacks:
            post_gain_hook = hinterlands_cards.Cache.CachePostGainHook(self.game, hinterlands_cards.Cache)
            self.supply.add_post_gain_hook(post_gain_hook, hinterlands_cards.Cache)
        # If the Embassy is in the Supply, add its post-gain hook
        if hinterlands_cards.Embassy in self.supply.card_stacks:
            post_gain_hook = hinterlands_cards.Embassy.EmbassyPostGainHook(self.game, hinterlands_cards.Embassy)
            self.supply.add_post_gain_hook(post_gain_hook, hinterlands_cards.Embassy)
        # If the Haggler is in the Supply, add its post-buy hook to all cards in the Supply
        if hinterlands_cards.Haggler in self.supply.card_stacks:
            post_buy_hook = hinterlands_cards.Haggler.HagglerPostBuyHook(self.game)
            for card_stack in self.supply.card_stacks:
                self.game.add_post_buy_hook(post_buy_hook, card_stack)
        # If the Ill-Gotten Gains is in the Supply, add its post-gain hook
        if hinterlands_cards.IllGottenGains in self.supply.card_stacks:
            post_gain_hook = hinterlands_cards.IllGottenGains.IllGottenGainsPostGainHook(self.game, hinterlands_cards.IllGottenGains)
            self.supply.add_post_gain_hook(post_gain_hook, hinterlands_cards.IllGottenGains)
        # If the Inn is in the Supply, add its post-gain hook
        if hinterlands_cards.Inn in self.supply.card_stacks:
            post_gain_hook = hinterlands_cards.Inn.InnPostGainHook(self.game, hinterlands_cards.Inn)
            self.supply.add_post_gain_hook(post_gain_hook, hinterlands_cards.Inn)

    def heartbeat(self):
        pass
            
    @property
    def game_end_conditions(self):
        return []

    def scoring(self, player):
        return 0