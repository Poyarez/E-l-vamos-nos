"""Integridade do "banco de dados": mapas, terrenos, locais, passagens, NPCs, diálogos,
monstros, encontros, habilidades, itens e lojas.

Estes testes protegem a expansão contínua do mundo: qualquer mapa, NPC ou monstro novo
com erro de digitação, coordenada inválida, item inexistente ou nó de diálogo quebrado é
apontado aqui.
"""

import string
import unittest
from collections import deque

from rpg import npcs, world
from rpg.character_creation import build_player
from rpg.combat import ELEMENTS, MAX_ENEMIES
from rpg.conditions import CONDITION_KEYS, as_list
from rpg.data.classes import CLASSES, STATS
from rpg.data.items import ITEM_TYPES, ITEMS, SLOTS, SUBTYPES
from rpg.data.monsters import FAMILIES, MONSTERS
from rpg.data.npcs import NPCS
from rpg.data.shops import SHOPS
from rpg.data.terrain import TERRAIN
from rpg.npcs import EFFECT_KEYS
from rpg.skills import SKILLS
from rpg.time_system import PERIODS
from tests.helpers import DRAFT

PERIOD_IDS = {period_id for period_id, _hour, _name in PERIODS}
KNOWN_PLACEHOLDERS = {"nome", "tratamento", "Tratamento", "bem_vindo", "Bem_vindo", "classe", "Classe"}

# o que o motor de combate (rpg.combat) sabe resolver
HERO_EFFECTS = {"damage", "finisher", "execute", "dot", "debuff", "stun", "freeze", "fear", "interrupt", "combo",
                "heal", "hot", "shield", "buff", "rage", "stealth"}
MONSTER_EFFECTS = {"dot", "stun", "freeze", "fear", "debuff", "drain_mana", "heal_self", "buff_self"}
REQUIREMENTS = {"first_round", "shield", "dagger", "combo", "target_below"}
MODIFIED_STATS = {"ap", "armor", "dodge", "hit", "damage_dealt", "damage_taken", "max_hp"}
SCALES = {None, "weapon", "ap", "sp"}
USE_KEYS = {"heal", "heal_pct", "mana", "mana_pct", "combat", "minutes", "verb"}


def placeholders(text):
    return {field for _literal, field, _spec, _conv in string.Formatter().parse(text) if field}


def reachable(game_map, start):
    seen, queue = {start}, deque([start])
    while queue:
        x, y = queue.popleft()
        for dx, dy, _name in world.DIRECTIONS.values():
            nxt = (x + dx, y + dy)
            if nxt not in seen and game_map.can_step(x, y, dx, dy):
                seen.add(nxt)
                queue.append(nxt)
    return seen


class TerrainTest(unittest.TestCase):
    def test_terrain_entries(self):
        for terrain_id, data in TERRAIN.items():
            self.assertTrue(data["day"], terrain_id)
            if data["passable"]:
                self.assertGreater(data["cost"], 0, terrain_id)


