"""Integridade do "banco de dados": mapas, terrenos, locais, passagens, NPCs e diálogos.

Estes testes protegem a expansão contínua do mundo: qualquer mapa ou NPC novo com
erro de digitação, coordenada inválida ou nó de diálogo quebrado é apontado aqui.
"""

import string
import unittest
from collections import deque

from rpg import npcs, world
from rpg.data.items import ITEMS
from rpg.data.npcs import NPCS
from rpg.data.terrain import TERRAIN
from rpg.npcs import CONDITION_KEYS, EFFECT_KEYS
from rpg.skills import SKILLS
from rpg.time_system import PERIODS
from tests.helpers import DRAFT

PERIOD_IDS = {period_id for period_id, _hour, _name in PERIODS}
KNOWN_PLACEHOLDERS = {"nome", "tratamento", "Tratamento", "bem_vindo", "Bem_vindo", "classe", "Classe"}


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
                        self.assertTrue(portal.locked_text, f"{portal.id} sem destino precisa estar bloqueado")

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
                        for landmark in npcs._as_list(condition.get("discovered", [])):
                            self.assertIn(landmark, all_landmarks)
                self.assertEqual(visited, set(npc.dialogue), "há nós de diálogo inalcançáveis")

    def test_every_npc_is_somewhere_during_the_day(self):
        for npc_id in NPCS:
            self.assertIsNotNone(npcs.get_npc(npc_id).position("manha"), npc_id)

    def test_dialogue_text_formats_for_every_gender(self):
        from rpg.character_creation import build_player

        for gender in ("masculino", "feminino", "nao_binario"):
            player = build_player({**DRAFT, "gender": gender})
            text = npcs.format_text("{Bem_vindo}, {tratamento} {nome}! {desconhecido}", player)
            self.assertNotIn("{Bem_vindo}", text)
            self.assertIn("{desconhecido}", text)


if __name__ == "__main__":
    unittest.main()
