"""Coleta e ofícios no estilo Old School RuneScape: as regras das seis perícias.

* **Coleta** (Mineração, Pesca e as ervas e fibras da Alquimia e da Alfaiataria): cada
  tentativa gasta minutos de jogo e acerta com uma chance que cresce com o nível e com a
  ferramenta. Os pontos se esgotam e se recuperam aos poucos; às vezes sai um achado raro.
* **Produção** (Metalurgia, Culinária, Alfaiataria e Alquimia): receitas liberadas por
  nível, feitas numa estação (fornalha, bigorna, fogo, roca, caldeirão) e/ou com uma
  ferramenta. Comida pode queimar e o ferro impuro pode se perder — cada vez menos,
  conforme o nível sobe.

A experiência dos dados está em unidades do OSRS; ``SKILL_XP_RATE`` acelera o ritmo para
um jogo de texto, como o ``XP_RATE`` do combate. O módulo não lê o teclado nem desenha:
a sessão (``rpg.session``) aplica o tempo e as mensagens; os comandos ficam em
``rpg.commands``.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Mapping, Optional, Tuple

from . import world
from .conditions import conditions_met
from .data.gathering import GATHER_VERBS, NODES
from .data.recipes import BURNT_ITEM, RECIPES, STATIONS
from .data.skills import SKILLS
from .items import ItemStack, get_item, item_name

if TYPE_CHECKING:
    from .player import Player
    from .state import GameState

SKILL_XP_RATE = 3
LEVEL_BONUS = 0.012          # chance de coleta a mais por nível acima do mínimo
MIN_CHANCE, MAX_CHANCE = 0.05, 0.95
ATTEMPTS_PER_ITEM = 6        # uma sessão de coleta desiste depois de tantas tentativas por item pedido
MAX_SESSION_MINUTES = 240    # e ninguém trabalha mais de 4 horas seguidas
DEFAULT_GATHER = 5           # itens por sessão de coleta quando o jogador não diz quantos
ALL = 999                    # "tudo": até o ponto se esgotar ou a mochila encher

TOOL_NAMES = {
    "picareta": "uma picareta", "rede": "uma rede de pesca", "vara": "uma vara de pesca",
    "martelo": "um martelo de ferreiro", "agulha": "agulha e linha", "tesoura": "uma tesoura de tosquia",
    "almofariz": "um almofariz",
}


def skill_xp(base: float) -> int:
    """Experiência de uma ação (dados em unidades do OSRS)."""
    return int(round(base * SKILL_XP_RATE))


def skill_name(skill_id: str) -> str:
    return SKILLS[skill_id]["name"]


def best_tool(player: "Player", kind: str) -> Optional[ItemStack]:
    """A melhor ferramenta de um tipo na mochila (a de maior ``power``)."""
    tools = [stack for stack in player.inventory if stack.data.get("tool") == kind]
    return max(tools, key=lambda stack: stack.data.get("power", 0.0)) if tools else None


def scaled_chance(spec: Optional[List[float]], required: int, level: int) -> float:
    """``[chance, nível]``: a chance no nível mínimo cai em linha reta até zero no nível dado."""
    if not spec:
        return 0.0
    start, stop = spec
    if level >= stop:
        return 0.0
    return start * (stop - level) / max(1, stop - required)


# --------------------------------------------------------------------------- pontos de coleta

@dataclass
class Spot:
    """Um ponto de coleta num local do mapa."""

    landmark: world.Landmark
    entry: Mapping[str, Any]

    @property
    def node_id(self) -> str:
        return self.entry["node"]

    @property
    def data(self) -> Dict[str, Any]:
        return NODES[self.node_id]

    @property
    def key(self) -> str:
        return f"{self.landmark.id}:{self.node_id}"

    @property
    def name(self) -> str:
        return self.data["name"]


def spots_at(landmark: Optional[world.Landmark], state: "GameState",
             skills: Optional[Iterable[str]] = None) -> List[Spot]:
    """Pontos de coleta visíveis num local (os revelados por segredos só depois do segredo)."""
    if landmark is None:
        return []
    wanted = set(skills) if skills else None
    spots = [Spot(landmark, entry) for entry in landmark.resources if conditions_met(entry.get("if"), state)]
    return [spot for spot in spots if wanted is None or spot.data["skill"] in wanted]


def node_open(spot: Spot, state: "GameState") -> bool:
    """O ponto pode ser usado agora? (Ex.: lírios-da-lua só à noite.)"""
    return conditions_met(spot.data.get("if"), state)


def _per_unit(data: Mapping[str, Any]) -> int:
    return max(1, data["respawn"] // data["amount"])


def node_left(state: "GameState", spot: Spot) -> int:
    """Quanto o ponto ainda rende agora, contando a recuperação desde a última coleta."""
    data, now = spot.data, state.clock.minutes
    entry = state.nodes.get(spot.key)
    if entry is None:
        return data["amount"]
    per_unit = _per_unit(data)
    units = max(0, now - entry["time"]) // per_unit
    left = min(data["amount"], entry["left"] + units)
    if left >= data["amount"]:
        del state.nodes[spot.key]
    elif units:
        entry["left"], entry["time"] = left, entry["time"] + units * per_unit
    return left


def minutes_to_refill(state: "GameState", spot: Spot) -> int:
    """Minutos até o ponto esgotado render de novo."""
    entry = state.nodes.get(spot.key)
    if entry is None or node_left(state, spot) > 0:
        return 0
    return max(1, entry["time"] + _per_unit(spot.data) - state.clock.minutes)


def _take_from_node(state: "GameState", spot: Spot) -> None:
    left = node_left(state, spot)
    entry = state.nodes.setdefault(spot.key, {"left": left, "time": state.clock.minutes})
    entry["left"] = left - 1


def gather_chance(player: "Player", data: Mapping[str, Any]) -> float:
    level = player.skills.level(data["skill"])
    tool = best_tool(player, data["tool"]) if data.get("tool") else None
    chance = data["chance"] + LEVEL_BONUS * (level - data["level"]) + (tool.data.get("power", 0.0) if tool else 0.0)
    return max(MIN_CHANCE, min(MAX_CHANCE, chance))


def gather_problem(player: "Player", state: "GameState", spot: Spot) -> Optional[str]:
    """Por que não dá para coletar aqui agora (``None`` se dá)."""
    data = spot.data
    level = player.skills.level(data["skill"])
    verb = GATHER_VERBS.get(data["skill"], "coletar")
    if level < data["level"]:
        return (f"Você precisa de {skill_name(data['skill'])} {data['level']} para {verb} {data['name']} "
                f"(seu nível: {level}).")
    if data.get("tool") and best_tool(player, data["tool"]) is None:
        return f"Você precisa de {TOOL_NAMES[data['tool']]} para {verb} aqui."
    if data.get("bait") and player.inventory.count(data["bait"]) == 0:
        return f"Você está sem isca: {item_name(data['bait'], colored=False)}."
    if not node_open(spot, state):
        return data.get("closed", f"Não dá para {verb} {data['name']} agora.")
    if node_left(state, spot) <= 0:
        return (f"{data['name']}: esgotado por enquanto. Volta a render em cerca de "
                f"{minutes_to_refill(state, spot)} min.")
    if not _fits(player, data["item"]):
        return "Sua mochila está cheia."
    return None


def _fits(player: "Player", item_id: str) -> bool:
    stack = get_item(item_id).get("stack", 1)
    return player.inventory.free_slots > 0 or any(
        s.item_id == item_id and s.dye is None and s.quantity < stack for s in player.inventory)


@dataclass
class GatherReport:
    name: str
    skill: str
    attempts: int = 0
    minutes: int = 0
    items: Dict[str, int] = field(default_factory=dict)
    xp: int = 0
    rare: List[str] = field(default_factory=list)
    bait_used: int = 0
    stopped: str = ""                                    # por que parou antes de completar
    level_ups: List[Tuple[str, int]] = field(default_factory=list)

    @property
    def gathered(self) -> int:
        return sum(self.items.values())


def gather(player: "Player", state: "GameState", spot: Spot, quantity: int,
           rng: Optional[random.Random] = None) -> GatherReport:
    """Uma sessão de coleta: tenta até colher ``quantity`` itens (ou parar por algum motivo).

    Não avança o relógio — devolve os minutos gastos para a sessão aplicar.
    """
    rng = rng or random.Random()
    data = spot.data
    report = GatherReport(data["name"], data["skill"])
    max_attempts = max(1, min(quantity, ALL)) * ATTEMPTS_PER_ITEM
    while report.gathered < quantity:
        if node_left(state, spot) <= 0:
            report.stopped = "esgotado"
            break
        if data.get("bait") and player.inventory.count(data["bait"]) == 0:
            report.stopped = "isca"
            break
        if not _fits(player, data["item"]):
            report.stopped = "mochila"
            break
        if report.attempts >= max_attempts:
            report.stopped = "azar"
            break
        if report.minutes + data["minutes"] > MAX_SESSION_MINUTES:
            report.stopped = "cansaco"
            break
        report.attempts += 1
        report.minutes += data["minutes"]
        if rng.random() >= gather_chance(player, data):
            continue
        player.inventory.add(data["item"], 1)
        report.items[data["item"]] = report.items.get(data["item"], 0) + 1
        _take_from_node(state, spot)
        if data.get("bait"):
            player.inventory.remove(data["bait"], 1)
            report.bait_used += 1
        _add_xp(player, data["skill"], skill_xp(data["xp"]), report)
        for rare_id, chance in data.get("rare", []):
            if rng.random() < chance and player.inventory.add(rare_id, 1) == 0:
                report.rare.append(rare_id)
    entry = state.nodes.get(spot.key)
    if entry is not None and report.gathered:
        entry["time"] = state.clock.minutes + report.minutes   # o ponto se recupera depois que você para
    return report


def _add_xp(player: "Player", skill_id: str, amount: int, report: Any) -> None:
    before = player.skills.level(skill_id)
    player.skills.add_xp(skill_id, amount)
    report.xp += amount
    after = player.skills.level(skill_id)
    for level in range(before + 1, after + 1):
        report.level_ups.append((skill_id, level))


# --------------------------------------------------------------------------- estações e receitas

def station_name(station_id: str) -> str:
    return STATIONS[station_id]["name"]


def station_at(landmark: Optional[world.Landmark], station_id: str,
               state: "GameState") -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """(estação, None) se ela está aqui e aberta; (None, aviso) se está fechada; (None, None) se não há."""
    if landmark is None:
        return None, None
    for station in landmark.stations:
        if station["id"] == station_id:
            if conditions_met(station.get("if"), state):
                return dict(station), None
            return None, station.get("closed", f"{station.get('name', station_name(station_id))} está fechada agora.")
    return None, None


def station_places(station_id: str) -> List[str]:
    """Nomes dos locais do mundo que têm a estação (para dicas)."""
    return [landmark.name for map_id in world.map_ids() for landmark in world.get_map(map_id).landmarks.values()
            if any(station["id"] == station_id for station in landmark.stations)]


def recipe_output(recipe_id: str) -> Tuple[str, int]:
    item_id, quantity = RECIPES[recipe_id]["output"]
    return item_id, quantity


def recipe_name(recipe_id: str) -> str:
    return get_item(recipe_output(recipe_id)[0])["name"]


def recipes_for(skill_id: Optional[str] = None) -> List[str]:
    """Receitas de uma perícia (ou todas), em ordem de nível."""
    ids = [recipe_id for recipe_id, recipe in RECIPES.items() if skill_id is None or recipe["skill"] == skill_id]
    return sorted(ids, key=lambda recipe_id: (RECIPES[recipe_id]["level"], recipe_name(recipe_id)))


def max_craftable(player: "Player", recipe_id: str) -> int:
    return min(player.inventory.count(item_id) // quantity for item_id, quantity in RECIPES[recipe_id]["inputs"])


def ingredients_text(recipe_id: str, player: Optional["Player"] = None) -> str:
    """"1 Minério de Cobre + 1 Minério de Estanho" (com o que você tem, se ``player`` for dado)."""
    parts = []
    for item_id, quantity in RECIPES[recipe_id]["inputs"]:
        text = f"{quantity} {get_item(item_id)['name']}"
        if player is not None:
            text += f" ({player.inventory.count(item_id)})"
        parts.append(text)
    return " + ".join(parts)


def missing_text(player: "Player", recipe_id: str) -> str:
    missing = [f"{quantity - player.inventory.count(item_id)} {get_item(item_id)['name']}"
               for item_id, quantity in RECIPES[recipe_id]["inputs"] if player.inventory.count(item_id) < quantity]
    return ", ".join(missing)


def craft_problem(player: "Player", state: "GameState", landmark: Optional[world.Landmark],
                  recipe_id: str) -> Optional[str]:
    """Por que não dá para fazer a receita aqui e agora (``None`` se dá)."""
    recipe = RECIPES[recipe_id]
    name = recipe_name(recipe_id)
    level = player.skills.level(recipe["skill"])
    if level < recipe["level"]:
        return f"{name} exige {skill_name(recipe['skill'])} {recipe['level']} (seu nível: {level})."
    if recipe.get("station"):
        station, closed = station_at(landmark, recipe["station"], state)
        if closed:
            return closed
        if station is None:
            places = station_places(recipe["station"])
            where = f" Há uma em: {', '.join(places)}." if places else ""
            return f"{name} precisa de uma estação: {station_name(recipe['station'])}.{where}"
        if station.get("fuel") and player.inventory.count(station["fuel"]) == 0:
            return (f"{station.get('name', station_name(recipe['station']))} está apagada. Você precisa de "
                    f"{item_name(station['fuel'], colored=False).lower()} para acendê-la.")
    if recipe.get("tool") and best_tool(player, recipe["tool"]) is None:
        return f"Para fazer {name}, você precisa de {TOOL_NAMES[recipe['tool']]}."
    if max_craftable(player, recipe_id) <= 0:
        return f"Faltam ingredientes para {name}: {missing_text(player, recipe_id)}."
    return None


@dataclass
class CraftReport:
    recipe_id: str
    made: int = 0
    failed: int = 0           # material perdido (ferro impuro)
    burnt: int = 0
    xp: int = 0
    minutes: int = 0
    fuel: Optional[str] = None
    stopped: str = ""
    level_ups: List[Tuple[str, int]] = field(default_factory=list)


def craft(player: "Player", state: "GameState", landmark: Optional[world.Landmark], recipe_id: str,
          quantity: int, rng: Optional[random.Random] = None) -> CraftReport:
    """Faz até ``quantity`` itens da receita (quem chama confere ``craft_problem`` antes).

    Não avança o relógio — devolve os minutos gastos para a sessão aplicar.
    """
    rng = rng or random.Random()
    recipe = RECIPES[recipe_id]
    report = CraftReport(recipe_id)
    station: Dict[str, Any] = {}
    if recipe.get("station"):
        station = station_at(landmark, recipe["station"], state)[0] or {}
    if station.get("fuel"):
        player.inventory.remove(station["fuel"], 1)
        report.fuel = station["fuel"]
    output_id, output_qty = recipe["output"]
    dye = player.appearance.armor_color if get_item(output_id).get("dyeable") else None
    for _ in range(max(0, min(quantity, max_craftable(player, recipe_id)))):
        for item_id, amount in recipe["inputs"]:
            player.inventory.remove(item_id, amount)
        level = player.skills.level(recipe["skill"])
        if rng.random() < scaled_chance(recipe.get("fail"), recipe["level"], level):
            report.failed += 1
            report.minutes += recipe["minutes"]
            continue
        if rng.random() < scaled_chance(recipe.get("burn"), recipe["level"], level) * station.get("burn", 1.0):
            report.burnt += 1
            report.minutes += recipe["minutes"]
            player.inventory.add(BURNT_ITEM, 1)    # sem espaço, a comida queimada vai fora mesmo
            continue
        leftover = player.inventory.add(output_id, output_qty, dye)
        if leftover:
            player.inventory.remove(output_id, output_qty - leftover)
            for item_id, amount in recipe["inputs"]:
                player.inventory.add(item_id, amount)
            report.stopped = "mochila"
            break
        report.made += 1
        report.minutes += recipe["minutes"]
        _add_xp(player, recipe["skill"], skill_xp(recipe["xp"]), report)
    return report


# --------------------------------------------------------------------------- progressão

def unlocks(skill_id: str, level: int) -> List[str]:
    """O que fica disponível exatamente neste nível da perícia."""
    names = [data["name"] for data in NODES.values() if data["skill"] == skill_id and data["level"] == level]
    names += [recipe_name(recipe_id) for recipe_id in recipes_for(skill_id) if RECIPES[recipe_id]["level"] == level]
    return names


def next_unlock(skill_id: str, level: int) -> Optional[Tuple[int, List[str]]]:
    """O próximo nível que libera algo, e o quê."""
    levels = sorted({data["level"] for data in NODES.values() if data["skill"] == skill_id}
                    | {recipe["level"] for recipe in RECIPES.values() if recipe["skill"] == skill_id})
    for candidate in levels:
        if candidate > level:
            return candidate, unlocks(skill_id, candidate)
    return None


def node_landmarks(node_id: str) -> List[Tuple[world.Landmark, Mapping[str, Any]]]:
    """Locais do mundo com este tipo de ponto de coleta (com a entrada de cada um)."""
    return [(landmark, entry) for map_id in world.map_ids() for landmark in world.get_map(map_id).landmarks.values()
            for entry in landmark.resources if entry["node"] == node_id]
