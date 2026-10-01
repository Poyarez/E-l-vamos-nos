"""Curvas de experiência, atributos, itens e criação de personagem."""

import random
import unittest

from rpg import combat
from rpg.character_creation import build_player, random_draft, validate_name
from rpg.data.classes import CLASSES
from rpg.items import Inventory
from rpg.player import MAX_LEVEL, Player, xp_to_next_level
from rpg.skills import MAX_SKILL_LEVEL, SkillSet, level_for_xp, level_progress, xp_for_level
from tests.helpers import DRAFT


class SkillCurveTest(unittest.TestCase):
    def test_osrs_reference_values(self):
        self.assertEqual(xp_for_level(1), 0)
        self.assertEqual(xp_for_level(2), 83)
        self.assertEqual(xp_for_level(10), 1154)
        self.assertEqual(xp_for_level(50), 101333)
        self.assertEqual(xp_for_level(92), 6517253)
        self.assertEqual(xp_for_level(99), 13034431)

    def test_level_for_xp_boundaries(self):
        self.assertEqual(level_for_xp(0), 1)
        self.assertEqual(level_for_xp(82), 1)
        self.assertEqual(level_for_xp(83), 2)
        self.assertEqual(level_for_xp(13034430), 98)
        self.assertEqual(level_for_xp(200_000_000), MAX_SKILL_LEVEL)

    def test_progress_and_skillset(self):
        self.assertEqual(level_progress(100), (2, 17, 174 - 83))
        skills = SkillSet({"mineracao": 90, "desconhecida": 999})
        self.assertNotIn("desconhecida", skills.xp)
        self.assertEqual(skills.level("mineracao"), 2)
        self.assertEqual(skills.add_xp("pesca", 1154), 9)
        self.assertEqual(skills.total_level(), 2 + 10 + 4)


class CombatLevelTest(unittest.TestCase):
    def test_wow_classic_curve(self):
        expected = [400, 900, 1400, 2100, 2800, 3600, 4500, 5400, 6500, 7600]
        self.assertEqual([xp_to_next_level(level) for level in range(1, 11)], expected)
        self.assertEqual(xp_to_next_level(MAX_LEVEL), 0)

    def test_gain_xp_levels_up_and_restores(self):
        player = build_player(DRAFT)
        player.hp = 1
        level_ups = player.gain_xp(1300)
        self.assertEqual([lu.level for lu in level_ups], [2, 3])
        self.assertEqual(player.xp, 0)
        self.assertEqual(player.hp, player.max_hp)
        self.assertIn("Dilacerar", [name for lu in player.gain_xp(1400) for name in lu.new_abilities])

    def test_max_level_stops_xp(self):
        player = build_player(DRAFT)
        player.gain_xp(10_000_000)
        self.assertEqual(player.level, MAX_LEVEL)
        self.assertEqual(player.xp, 0)
        self.assertEqual(player.gain_xp(500), [])


class PlayerTest(unittest.TestCase):
    def test_every_class_builds_with_valid_gear(self):
        for class_id in CLASSES:
            for gender in ("masculino", "feminino", "nao_binario"):
                player = build_player({**DRAFT, "class_id": class_id, "gender": gender})
                self.assertTrue(player.equipment)
                self.assertGreater(player.max_hp, 0)
                self.assertGreater(player.max_resource, 0)
                expected = player.max_resource if player.resource_data["starts_full"] else 0
                self.assertEqual(player.resource, expected)
                self.assertTrue(player.abilities())
                for ability in player.abilities(include_locked=True):
                    self.assertIn(ability["element"], combat.ELEMENTS)

    def test_starting_armor_is_dyed(self):
        player = build_player(DRAFT)
        self.assertEqual(player.equipment["peito"].dye, "azul_real")
        self.assertIn("Azul real", player.equipment["peito"].name(colored=False))
        self.assertIsNone(player.equipment["arma"].dye)

    def test_gendered_forms_and_portrait(self):
        self.assertEqual(build_player({**DRAFT, "gender": "feminino"}).forms["tratamento"], "senhora")
        self.assertEqual(build_player({**DRAFT, "gender": "nao_binario"}).forms["Bem_vindo"], "Boas-vindas")
        bald = build_player({**DRAFT, "hair_style": "cabeca_raspada"})
        self.assertNotIn("de um tom", bald.portrait())

    def test_roundtrip(self):
        player = build_player(DRAFT)
        player.gain_xp(500)
        clone = Player.from_dict(player.to_dict())
        self.assertEqual(clone.to_dict(), player.to_dict())

    def test_random_drafts_are_valid(self):
        rng = random.Random(7)
        for _ in range(50):
            self.assertIsInstance(build_player(random_draft(rng)), Player)


class NameTest(unittest.TestCase):
    def test_validation(self):
        self.assertEqual(validate_name("  ana   lua "), "Ana lua")
        self.assertEqual(validate_name("D'Artagnan"), "D'Artagnan")
        self.assertEqual(validate_name("Árwen-Lis"), "Árwen-Lis")
        for bad in ("", "A", "Nome Muito Comprido Demais", "R2D2", "Ana--Lua", "Zé!"):
            self.assertIsNone(validate_name(bad), bad)


class InventoryTest(unittest.TestCase):
    def test_stacking_capacity_and_removal(self):
        bag = Inventory(capacity=2)
        self.assertEqual(bag.add("pao_de_viagem", 25), 0)      # 20 + 5: duas pilhas
        self.assertEqual(len(bag), 2)
        self.assertEqual(bag.add("tocha", 1), 1)               # sem espaço
        self.assertTrue(bag.remove("pao_de_viagem", 21))
        self.assertEqual(bag.count("pao_de_viagem"), 4)
        self.assertFalse(bag.remove("pao_de_viagem", 99))
        self.assertEqual(Inventory.from_dict(bag.to_dict()).count("pao_de_viagem"), 4)


class ElementTest(unittest.TestCase):
    def test_multipliers(self):
        self.assertEqual(combat.element_multiplier("fogo"), 1.0)
        self.assertEqual(combat.element_multiplier("fogo", weaknesses=["fogo"]), 1.5)
        self.assertEqual(combat.element_multiplier("gelo", resistances=["gelo"]), 0.5)
        self.assertEqual(combat.element_multiplier("gelo", ["gelo"], ["gelo"]), 1.0)
        self.assertEqual(combat.element_multiplier("sombra", immunities=["sombra"]), 0.0)
        with self.assertRaises(KeyError):
            combat.element_multiplier("plasma")


if __name__ == "__main__":
    unittest.main()