class MapIntegrityTest(unittest.TestCase):
    def test_all_maps(self):
        landmark_ids, region_ids = set(), set()
        for map_id in world.map_ids():
            game_map = world.get_map(map_id)
            with self.subTest(map=map_id):
                self.assertTrue(game_map.passable(*game_map.start))
                tiles = reachable(game_map, game_map.start)
                for landmark in game_map.landmarks.values():
                    self.assertNotIn(landmark.id, landmark_ids, "ids de locais devem ser únicos no mundo")
                    landmark_ids.add(landmark.id)
                    self.assertTrue(game_map.passable(landmark.x, landmark.y), landmark.id)
                    self.assertIn(landmark.pos, tiles, f"{landmark.id} é inalcançável")
                    self.assertIsNotNone(game_map.region_at(landmark.x, landmark.y), landmark.id)
                    self.assertTrue(landmark.description and landmark.examine, landmark.id)
                    if landmark.hint:
                        self.assertEqual(placeholders(landmark.hint), {"direcao"}, landmark.id)
                    for node in landmark.resources:
                        self.assertIn(node["skill"], SKILLS)
                        self.assertTrue(1 <= node["level"] <= 99)
                    if landmark.loot:
                        for item_id, quantity in landmark.loot.get("items", []):
                            self.assertIn(item_id, ITEMS)
                            self.assertGreater(quantity, 0)
                for region in game_map.regions:
                    self.assertNotIn(region.id, region_ids, "ids de regiões devem ser únicos no mundo")
                    region_ids.add(region.id)
                for portal in game_map.portals:
                    self.assertTrue(game_map.passable(portal.x, portal.y), portal.id)
                    self.assertTrue(portal.direction or portal.verb, portal.id)
                    if portal.direction:
                        self.assertIn(portal.direction, world.DIRECTIONS)
                    if portal.verb:
                        self.assertIn(portal.verb, ("entrar", "sair"))
                    if portal.target:
                        target_map, x, y = portal.target
                        self.assertTrue(world.get_map(target_map).passable(x, y), portal.id)
                    else:
                        self.assertTrue(portal.locked and portal.locked_text,
                                        f"{portal.id} sem destino precisa estar bloqueado")

    def test_every_map_has_a_way_in(self):
        targets = {portal.target[0] for map_id in world.map_ids() for portal in world.get_map(map_id).portals
                   if portal.target}
        self.assertLessEqual(set(world.map_ids()) - {"vale_primordia"}, targets)

    def test_valley_is_large_and_fully_connected(self):
        game_map = world.get_map("vale_primordia")
        self.assertEqual((game_map.width, game_map.height), (60, 30))
        tiles = reachable(game_map, game_map.start)
        island = {(45, 24), (46, 24)}      # a ilhota do lago só será alcançável de barco
        unreachable = {(x, y) for y in range(game_map.height) for x in range(game_map.width)
                       if game_map.passable(x, y) and (x, y) not in tiles}
        self.assertEqual(unreachable, island)
        self.assertGreaterEqual(len(game_map.landmarks), 35)

    def test_no_corner_cutting(self):
        tiny = world.GameMap({"id": "teste", "name": "Teste", "start": (0, 0),
                              "legend": {".": "planicie", "~": "agua"}, "layout": ".~.\n~..\n..."})
        self.assertFalse(tiny.can_step(0, 0, 1, 1))    # água nos dois lados da diagonal
        self.assertTrue(tiny.can_step(1, 1, 1, 1))
        self.assertFalse(tiny.can_step(1, 1, 1, -1))   # (1,0) é água: precisa contornar
        self.assertIsNone(tiny.find_path((0, 0), (2, 2)))
        self.assertEqual(tiny.find_path((1, 1), (2, 0)), [(2, 1), (2, 0)])

    def test_pathfinding_prefers_roads_and_respects_allowed(self):
        game_map = world.get_map("vale_primordia")
        path = game_map.find_path((30, 18), (30, 29))
        self.assertEqual(path[-1], (30, 29))
        self.assertTrue(all(game_map.char_at(x, y) in "=#" for x, y in path))
        self.assertIsNone(game_map.find_path((30, 18), (5, 6), allowed=lambda x, y: False))

    def test_direction_helpers(self):
        self.assertEqual(world.parse_direction("nordeste"), "ne")
        self.assertEqual(world.parse_direction("w"), "o")
        self.assertIsNone(world.parse_direction("cima"))
        self.assertEqual(world.direction_between((0, 0), (5, -1)), "l")
        self.assertEqual(world.direction_between((0, 0), (-3, 3)), "so")
        self.assertIsNone(world.direction_between((2, 2), (2, 2)))


