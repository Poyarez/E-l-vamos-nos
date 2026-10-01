"""Estado completo de uma partida: herói, posição, relógio e a memória do mundo.

É exatamente isto que vai para o arquivo de save (ver ``rpg.save_system``).
"""

from __future__ import annotations

import random
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Mapping, Optional, Set, Tuple

from . import world
from .data.monsters import MONSTERS
from .data.quests import BOUNTIES, QUESTS
from .player import Player
from .time_system import GameClock

Coord = Tuple[int, int]

START_MAP = "vale_primordia"


@dataclass
class JournalEntry:
    """Uma anotação no diário: pistas, rumores e segredos descobertos."""

    id: str
    title: str
    text: str
    day: int
    category: str = "pista"


class GameState:
    def __init__(self, player: Player, map_id: str, x: int, y: int, clock: GameClock,
                 save_id: Optional[str] = None, created_at: Optional[str] = None) -> None:
        self.player = player
        self.map_id = map_id
        self.x = x
        self.y = y
        self.clock = clock
        self.save_id = save_id or uuid.uuid4().hex[:8]
        self.created_at = created_at or datetime.now().isoformat(timespec="seconds")
        self.explored: Dict[str, Set[Coord]] = {}
        self.discovered: Set[str] = set()      # ids de locais notáveis visitados
        self.regions: Set[str] = set()         # ids de regiões visitadas
        self.flags: Dict[str, Any] = {}        # marcos de história, segredos, escolhas
        self.journal: List[JournalEntry] = []
        self.met: Set[str] = set()             # NPCs com quem já conversou
        self.bestiary: Dict[str, Dict[str, Any]] = {}   # criatura -> abates, fatos e saques conhecidos
        self.nodes: Dict[str, Dict[str, int]] = {}      # "local:ponto" -> o que resta e desde quando (coleta)
        self.quests: Dict[str, Dict[str, Any]] = {}     # missão -> etapa, contagem de abates, concluída?
        self.bounties: Dict[str, Any] = {}              # quadro de avisos: dia, ofertas, aceitas e feitas
        self.stats: Dict[str, int] = {"passos": 0}
        self.play_seconds = 0.0

    @classmethod
    def new(cls, player: Player, seed: Optional[int] = None) -> "GameState":
        start = world.get_map(START_MAP).start
        clock = GameClock(seed=random.randrange(1, 1_000_000) if seed is None else seed)
        return cls(player, START_MAP, start[0], start[1], clock)

    # ------------------------------------------------------------------ consultas

    @property
    def pos(self) -> Coord:
        return (self.x, self.y)

    def explored_on(self, map_id: str) -> Set[Coord]:
        return self.explored.setdefault(map_id, set())

    def has_flag(self, flag: str) -> bool:
        return bool(self.flags.get(flag))

    def bestiary_entry(self, template_id: str) -> Dict[str, Any]:
        return self.bestiary.setdefault(template_id, {"kills": 0, "facts": [], "loot": []})

    def knowledge(self) -> Dict[str, Set[str]]:
        """O que se sabe de cada criatura (fraquezas, resistências...), para o motor de combate."""
        return {template_id: set(entry.get("facts", [])) for template_id, entry in self.bestiary.items()}

    def learn(self, knowledge: Mapping[str, Set[str]]) -> None:
        for template_id, facts in knowledge.items():
            entry = self.bestiary_entry(template_id)
            entry["facts"] = sorted(set(entry["facts"]) | set(facts))

    def record_kill(self, template_id: str, loot: List[str]) -> None:
        entry = self.bestiary_entry(template_id)
        entry["kills"] += 1
        entry["loot"] = sorted(set(entry["loot"]) | set(loot))

    def add_journal(self, entry_id: str, title: str, text: str, category: str = "pista") -> bool:
        """Anota no diário. Devolve ``False`` se a anotação já existia."""
        if any(entry.id == entry_id for entry in self.journal):
            return False
        self.journal.append(JournalEntry(entry_id, title, text, self.clock.day, category))
        return True

    # ------------------------------------------------------------------ persistência

    def to_dict(self) -> Dict[str, Any]:
        explored = {}
        for map_id, tiles in self.explored.items():
            if map_id in world.map_ids() and tiles:
                game_map = world.get_map(map_id)
                explored[map_id] = ["".join("1" if (x, y) in tiles else "0" for x in range(game_map.width))
                                    for y in range(game_map.height)]
        return {
            "save_id": self.save_id,
            "created_at": self.created_at,
            "player": self.player.to_dict(),
            "location": {"map": self.map_id, "x": self.x, "y": self.y},
            "clock": self.clock.to_dict(),
            "explored": explored,
            "discovered": sorted(self.discovered),
            "regions": sorted(self.regions),
            "flags": dict(self.flags),
            "journal": [asdict(entry) for entry in self.journal],
            "met": sorted(self.met),
            "bestiary": {template_id: dict(entry) for template_id, entry in self.bestiary.items()},
            "nodes": {key: dict(entry) for key, entry in self.nodes.items()},
            "quests": {quest_id: dict(entry) for quest_id, entry in self.quests.items()},
            "bounties": {"day": self.bounties.get("day"), "offers": list(self.bounties.get("offers", [])),
                         "done": list(self.bounties.get("done", [])),
                         "active": {key: dict(value) for key, value in self.bounties.get("active", {}).items()}},
            "stats": dict(self.stats),
            "play_seconds": round(self.play_seconds, 1),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "GameState":
        location = data.get("location", {})
        map_id, x, y = location.get("map", START_MAP), int(location.get("x", -1)), int(location.get("y", -1))
        # se o mapa ou o tile deixaram de existir numa atualização, volta ao início do vale
        if map_id not in world.map_ids() or not world.get_map(map_id).passable(x, y):
            map_id = START_MAP
            x, y = world.get_map(START_MAP).start
        state = cls(
            player=Player.from_dict(data["player"]),
            map_id=map_id, x=x, y=y,
            clock=GameClock.from_dict(data.get("clock", {})),
            save_id=data.get("save_id"),
            created_at=data.get("created_at"),
        )
        for saved_map, rows in data.get("explored", {}).items():
            state.explored[saved_map] = {(col, row) for row, line in enumerate(rows)
                                         for col, char in enumerate(line) if char == "1"}
        state.discovered = set(data.get("discovered", []))
        state.regions = set(data.get("regions", []))
        state.flags = dict(data.get("flags", {}))
        state.journal = [JournalEntry(**entry) for entry in data.get("journal", [])]
        state.met = set(data.get("met", []))
        state.bestiary = {template_id: {"kills": int(entry.get("kills", 0)), "facts": list(entry.get("facts", [])),
                                        "loot": list(entry.get("loot", []))}
                          for template_id, entry in data.get("bestiary", {}).items() if template_id in MONSTERS}
        state.nodes = {key: {"left": int(entry.get("left", 0)), "time": int(entry.get("time", 0))}
                       for key, entry in data.get("nodes", {}).items()}
        state.quests = {quest_id: {"stage": int(entry.get("stage", 0)), "kills": int(entry.get("kills", 0)),
                                   "done": bool(entry.get("done", False)), "day": int(entry.get("day", 1))}
                        for quest_id, entry in data.get("quests", {}).items() if quest_id in QUESTS}
        saved_board = data.get("bounties") or {}
        state.bounties = {"day": saved_board.get("day"),
                          "offers": [b for b in saved_board.get("offers", []) if b in BOUNTIES],
                          "done": [b for b in saved_board.get("done", []) if b in BOUNTIES],
                          "active": {b: {"kills": int(v.get("kills", 0))}
                                     for b, v in saved_board.get("active", {}).items() if b in BOUNTIES}}
        state.stats.update({key: int(value) for key, value in data.get("stats", {}).items()})
        state.play_seconds = float(data.get("play_seconds", 0.0))
        return state
