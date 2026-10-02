"""Exporta o "banco de dados" do jogo (``rpg.data``) para JSON, lido pela versão Godot.

Os dados continuam nascendo no Python: classes, itens, mapas, NPCs, monstros e missões
são escritos uma vez só e chegam ao Godot por este script, sem redigitar nada.

Uso (na raiz do repositório):

    python tools/export_godot_data.py

Os arquivos vão para ``godot/data/``. O teste ``tests/test_godot_export.py`` avisa quando
algum dado mudou e o JSON ficou desatualizado.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rpg.config import GAME_SUBTITLE, GAME_TITLE, GAME_VERSION  # noqa: E402
from rpg.data import appearance, classes, gathering, items, monsters, npcs, quests, recipes, shops, skills  # noqa: E402
from rpg.data import terrain  # noqa: E402
from rpg.data.maps import MAPS  # noqa: E402
from rpg.items import DEFAULT_BAG_SLOTS  # noqa: E402
from rpg.player import MAX_LEVEL, xp_to_next_level  # noqa: E402
from rpg import quests as quest_rules, time_system  # noqa: E402

OUT_DIR = ROOT / "godot" / "data"


def _map_entry(data: Dict[str, Any]) -> Dict[str, Any]:
    """O mapa como no Python, mas com o desenho já dividido em linhas."""
    entry = {key: value for key, value in data.items() if key != "layout"}
    entry["rows"] = data["layout"].strip("\n").split("\n")
    return entry


def build() -> Dict[str, Any]:
    """Todos os arquivos a escrever: ``{caminho relativo: conteúdo}``."""
    files: Dict[str, Any] = {
        "terrain.json": terrain.TERRAIN,
        "npcs.json": npcs.NPCS,
        "items.json": {
            "items": items.ITEMS, "qualities": items.QUALITIES, "slots": items.SLOTS, "types": items.ITEM_TYPES,
            "subtypes": items.SUBTYPES, "starting_items": items.STARTING_ITEMS,
            "starting_copper": items.STARTING_COPPER,
        },
        "monsters.json": {"families": monsters.FAMILIES, "monsters": monsters.MONSTERS},
        "classes.json": {"classes": classes.CLASSES, "resources": classes.RESOURCES, "stats": classes.STATS,
                         "talent_start_level": classes.TALENT_START_LEVEL},
        "appearance.json": {"genders": appearance.GENDERS, "hair_styles": appearance.HAIR_STYLES,
                            "hair_colors": appearance.HAIR_COLORS, "features": appearance.FEATURES,
                            "armor_colors": appearance.ARMOR_COLORS, "alignments": appearance.ALIGNMENTS},
        "quests.json": {"quests": quests.QUESTS, "bounties": quests.BOUNTIES,
                        "board_landmark": quest_rules.BOARD_LANDMARK, "board_size": quest_rules.BOARD_SIZE,
                        "max_active_bounties": quest_rules.MAX_ACTIVE_BOUNTIES,
                        "categories": quest_rules.CATEGORIES},
        "crafting.json": {"skills": skills.SKILLS, "nodes": gathering.NODES, "gather_verbs": gathering.GATHER_VERBS,
                          "recipes": recipes.RECIPES, "stations": recipes.STATIONS,
                          "burnt_item": recipes.BURNT_ITEM},
        "shops.json": shops.SHOPS,
        "rules.json": {
            "title": GAME_TITLE, "subtitle": GAME_SUBTITLE, "version": GAME_VERSION,
            "minutes_per_day": time_system.MINUTES_PER_DAY, "start_minutes": time_system.START_MINUTES,
            "dawn_hour": time_system.DAWN_HOUR,
            "periods": [{"id": period_id, "hour": hour, "name": name}
                        for period_id, hour, name in time_system.PERIODS],
            "night_periods": sorted(time_system.NIGHT_PERIODS),
            "twilight_periods": sorted(time_system.TWILIGHT_PERIODS),
            "moon_phases": list(time_system.MOON_PHASES), "weather": time_system.WEATHER,
            "max_level": MAX_LEVEL,
            # XP para ir do nível N ao N+1 (índice 0 = nível 1), pela curva do WoW Classic
            "xp_to_next": [xp_to_next_level(level) for level in range(1, MAX_LEVEL + 1)],
            "bag_slots": DEFAULT_BAG_SLOTS,
        },
    }
    for map_id, data in MAPS.items():
        files[f"maps/{map_id}.json"] = _map_entry(data)
    files["maps/index.json"] = list(MAPS)
    return files


def render(content: Any) -> str:
    return json.dumps(content, ensure_ascii=False, indent=1) + "\n"


def export(out_dir: Path = OUT_DIR) -> int:
    """Escreve os arquivos e devolve quantos foram (re)escritos."""
    written = 0
    for name, content in build().items():
        path = out_dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        text = render(content)
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            path.write_text(text, encoding="utf-8")
            written += 1
    return written


if __name__ == "__main__":
    count = export()
    print(f"{count} arquivo(s) atualizado(s) em {OUT_DIR.relative_to(ROOT)}")