class NpcDataTest(unittest.TestCase):
    def test_npcs_and_dialogues(self):
        all_landmarks = {lm for map_id in world.map_ids() for lm in world.get_map(map_id).landmarks}
        for npc in npcs.all_npcs():
            with self.subTest(npc=npc.id):
                game_map = world.get_map(npc.map_id)
                for rule in npc.schedule:
                    self.assertTrue(game_map.passable(rule["x"], rule["y"]))
                    self.assertLessEqual(set(rule.get("periods", PERIOD_IDS)), PERIOD_IDS)
                self.assertIn("inicio", npc.dialogue)
                visited, queue = set(), deque(["inicio"])
                while queue:
                    node_id = queue.popleft()
                    if node_id in visited:
                        continue
                    visited.add(node_id)
                    node = npc.dialogue[node_id]
                    self.assertTrue("options" in node or "next" in node or node.get("text"), node_id)
                    texts = [entry if isinstance(entry, str) else entry["text"] for entry in node.get("text", [])]
                    for entry in node.get("text", []):
                        if isinstance(entry, dict):
                            self.assertLessEqual(set(entry["if"]), CONDITION_KEYS)
                    for option in node.get("options", []):
                        texts.append(option["text"])
                        self.assertLessEqual(set(option.get("if", {})), CONDITION_KEYS)
                        if option["next"] is not None:
                            self.assertIn(option["next"], npc.dialogue)
                            queue.append(option["next"])
                    if node.get("next"):
                        self.assertIn(node["next"], npc.dialogue)
                        queue.append(node["next"])
                    effects = node.get("effects", {})
                    self.assertLessEqual(set(effects), EFFECT_KEYS)
                    journal = effects.get("journal", [])
                    for entry in journal if isinstance(journal, list) else [journal]:
                        self.assertTrue(entry["id"] and entry["title"] and entry["text"])
                    for text in texts:
                        self.assertLessEqual(placeholders(text), KNOWN_PLACEHOLDERS, text)
                    for condition in [e.get("if", {}) for e in node.get("options", [])]:
                        for landmark in as_list(condition.get("discovered", [])):
                            self.assertIn(landmark, all_landmarks)
                self.assertEqual(visited, set(npc.dialogue), "há nós de diálogo inalcançáveis")

    def test_every_npc_is_somewhere_during_the_day(self):
        for npc_id in NPCS:
            self.assertIsNotNone(npcs.get_npc(npc_id).position("manha"), npc_id)

    def test_dialogue_text_formats_for_every_gender(self):
        for gender in ("masculino", "feminino", "nao_binario"):
            player = build_player({**DRAFT, "gender": gender})
            text = npcs.format_text("{Bem_vindo}, {tratamento} {nome}! {desconhecido}", player)
            self.assertNotIn("{Bem_vindo}", text)
            self.assertIn("{desconhecido}", text)



