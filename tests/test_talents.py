"""Talentos (Etapa 4): pontos por nível, tiers, bônus aplicados ao herói e ao combate,
habilidades concedidas, a prece de esquecimento da Irmã Celeste e o save."""

import unittest

from rpg import commands, npcs, talents
from rpg.combat import Hero
from rpg.data.classes import CLASSES, STATS, TALENT_START_LEVEL
from rpg.player import Player
from tests.helpers import QuietTestCase, make_session
from tests.test_combat import ability, fight

EFFECT_KINDS = {"stat", "crit", "spell_crit", "dodge", "hit", "armor_pct", "max_hp_pct", "max_resource_pct",
                "damage_pct", "ability_pct", "heal_pct", "shield_pct", "cost", "cooldown", "rage_pct",
                "mana_regen_pct", "offhand_pct", "coating_pct", "ability"}


def level_up(session, level):
    while session.player.level < level:
        session.gain_xp(session.player.xp_needed - session.player.xp)
    session.pop_messages()
    session.level_ups.clear()


class TalentDataTest(unittest.TestCase):
    def test_every_class_has_three_complete_trees(self):
        for class_id, data in CLASSES.items():
            trees = data["talent_trees"]
            self.assertEqual(len(trees), 3, class_id)
            abilities = {ability["id"]: ability for ability in data["abilities"]}
            seen = set()
            for tree in trees:
                self.assertTrue(tree["name"] and tree["description"])
                self.assertEqual([talent["tier"] for talent in tree["talents"]], [1, 2, 3, 4], tree["id"])
                for talent in tree["talents"]:
                    with self.subTest(talent=talent["id"]):
                        self.assertNotIn(talent["id"], seen)
                        seen.add(talent["id"])
                        self.assertTrue(talent["id"].startswith(tree["id"] + "_"))
                        self.assertIn(talent["ranks"], (1, 3, 5))
                        for effect in talent["effects"]:
                            self.assertIn(effect["kind"], EFFECT_KINDS)
                            if effect["kind"] == "stat":
                                self.assertIn(effect["key"], STATS)
                            if effect["kind"] in ("ability_pct", "cost", "cooldown") and effect["key"] != "all":
                                self.assertIn(effect["key"], abilities)
                            if effect["kind"] == "ability":
                                self.assertEqual(abilities[effect["key"]].get("talent"), talent["id"])
                        self.assertTrue(talents.describe(class_id, talent).endswith("."))
                last = tree["talents"][-1]
                self.assertTrue(any(effect["kind"] == "ability" for effect in last["effects"]),
                                "o último talento de cada árvore ensina uma habilidade")

    def test_points_and_tiers(self):
        self.assertEqual(talents.points_total(TALENT_START_LEVEL - 1), 0)
        self.assertEqual(talents.points_total(TALENT_START_LEVEL), 1)
        self.assertEqual(talents.points_total(60), 60 - TALENT_START_LEVEL + 1)
        # o tier 4 (13 pontos na árvore) só abre no nível 22
        self.assertEqual(talents.points_total(22), talents.TIER_REQUIREMENTS[4])


