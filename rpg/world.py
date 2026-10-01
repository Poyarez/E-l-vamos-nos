"""Mundo: mapas em grade de coordenadas, terrenos, regiões, locais notáveis e passagens.

Coordenadas são ``(x, y)``: ``x`` cresce para o leste e ``y`` para o sul, como nas
linhas do desenho do mapa. O movimento é em 8 direções, mas não é possível "cortar
quinas" entre dois tiles intransponíveis (atravessar um rio pela diagonal, por exemplo).
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterator, List, Mapping, Optional, Tuple

from .data.maps import MAPS
from .data.terrain import TERRAIN

Coord = Tuple[int, int]

#: id -> (dx, dy, nome). A ordem é a da rosa dos ventos, em sentido horário.
DIRECTIONS: Dict[str, Tuple[int, int, str]] = {
    "n": (0, -1, "Norte"),
    "ne": (1, -1, "Nordeste"),
    "l": (1, 0, "Leste"),
    "se": (1, 1, "Sudeste"),
    "s": (0, 1, "Sul"),
    "so": (-1, 1, "Sudoeste"),
    "o": (-1, 0, "Oeste"),
    "no": (-1, -1, "Noroeste"),
}

DIRECTION_ALIASES = {
    "norte": "n", "nordeste": "ne", "leste": "l", "sudeste": "se",
    "sul": "s", "sudoeste": "so", "oeste": "o", "noroeste": "no",
    # atalhos em inglês, para quem tem o hábito
    "e": "l", "w": "o", "nw": "no", "sw": "so", "north": "n", "south": "s", "east": "l", "west": "o",
}


def parse_direction(word: str) -> Optional[str]:
    """Converte "norte", "N", "nordeste", "w"... no id de direção (ou ``None``)."""
    if word in DIRECTIONS:
        return word
    return DIRECTION_ALIASES.get(word)


def direction_between(origin: Coord, target: Coord) -> Optional[str]:
    """Direção aproximada (8 pontos) de ``origin`` para ``target``; ``None`` se forem iguais."""
    dx, dy = target[0] - origin[0], target[1] - origin[1]
    if dx == 0 and dy == 0:
        return None
    if abs(dx) > 2 * abs(dy):
        dy = 0
    elif abs(dy) > 2 * abs(dx):
        dx = 0
    step = ((dx > 0) - (dx < 0), (dy > 0) - (dy < 0))
    for key, (ddx, ddy, _name) in DIRECTIONS.items():
        if (ddx, ddy) == step:
            return key
    return None  # pragma: no cover - todas as combinações estão no dicionário


@dataclass(frozen=True)
class Terrain:
    id: str
    name: str
    color: str
    passable: bool
    cost: int
    vision: int
    day: Tuple[str, ...]
    night: Tuple[str, ...]

    @classmethod
    def from_data(cls, terrain_id: str, data: Mapping[str, Any]) -> "Terrain":
        return cls(terrain_id, data["name"], data["color"], data["passable"], data["cost"],
                   data.get("vision", 0), tuple(data["day"]), tuple(data.get("night", data["day"])))


@dataclass
class Region:
    """Sub-zona nomeada (como as do WoW). Entrar pela primeira vez rende experiência."""

    id: str
    name: str
    rects: Tuple[Tuple[int, int, int, int], ...]
    intro: str = ""
    day: Tuple[str, ...] = ()
    night: Tuple[str, ...] = ()
    xp: int = 30
    encounters: Optional[Dict[str, Any]] = None   # monstros que podem aparecer (ver rpg.monsters)

    def contains(self, x: int, y: int) -> bool:
        return any(x1 <= x <= x2 and y1 <= y <= y2 for x1, y1, x2, y2 in self.rects)


@dataclass
class Landmark:
    """Local notável em uma coordenada: descrição própria, exame detalhado e segredos."""

    id: str
    name: str
    x: int
    y: int
    description: str
    night: str = ""                  # descrição alternativa à noite
    examine: str = ""                # texto do comando "examinar"
    xp: int = 25                     # experiência ao descobrir
    hint: str = ""                   # percebido nos arredores enquanto não descoberto
    hidden: bool = False             # não aparece como "?" no mapa antes da descoberta
    reveal: int = 0                  # raio do mapa revelado ao descobrir (mirantes)
    rest: bool = False               # é possível dormir aqui
    resources: Tuple[Dict[str, Any], ...] = ()   # pontos de coleta
    secret: Optional[Dict[str, Any]] = None      # revelado ao examinar
    loot: Optional[Dict[str, Any]] = None        # recompensa única ao examinar
    encounter: Optional[Dict[str, Any]] = None   # luta fixa ao se aproximar (até ser vencida)

    @property
    def pos(self) -> Coord:
        return (self.x, self.y)


@dataclass
class Portal:
    """Passagem para outro mapa: pela borda (``direction``) ou por comando (``verb``)."""

    id: str
    x: int
    y: int
    label: str
    target: Optional[Tuple[str, int, int]] = None   # (mapa, x, y)
    direction: Optional[str] = None
    verb: Optional[str] = None                      # "entrar" ou "sair"
    locked: bool = False                            # bloqueada (até que ``unlock_flag`` seja ativada)
    unlock_flag: Optional[str] = None               # flag que desbloqueia a passagem
    min_level: int = 0                              # nível mínimo para atravessar
    locked_text: str = ""                           # mensagem quando bloqueada
    requires_flag: Optional[str] = None             # a passagem só existe com esta flag
    travel_text: str = ""

    def is_known(self, flags: Mapping[str, Any]) -> bool:
        return self.requires_flag is None or bool(flags.get(self.requires_flag))

    def is_locked(self, flags: Mapping[str, Any], level: int = 1) -> bool:
        if self.unlock_flag:
            if not flags.get(self.unlock_flag):
                return True
        elif self.locked:
            return True
        return level < self.min_level


class GameMap:
    """Um mapa jogável construído a partir de um dicionário de ``rpg.data.maps``."""

    def __init__(self, data: Mapping[str, Any]) -> None:
        self.id: str = data["id"]
        self.name: str = data["name"]
        self.outdoor: bool = data.get("outdoor", True)
        self.light: int = data.get("light", 3)          # raio de visão em mapas fechados
        self.intro: str = data.get("intro", "")
        self.rows: List[str] = data["layout"].strip("\n").split("\n")
        self.height = len(self.rows)
        self.width = len(self.rows[0])
        if any(len(row) != self.width for row in self.rows):
            raise ValueError(f"Mapa {self.id}: todas as linhas do desenho precisam ter a mesma largura")
        self.legend: Dict[str, Terrain] = {
            char: Terrain.from_data(terrain_id, TERRAIN[terrain_id]) for char, terrain_id in data["legend"].items()
        }
        unknown = {char for row in self.rows for char in row} - set(self.legend)
        if unknown:
            raise ValueError(f"Mapa {self.id}: caracteres sem legenda: {sorted(unknown)}")
        self.start: Coord = tuple(data["start"])  # type: ignore[assignment]
        self.regions = [Region(r["id"], r["name"], tuple(tuple(rect) for rect in r["rects"]), r.get("intro", ""),
                               tuple(r.get("day", ())), tuple(r.get("night", ())), r.get("xp", 30),
                               r.get("encounters"))
                        for r in data.get("regions", [])]
        self.landmarks: Dict[str, Landmark] = {}
        for entry in data.get("landmarks", []):
            landmark = Landmark(**{**entry, "resources": tuple(entry.get("resources", ()))})
            self.landmarks[landmark.id] = landmark
        self._landmark_at: Dict[Coord, Landmark] = {lm.pos: lm for lm in self.landmarks.values()}
        self.portals = [Portal(**{**entry, "target": tuple(entry["target"]) if entry.get("target") else None})
                        for entry in data.get("portals", [])]
        self.passable_tiles = sum(1 for y in range(self.height) for x in range(self.width) if self.passable(x, y))

    # ------------------------------------------------------------------ consultas

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def char_at(self, x: int, y: int) -> str:
        return self.rows[y][x]

    def terrain_at(self, x: int, y: int) -> Terrain:
        return self.legend[self.rows[y][x]]

    def passable(self, x: int, y: int) -> bool:
        return self.in_bounds(x, y) and self.terrain_at(x, y).passable

    def can_step(self, x: int, y: int, dx: int, dy: int) -> bool:
        """Pode andar de (x, y) para (x+dx, y+dy)? Diagonais não cortam quinas bloqueadas."""
        if not self.passable(x + dx, y + dy):
            return False
        if dx and dy:
            return self.passable(x + dx, y) and self.passable(x, y + dy)
        return True

    def landmark_at(self, x: int, y: int) -> Optional[Landmark]:
        return self._landmark_at.get((x, y))

    def region_at(self, x: int, y: int) -> Optional[Region]:
        for region in self.regions:
            if region.contains(x, y):
                return region
        return None

    def portals_at(self, x: int, y: int) -> List[Portal]:
        return [portal for portal in self.portals if (portal.x, portal.y) == (x, y)]

    def tiles_in_radius(self, x: int, y: int, radius: int) -> Iterator[Coord]:
        """Tiles dentro de um círculo (levemente "gordo", para parecer redondo na grade)."""
        limit = radius * radius + radius
        for ty in range(y - radius, y + radius + 1):
            for tx in range(x - radius, x + radius + 1):
                if self.in_bounds(tx, ty) and (tx - x) ** 2 + (ty - y) ** 2 <= limit:
                    yield tx, ty

    def find_path(self, start: Coord, goal: Coord,
                  allowed: Optional[Callable[[int, int], bool]] = None) -> Optional[List[Coord]]:
        """Caminho mais rápido (em minutos de jogo) de ``start`` até ``goal``, sem incluir ``start``.

        ``allowed`` restringe os tiles utilizáveis (ex.: apenas os já explorados).
        """
        if start == goal:
            return []
        best: Dict[Coord, float] = {start: 0.0}
        came_from: Dict[Coord, Coord] = {}
        queue: List[Tuple[float, Coord]] = [(0.0, start)]
        while queue:
            cost, (x, y) = heapq.heappop(queue)
            if (x, y) == goal:
                break
            if cost > best[(x, y)]:
                continue
            for dx, dy, _name in DIRECTIONS.values():
                nx, ny = x + dx, y + dy
                if not self.can_step(x, y, dx, dy):
                    continue
                if allowed is not None and (nx, ny) != goal and not allowed(nx, ny):
                    continue
                # diagonais custam um tiquinho a mais para preferir linhas retas
                new_cost = cost + self.terrain_at(nx, ny).cost + (0.01 if dx and dy else 0.0)
                if new_cost < best.get((nx, ny), float("inf")):
                    best[(nx, ny)] = new_cost
                    came_from[(nx, ny)] = (x, y)
                    heapq.heappush(queue, (new_cost, (nx, ny)))
        if goal not in came_from:
            return None
        path = [goal]
        while path[-1] in came_from and came_from[path[-1]] != start:
            path.append(came_from[path[-1]])
        path.reverse()
        return path


_loaded: Dict[str, GameMap] = {}


def get_map(map_id: str) -> GameMap:
    """Fábrica de mapas (com cache): constrói o ``GameMap`` a partir dos dados na primeira vez."""
    if map_id not in _loaded:
        if map_id not in MAPS:
            raise KeyError(f"Mapa desconhecido: {map_id!r}")
        _loaded[map_id] = GameMap(MAPS[map_id])
    return _loaded[map_id]


def map_ids() -> List[str]:
    return list(MAPS)


def find_landmark(landmark_id: str) -> Optional[Tuple[GameMap, Landmark]]:
    for map_id in MAPS:
        game_map = get_map(map_id)
        if landmark_id in game_map.landmarks:
            return game_map, game_map.landmarks[landmark_id]
    return None