class CombatDataTest(unittest.TestCase):
    def assertEffect(self, effect, allowed):
        self.assertIn(effect["type"], allowed)
        if "stat" in effect:
            self.assertIn(effect["stat"], MODIFIED_STATS)
        if "element" in effect:
            self.assertIn(effect["element"], ELEMENTS)
        if effect["type"] in ("dot", "hot", "buff", "debuff", "shield", "stun", "freeze", "fear"):
            self.assertGreater(effect["turns"], 0)
        if effect["type"] in ("dot", "hot", "buff", "debuff", "buff_self", "shield"):
            self.assertTrue(effect.get("id") and effect.get("name"), effect)

    def test_monsters(self):
        for template_id, data in MONSTERS.items():
            with self.subTest(monster=template_id):
                self.assertTrue(data["name"] and data["description"])
                self.assertIn(data["family"], FAMILIES)
                low, high = data["levels"]
                self.assertTrue(1 <= low <= high <= 60)
                elements = [data.get("element", "fisico"), *data.get("weaknesses", ()),
                            *data.get("resistances", ()), *data.get("immunities", ())]
                self.assertLessEqual(set(elements), set(ELEMENTS))
                ids = [ability["id"] for ability in data.get("abilities", [])]
                self.assertEqual(len(ids), len(set(ids)))
                for ability in data.get("abilities", []):
                    self.assertTrue(0 < ability.get("chance", 0) <= 1 or 0 < ability.get("hp_below", 0) < 1,
                                    ability["id"])
                    self.assertIn(ability.get("element", "fisico"), ELEMENTS)
                    self.assertLessEqual(set(ability.get("locks", [])), set(ELEMENTS))
                    if ability.get("locks"):
                        self.assertGreater(ability.get("charge", 0), 0, ability["id"])
                    for summoned in ability.get("summon", []):
                        self.assertIn(summoned, MONSTERS)
                    for effect in ability.get("effects", []):
                        self.assertEffect(effect, MONSTER_EFFECTS)
                for entry in data.get("loot", []):
                    for item_id in entry.get("one_of") or [entry["item"]]:
                        self.assertIn(item_id, ITEMS)
                    self.assertTrue(0 < entry.get("chance", 100) <= 100)
                    low, high = entry.get("qty", (1, 1))
                    self.assertTrue(1 <= low <= high)
                low, high = data.get("copper", (0, 0))
                self.assertTrue(0 <= low <= high)

    def test_class_abilities(self):
        for class_id, data in CLASSES.items():
            ids = [ability["id"] for ability in data["abilities"]]
            self.assertEqual(len(ids), len(set(ids)), class_id)
            skills = data["proficiencies"]
            self.assertLessEqual(set(skills["armor"]) | set(skills["weapons"]), set(SUBTYPES))
            self.assertLessEqual(set(data["attack_power"]) | set(data.get("spell_power") or {}), set(STATS))
            for ability in data["abilities"]:
                with self.subTest(ability=ability["id"]):
                    self.assertTrue(1 <= ability["level"] <= 60)
                    self.assertIn(ability.get("target", "enemy"), ("enemy", "self", "all_enemies"))
                    self.assertLessEqual(set(ability.get("requires", {})), REQUIREMENTS)
                    self.assertTrue(ability["effects"] and ability["description"])
                    for effect in ability["effects"]:
                        self.assertEffect(effect, HERO_EFFECTS)
                        self.assertIn(effect.get("scale"), SCALES)
                        if effect.get("scale") == "sp":
                            self.assertTrue(data.get("spell_power"), "magia sem poder mágico")
            player = build_player({**DRAFT, "class_id": class_id})
            for slot, stack in player.equipment.items():
                self.assertEqual(stack.data["slot"], slot)
                self.assertIsNone(player.equip_problem(stack.item_id), f"{class_id}: {stack.item_id}")

    def test_items(self):
        for item_id, data in ITEMS.items():
            with self.subTest(item=item_id):
                self.assertTrue(data["name"] and data["description"])
                self.assertIn(data["type"], ITEM_TYPES)
                self.assertGreaterEqual(data["value"], 0)
                if data.get("slot"):
                    self.assertIn(data["slot"], SLOTS)
                if data.get("subtype"):
                    self.assertIn(data["subtype"], SUBTYPES)
                if data["type"] == "arma":
                    low, high = data["damage"]
                    self.assertTrue(0 < low <= high and data.get("subtype"))
                self.assertLessEqual(set(data.get("stats", {})), set(STATS))
                if data.get("use"):
                    self.assertLessEqual(set(data["use"]), USE_KEYS)

    def test_shops(self):
        for shop_id, data in SHOPS.items():
            with self.subTest(shop=shop_id):
                self.assertGreater(data["markup"], 0)
                self.assertTrue(data["stock"])
                for item_id in data["stock"]:
                    self.assertIn(item_id, ITEMS)
                    self.assertGreater(ITEMS[item_id]["value"], 0)
        for npc in npcs.all_npcs():
            if npc.shop:
                self.assertIn(npc.shop, SHOPS, npc.id)

    def test_encounter_tables(self):
        for map_id in world.map_ids():
            game_map = world.get_map(map_id)
            for region in game_map.regions:
                table = region.encounters
                if not table:
                    continue
                with self.subTest(region=region.id):
                    self.assertTrue(0 < table["chance"] < 1)
                    self.assertTrue(table["groups"])
                    for group in table["groups"]:
                        self.assertTrue(0 < len(group["monsters"]) <= MAX_ENEMIES)
                        self.assertLessEqual(set(group["monsters"]), set(MONSTERS))
                        self.assertIn(group.get("time"), (None, "dia", "noite"))
                        self.assertLessEqual(set(group.get("if", {})), CONDITION_KEYS)
                        self.assertGreater(group.get("weight", 1), 0)
                        low, high = group.get("levels", (1, 1))
                        self.assertTrue(1 <= low <= high)
            for landmark in game_map.landmarks.values():
                encounter = landmark.encounter
                if not encounter:
                    continue
                with self.subTest(landmark=landmark.id):
                    self.assertTrue(encounter["flag"])
                    self.assertTrue(0 < len(encounter["monsters"]) <= MAX_ENEMIES)
                    for template_id, level in encounter["monsters"]:
                        self.assertIn(template_id, MONSTERS)
                        self.assertGreaterEqual(level, 1)
                    journal = encounter.get("journal")
                    if journal:
                        self.assertTrue(journal["id"] and journal["title"] and journal["text"])


if __name__ == "__main__":
    unittest.main()
