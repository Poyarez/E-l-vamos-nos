"""Monstros: fábrica a partir de ``rpg.data.monsters``, experiência por abate, cores de
dificuldade, tabelas de saque por porcentagem e sorteio de encontros.

A experiência segue a fórmula do WoW Classic — ``nível × 5 + 45`` contra um inimigo do
mesmo nível, mais 5% por nível acima, menos conforme a "diferença zero" abaixo, dobrada
para elites — multiplicada por ``XP_RATE`` para combinar com o ritmo de um jogo de texto.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Tuple

from .combat import Monster
from .conditions import conditions_met
from .data.monsters import MONSTERS

if TYPE_CHECKING:
    from .state import GameState

XP_RATE = 2.0


def get_template(template_id: str) -> Dict[str, Any]:
    try:
        return MONSTERS[template_id]
    except KeyError:
        raise KeyError(f"Monstro desconhecido: {template_id!r}") from None


def stat_curve(level: int) -> Tuple[float, float, float]:
    """Vida, dano médio por golpe e armadura de uma criatura comum deste nível."""
    return 38 + 15 * (level - 1), 3.8 + 1.7 * (level - 1), 15 + 22 * level


def create_monster(template_id: str, level: Optional[int] = None,
                   rng: Optional[random.Random] = None) -> Monster:
    """Fábrica de monstros: sem ``level``, sorteia um nível da faixa do modelo."""
    data = get_template(template_id)
    rng = rng or random.Random()
    if level is None:
        level = rng.randint(*data["levels"])
    hp, damage, armor = stat_curve(level)
    average = damage * data.get("damage", 1.0)
    return Monster(template_id, data, level, max_hp=int(round(hp * data.get("hp", 1.0))),
                   damage=(average * 0.8, average * 1.2), armor=int(round(armor * data.get("armor", 1.0))))


# --------------------------------------------------------------------------- experiência e dificuldade

def zero_difference(level: int) -> int:
    """Quantos níveis abaixo do herói uma criatura deixa de dar experiência (tabela do WoW Classic)."""
    for limit, value in ((7, 5), (9, 6), (11, 7), (15, 8), (19, 9), (29, 11), (39, 12), (44, 13), (49, 14),
                         (54, 15), (59, 16)):
        if level <= limit:
            return value
    return 17


def kill_xp(player_level: int, monster_level: int, elite: bool = False) -> int:
    base = player_level * 5 + 45
    diff = monster_level - player_level
    if diff >= 0:
        xp = base * (1 + 0.05 * min(diff, 4))
    else:
        gap = zero_difference(player_level)
        if -diff >= gap:
            return 0
        xp = base * (1 - (-diff) / gap)
    if elite:
        xp *= 2
    return int(round(xp * XP_RATE))


def con_color(player_level: int, monster_level: int) -> str:
    """Cor de dificuldade do WoW: cinza, verde, amarelo, laranja (vermelho escuro) e vermelho."""
    diff = monster_level - player_level
    if diff >= 5:
        return "bright_red"
    if diff >= 3:
        return "red"
    if diff >= -2:
        return "bright_yellow"
    if kill_xp(player_level, monster_level) > 0:
        return "bright_green"
    return "gray"


# --------------------------------------------------------------------------- saque

def roll_loot(monster: Monster, rng: random.Random) -> Tuple[List[Tuple[str, int]], int]:
    """Sorteia o saque de uma criatura derrotada: (itens com quantidade, cobre)."""
    items: List[Tuple[str, int]] = []
    for entry in monster.data.get("loot", []):
        if rng.random() * 100 >= entry.get("chance", 100):
            continue
        item_id = rng.choice(entry["one_of"]) if "one_of" in entry else entry["item"]
        low, high = entry.get("qty", (1, 1))
        items.append((item_id, rng.randint(low, high)))
    low, high = monster.data.get("copper", (0, 0))
    copper = rng.randint(low, high) if high else 0
    return items, copper


# --------------------------------------------------------------------------- encontros

def _group_allowed(group: Mapping[str, Any], state: "GameState", outdoor: bool) -> bool:
    time = group.get("time")
    if outdoor and time == "noite" and not state.clock.is_night:
        return False
    if outdoor and time == "dia" and state.clock.is_night:
        return False
    return conditions_met(group.get("if"), state)


def available_groups(encounters: Optional[Mapping[str, Any]], state: "GameState",
                     outdoor: bool = True) -> List[Mapping[str, Any]]:
    if not encounters:
        return []
    return [group for group in encounters["groups"] if _group_allowed(group, state, outdoor)]


def encounter_chance(encounters: Optional[Mapping[str, Any]], state: "GameState", outdoor: bool = True) -> float:
    if not encounters:
        return 0.0
    chance = encounters.get("chance", 0.0)
    if outdoor and state.clock.is_night:
        chance += encounters.get("night_bonus", 0.0)
    return chance


def pick_group(encounters: Mapping[str, Any], state: "GameState", rng: random.Random,
               outdoor: bool = True) -> Optional[List[Tuple[str, int]]]:
    """Sorteia um grupo da tabela: lista de (criatura, nível)."""
    groups = available_groups(encounters, state, outdoor)
    if not groups:
        return None
    group = rng.choices(groups, weights=[g.get("weight", 1) for g in groups])[0]
    picked = []
    for template_id in group["monsters"]:
        low, high = group.get("levels") or get_template(template_id)["levels"]
        picked.append((template_id, rng.randint(low, high)))
    return picked


def danger_range(encounters: Optional[Mapping[str, Any]], state: "GameState",
                 outdoor: bool = True) -> Optional[Tuple[int, int]]:
    """Faixa de níveis das criaturas que podem aparecer agora."""
    levels = []
    for group in available_groups(encounters, state, outdoor):
        for template_id in group["monsters"]:
            levels.extend(group.get("levels") or get_template(template_id)["levels"])
    return (min(levels), max(levels)) if levels else None
