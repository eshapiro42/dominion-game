from collections import defaultdict
from enum import StrEnum

from .game import Game
from .interactions import BrowserInteraction
from .player import Player


class DataSource(StrEnum):
    HAND = "hand"
    DISCARD_PILE = "discard pile"
    PLAYERS_INFO = "players info"
    CURRENT_TURN_INFO = "current turn info"
    PLAYED_CARDS = "played cards"
    SUPPLY = "supply"
    TRASH = "trash"


class HeartBeatCache:
    def __init__(self):
        self.individual = defaultdict(lambda: defaultdict(list))
        self.communal = defaultdict(list)


class HeartBeat:
    def __init__(self, game: Game):
        self.game = game
        self.cache = HeartBeatCache()
        self.run = True
        self.beats_per_second = 5 # Must be an integer
        self.message_interval = 60 # In seconds
        self.sleep_time = 1 / self.beats_per_second
        self.message_frequency = self.beats_per_second * self.message_interval

    def get_individual_json(self, player: Player, source: DataSource):
        match source:
            case DataSource.HAND:
                return {
                    "cards": [card.json for card in player.hand],
                }
            case DataSource.DISCARD_PILE:
                return {
                    "cards": [card.json for card in player.discard_pile],
                }

    def get_communal_json(self, source: DataSource):
        match source:
            case DataSource.PLAYERS_INFO:
                if hasattr(self.game, "turn_order"):
                    return [player.json for player in self.game.turn_order]
                else:
                    return None
            case DataSource.CURRENT_TURN_INFO:
                return self.game.current_turn.json
            case DataSource.PLAYED_CARDS:
                return {
                    "cards": [card.json for card in self.game.current_turn.player.played_cards],
                }
            case DataSource.SUPPLY:
                return {
                    "cards": [card_stack.json for card_stack in self.game.supply.card_stacks.values()],
                }
            case DataSource.TRASH:
                return {
                    "cards": self.game.supply.trash_pile_json,
                }

    def send_individual_json(self, player: Player, source: DataSource):
        if (source_json := self.get_individual_json(player, source)) is None:
            return
        if source_json != self.cache.individual[player][source]:
            self.cache.individual[player][source] = source_json
            try:
                self.game.socketio.emit(
                    f"display {source}",
                    source_json,
                    to=player.sid,
                )
            except Exception as exception:
                print(exception)

    def send_communal_json(self, source: DataSource):
        if (source_json := self.get_communal_json(source)) is None:
            return
        if source_json != self.cache.communal[source]:
            self.cache.communal[source] = source_json
            try:
                self.game.socketio.emit(
                    f"display {source}",
                    source_json,
                    to=self.game.room,
                )
            except Exception as exception:
                raise

    def beat(self):
        counter = 0
        while self.run:
            self.game.socketio.sleep(self.sleep_time)
            if counter == self.message_frequency:
                counter = 0
                print(f"<3 Game {self.game.room} heartbeat <3")
            if not self.game.started or self.game.current_turn is None:
                continue
            try:
                # Each player sees their individual data
                for player in self.game.players:
                    if isinstance(player.interactions, BrowserInteraction):
                        for source in DataSource:
                            self.send_individual_json(player, source)
                # All players see communal data
                for source in DataSource:
                    self.send_communal_json(source)
                # Send expansion-specific info
                for expansion in self.game.supply.customization.expansions:
                    expansion.heartbeat()
            except Exception as exception:
                raise
            counter += 1

    def stop(self):
        self.run = False



