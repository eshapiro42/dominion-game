from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .player import Player
    from .game import Game


@dataclass
class GameLogEntry:
    game_log: GameLog
    message: str
    scope: List[Player] | None = None
    parent: GameLogEntry | None = None
    timestamp: datetime = field(init=False)
    children: List[GameLogEntry] = field(default_factory=list)

    def __post_init__(self):
        # Set timestamp
        self.timestamp = datetime.now()

    def __str__(self) -> str:
        indent = "    " * self.depth
        return f"{indent}{self.timestamp}: {self.message}"

    # def add_child(self, child: GameLogEntry) -> GameLogEntry:
    #     self.children.append(child)
    #     return child
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "message": self.message,
            "depth": self.depth,
            "timestamp": self.timestamp.isoformat(),
        }

    @property
    def depth(self) -> int:
        current_depth = 0
        current_parent = self.parent
        while current_parent is not None:
            current_depth += 1
            current_parent = current_parent.parent
        return current_depth


class GameLog:
    def __init__(self, game: Game):
        self.root_entries: List[GameLogEntry] = []
        self.most_recent_entry: GameLogEntry | None = None
        self.game = game

    def add_entry(self, message: str, parent: GameLogEntry | None = None, scope: List[Player] | None = None) -> GameLogEntry:
        entry = GameLogEntry(self, message, scope, parent)
        self.most_recent_entry = entry
        if parent is None:
            self.root_entries.append(entry)
        else:
            parent.children.append(entry)
        self.game.socketio.emit("new log entry", entry.serialize(), room=self.game.room)
        print(entry)
        return entry
    
    def add_context_aware_subentry(self, message: str, scope: List[Player] | None = None) -> GameLogEntry:
        return self.add_entry(message, scope, self.most_recent_entry)
    
    def __str__(self) -> str:
        def traverse(entry: GameLogEntry, depth: int) -> str:
            indent = "    " * depth
            result = f"{indent}{entry.timestamp}: {entry.message}"
            for child in entry.children:
                result += "\n" + traverse(child, depth + 1)
            return result

        log_str = ""
        for entry in self.root_entries:
            log_str += traverse(entry, 0) + "\n"
        return log_str.strip()