class TalentRulesTest(QuietTestCase):
    def test_learning_follows_points_ranks_and_tiers(self):
        session = make_session()
        player = session.player
        self.assertIn("nível 10", talents.learn_problem("guerreiro", player.level, player.talents, "armas_mestria"))
        level_up(session, 15)                       # 6 pontos
        self.assertEqual(player.talent_points, 6)
        self.assertIn("exige 5 pontos", talents.learn_problem("guerreiro", 15, player.talents, "armas_sangria"))
        for _ in range(5):
            player.learn_talent("armas_mestria")
        with self.assertRaises(ValueError):
            player.learn_talent("armas_mestria")    # já no máximo (5/5)
        player.learn_talent("armas_sangria")         # tier 2 aberto com 5 pontos na árvore
        self.assertEqual(player.talent_points, 0)
        with self.assertRaises(ValueError):
            player.learn_talent("furia_raiva")      # sem pontos livres
        self.assertEqual(talents.points_in_tree("guerreiro", player.talents, 0), 6)

    def test_bonuses_reach_the_hero_and_the_combat_engine(self):
        session = make_session(class_id="guerreiro")
        player = session.player
        level_up(session, 22)                      # 13 pontos: 5 + 5 + 3
        strength, max_hp, armor = player.stat("forca"), player.max_hp, player.armor
        for _ in range(5):
            player.learn_talent("protecao_robustez")       # +2% de armadura por ponto
        for _ in range(5):
            player.learn_talent("protecao_vigor")          # +2% de vida por ponto
        self.assertAlmostEqual(player.armor, armor * 1.10, delta=1)
        self.assertGreater(player.max_hp, max_hp)
        for _ in range(3):
            player.learn_talent("protecao_desvio")         # +1% de esquiva
        hero = Hero(player)
        self.assertGreater(hero.dodge, Hero(Player.from_dict({**player.to_dict(), "talents": {}})).dodge)
        self.assertEqual(player.stat("forca"), strength)

        session = make_session(class_id="mago")
        mage = session.player
        level_up(session, 15)
        plain = Hero(mage).damage_bonus("fogo")
        for _ in range(5):
            mage.learn_talent("fogo_intenso")              # +2% de dano de Fogo por ponto
        self.assertAlmostEqual(Hero(mage).damage_bonus("fogo"), plain + 0.10)
        self.assertAlmostEqual(Hero(mage).damage_bonus("gelo"), plain)
        bolt = ability(session, "bola_de_fogo")
        before = mage.ability_cost(bolt)
        mage.learn_talent("arcano_mente")
        self.assertEqual(mage.ability_cost(bolt), before)   # Mente Arcana não mexe no custo

    def test_tier_four_teaches_an_ability(self):
        session = make_session(class_id="ladino")
        player = session.player
        level_up(session, 23)                      # 13 pontos para abrir o tier 4, mais 1 para aprendê-lo
        self.assertNotIn("hemorragia", [a["id"] for a in player.abilities()])
        for talent_id, ranks in (("sutileza_sombras", 5), ("sutileza_oportunidade", 5),
                                 ("sutileza_furtividade", 3), ("sutileza_hemorragia", 1)):
            for _ in range(ranks):
                player.learn_talent(talent_id)
        self.assertIn("hemorragia", [a["id"] for a in player.abilities()])
        battle = fight(session, ("lobo_cinzento", 20))
        self.assertTrue(battle.ability_status(ability(session, "hemorragia"))[0])

    def test_celeste_prayer_resets_talents_for_a_fee(self):
        session = make_session()
        player = session.player
        level_up(session, 12)
        player.learn_talent("armas_mestria")
        player.learn_talent("armas_mestria")
        player.copper = 500
        node = npcs.get_npc("celeste").dialogue["esquecer_feito"]
        npcs.apply_effects(node["effects"], session)
        self.assertEqual(player.talents, {})
        self.assertEqual(player.talent_points, 3)
        self.assertEqual(player.copper, 300)

    def test_talents_survive_save_and_load(self):
        session = make_session()
        level_up(session, 11)
        session.player.learn_talent("furia_raiva")
        loaded = Player.from_dict(session.player.to_dict())
        self.assertEqual(loaded.talents, {"furia_raiva": 1})
        broken = Player.from_dict({**session.player.to_dict(), "talents": {"furia_raiva": 99, "inexistente": 2}})
        self.assertEqual(broken.talents, {"furia_raiva": 5})

    def test_talent_command_spends_points(self):
        session = make_session(class_id="sacerdote")
        level_up(session, 11)                      # 2 pontos
        self.type_in("1", "1", "")                 # aprende o primeiro talento duas vezes (e sai da tela)
        commands.dispatch(session, "talentos")
        self.assertEqual(session.player.talents, {"disciplina_vontade": 2})
        self.assertIn("agora está em 2/5", self.output.getvalue())


if __name__ == "__main__":
    unittest.main()
