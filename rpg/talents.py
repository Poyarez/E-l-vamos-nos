"""Árvores de talentos (estilo WoW Classic).

A partir do nível 10, cada nível dá um ponto de talento. Cada classe tem três árvores
(em ``rpg.data.classes``) com quatro talentos em quatro tiers; para abrir um tier é preciso
ter gasto pontos naquela árvore (``TIER_REQUIREMENTS``). O último talento de cada árvore
ensina uma habilidade nova.

Este módulo só lê dados e o dicionário ``{talento: pontos}`` do herói; quem aplica os
bônus é o herói (atributos, vida, armadura) e o motor de combate (dano, críticos, custos).
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Tuple

from .data.classes import CLASSES, STATS, TALENT_START_LEVEL

#: Pontos gastos na árvore exigidos para abrir cada tier.
TIER_REQUIREMENTS = {1: 0, 2: 5, 3: 10, 4: 13}

ELEMENT_NAMES = {"fisico": "físico", "fogo": "de Fogo", "gelo": "de Gelo", "arcano": "Arcano",
                 "sagrado": "Sagrado", "sombra": "de Sombra", "natureza": "de Natureza"}


def trees(class_id: str) -> List[Dict[str, Any]]:
    return CLASSES[class_id]["talent_trees"]


def all_talents(class_id: str) -> Dict[str, Tuple[int, Dict[str, Any]]]:
    """``{id do talento: (índice da árvore, talento)}``."""
    return {talent["id"]: (index, talent) for index, tree in enumerate(trees(class_id))
            for talent in tree["talents"]}


def points_total(level: int) -> int:
    """Pontos de talento que o nível concede."""
    return max(0, level - TALENT_START_LEVEL + 1)


def points_spent(learned: Mapping[str, int]) -> int:
    return sum(learned.values())


def points_in_tree(class_id: str, learned: Mapping[str, int], tree_index: int) -> int:
    return sum(learned.get(talent["id"], 0) for talent in trees(class_id)[tree_index]["talents"])


def learn_problem(class_id: str, level: int, learned: Mapping[str, int], talent_id: str) -> Optional[str]:
    """Por que o talento não pode receber mais um ponto agora (``None`` se pode)."""
    catalog = all_talents(class_id)
    if talent_id not in catalog:
        return "Talento desconhecido."
    tree_index, talent = catalog[talent_id]
    if points_total(level) - points_spent(learned) <= 0:
        if level < TALENT_START_LEVEL:
            return f"Os talentos se abrem no nível {TALENT_START_LEVEL}."
        return "Você não tem pontos de talento livres. Ganhe um nível para receber mais."
    if learned.get(talent_id, 0) >= talent["ranks"]:
        return f"{talent['name']} já está no máximo."
    needed = TIER_REQUIREMENTS[talent["tier"]]
    spent = points_in_tree(class_id, learned, tree_index)
    if spent < needed:
        tree_name = trees(class_id)[tree_index]["name"]
        return f"{talent['name']} exige {needed} pontos em {tree_name} (você tem {spent})."
    return None


def learn(class_id: str, level: int, learned: Dict[str, int], talent_id: str) -> None:
    problem = learn_problem(class_id, level, learned, talent_id)
    if problem:
        raise ValueError(problem)
    learned[talent_id] = learned.get(talent_id, 0) + 1


def bonus(class_id: str, learned: Mapping[str, int], kind: str, key: Optional[str] = None) -> float:
    """Soma dos efeitos de um tipo (``kind``) para uma chave (elemento, habilidade ou atributo).

    Efeitos com ``key: "all"`` valem para qualquer chave.
    """
    total = 0.0
    catalog = all_talents(class_id)
    for talent_id, ranks in learned.items():
        if ranks <= 0 or talent_id not in catalog:
            continue
        for effect in catalog[talent_id][1]["effects"]:
            if effect["kind"] != kind:
                continue
            effect_key = effect.get("key")
            if effect_key is None or effect_key == "all" or effect_key == key:
                total += effect.get("value", 0) * ranks
    return total


def granted_abilities(class_id: str, learned: Mapping[str, int]) -> List[str]:
    catalog = all_talents(class_id)
    return [effect["key"] for talent_id, ranks in learned.items() if ranks > 0 and talent_id in catalog
            for effect in catalog[talent_id][1]["effects"] if effect["kind"] == "ability"]


def effect_text(effect: Mapping[str, Any], class_id: str) -> str:
    """Descrição de um efeito por ponto: "+2% de dano físico"."""
    kind, value, key = effect["kind"], effect.get("value", 0), effect.get("key")
    percent = f"{value * 100:g}%"
    abilities = {ability["id"]: ability["name"] for ability in CLASSES[class_id]["abilities"]}
    if kind == "stat":
        return f"+{value:g} de {STATS[key]['name']}"
    if kind == "damage_pct":
        return f"+{percent} de dano" + ("" if key == "all" else f" {ELEMENT_NAMES[key]}")
    texts = {
        "crit": f"+{percent} de chance de crítico",
        "spell_crit": f"+{percent} de chance de crítico mágico",
        "dodge": f"+{percent} de esquiva",
        "hit": f"+{percent} de chance de acerto",
        "armor_pct": f"+{percent} de armadura",
        "max_hp_pct": f"+{percent} de vida máxima",
        "max_resource_pct": f"+{percent} de mana máxima",
        "heal_pct": f"+{percent} de cura",
        "shield_pct": f"+{percent} de absorção dos escudos",
        "rage_pct": f"+{percent} de Raiva gerada",
        "mana_regen_pct": f"+{percent} de regeneração de mana",
        "offhand_pct": f"+{percent} de dano da mão secundária",
        "coating_pct": f"+{percent} de dano dos venenos de arma",
    }
    if kind in texts:
        return texts[kind]
    if kind == "ability_pct":
        return f"+{percent} de dano de {abilities.get(key, key)}"
    if kind == "cost":
        return f"-{value:g} no custo de " + ("todas as habilidades" if key == "all" else abilities.get(key, key))
    if kind == "cooldown":
        return f"-{value:g} turno na recarga de {abilities.get(key, key)}"
    if kind == "ability":
        ability = next(a for a in CLASSES[class_id]["abilities"] if a["id"] == key)
        return f"Ensina {ability['name']}: {ability['description']}"
    raise KeyError(f"Efeito de talento desconhecido: {kind!r}")


def describe(class_id: str, talent: Mapping[str, Any]) -> str:
    texts = [effect_text(effect, class_id) for effect in talent["effects"]]
    suffix = " por ponto" if talent["ranks"] > 1 else ""
    return ("; ".join(texts) + suffix).rstrip(".") + "."
