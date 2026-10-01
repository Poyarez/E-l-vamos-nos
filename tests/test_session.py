"""Regras da exploração: movimento, tempo, visão, descobertas, segredos, NPCs e comandos."""

import unittest

from rpg import commands, npcs
from tests.helpers import QuietTestCase, make_session, place, set_hour


class MovementTest(QuietTestCase):
    def test_new_game_starts_at_village_entrance(self):
        session = make_session()
        self.assertEqual(session.state.pos, (30, 18))
        self.assertIn("entrada_vila", session.state.discovered)
        self.assertIn("vila_primordia", session.state.regions)
        self.assertEqual(session.player.xp, 0)
        self.assertIn((30, 15), session.state.explored_on("vale_primordia"))

    def test_step_costs_terrain_time(self):
        session = make_session()
        start = session.clock.minutes
        self.assertEqual(session.walk("n"), 1)
        self.assertEqual(session.state.pos, (30, 17))
        self.assertEqual(session.clock.minutes - start, 5)   # ruas da vila: 5 minutos

    def test_water_blocks_movement(self):
        session = make_session()
        place(session, 21, 8)
        self.assertEqual(session.walk("l"), 0)
        self.assertEqual(session.state.pos, (21, 8))
        self.assertTrue(any("águas" in message for message in session.pop_messages()))

    def test_multi_step_walk_stops_on_discovery(self):
        session = make_session()
        moved = session.walk("n", 10)
        self.assertEqual(moved, 3)
        self.assertEqual(session.state.pos, (30, 15))       # parou na Praça do Poço Antigo
        self.assertIn("praca_poco", session.state.discovered)
        self.assertEqual(session.player.xp, 15)

    def test_new_region_grants_xp(self):
        session = make_session()
        session.walk("s")
        self.assertIn("campos_dourados", session.state.regions)
        self.assertEqual(session.player.xp, 30)

    def test_lookout_reveals_map(self):
        session = make_session()
        place(session, 55, 10)
        explored = session.state.explored_on("vale_primordia")
        self.assertIn((45, 15), explored)   # 10 tiles de distância: só o mirante revela

    def test_locked_edge_portal(self):
        session = make_session()
        place(session, 40, 0)
        self.assertEqual(session.walk("n"), 0)
        self.assertEqual(session.state.map_id, "vale_primordia")
        self.assertTrue(any("Pedravale" in message for message in session.pop_messages()))

    def test_travel_uses_known_paths(self):
        session = make_session()
        session.walk("n", 3)
        session.walk("s", 3)
        self.assertTrue(session.travel_to(session.map.landmarks["praca_poco"]))
        self.assertEqual(session.state.pos, (30, 15))
        self.assertFalse(session.travel_to(session.map.landmarks["carvalho_anciao"]))


class TimeAndVisionTest(QuietTestCase):
    def test_vision_shrinks_at_night(self):
        session = make_session()
        set_hour(session, 10)
        self.assertGreaterEqual(session.vision_radius(), 2)
        set_hour(session, 23)
        self.assertEqual(session.vision_radius(), 1)

    def test_sleeping_at_inn_until_morning(self):
        session = make_session()
        place(session, 33, 14)
        set_hour(session, 22)
        session.player.hp = 1
        day = session.clock.day
        session.rest()
        self.assertEqual((session.clock.day, session.clock.hour), (day + 1, 7))
        self.assertEqual(session.player.hp, session.player.max_hp)
        self.assertTrue(session.pending_autosave)

    def test_weather_is_stable_within_a_day(self):
        session = make_session()
        first = session.clock.weather_id()
        session.advance_time(600)
        if session.clock.day == 1:
            self.assertEqual(session.clock.weather_id(), first)


class SecretTest(QuietTestCase):
    def test_waterfall_secret_grotto_and_chest(self):
        session = make_session()
        place(session, 23, 3)
        self.assertFalse(session.use_verb("entrar"), "a passagem não pode existir antes do segredo")
        xp_before = session.player.xp
        session.examine()
        self.assertTrue(session.state.has_flag("segredo_cachoeira"))
        self.assertEqual(session.player.xp, xp_before + 120)
        self.assertIn("segredo_cachoeira", {entry.id for entry in session.state.journal})

        self.assertTrue(session.use_verb("entrar"))
        self.assertEqual(session.state.map_id, "gruta_veu_prata")
        place(session, 11, 1)
        copper = session.player.copper
        session.examine()
        self.assertEqual(session.player.inventory.count("pingente_pedra_da_lua"), 1)
        self.assertEqual(session.player.copper, copper + 4500)
        session.examine()   # o baú não se enche de novo
        self.assertEqual(session.player.inventory.count("pingente_pedra_da_lua"), 1)

        place(session, 4, 8)
        session.walk("s")
        self.assertEqual((session.state.map_id, session.state.pos), ("vale_primordia", (23, 3)))


class NpcTest(QuietTestCase):
    def test_schedule(self):
        session = make_session()
        set_hour(session, 10)
        self.assertEqual([n.id for n in npcs.npcs_at(session.state, "vale_primordia", 41, 22)], ["anselmo"])
        set_hour(session, 22)
        self.assertEqual(npcs.npcs_at(session.state, "vale_primordia", 41, 22), [])
        self.assertIn("renna", [n.id for n in npcs.npcs_at(session.state, "vale_primordia", 33, 14)])

    def test_scripted_conversation_records_clues(self):
        session = make_session()
        place(session, 28, 13)
        set_hour(session, 10)
        self.type_in("2", "5")   # "Por que o vale precisa de ajuda?" e depois "Até logo"
        npcs.run_dialogue(session, npcs.get_npc("ysolde"))
        self.assertIn("ysolde", session.state.met)
        self.assertIn("rumor_tremores", {entry.id for entry in session.state.journal})
        self.assertTrue(session.state.has_flag("visto:ysolde:problemas"))

    def test_conditional_options(self):
        session = make_session()
        options = npcs.node_options(npcs.get_npc("ysolde").dialogue["inicio"], session.state, met=False)
        self.assertNotIn("primordial", [option["next"] for option in options])
        session.state.flags["lenda_primordial"] = True
        options = npcs.node_options(npcs.get_npc("ysolde").dialogue["inicio"], session.state, met=False)
        self.assertIn("primordial", [option["next"] for option in options])


class CommandTest(QuietTestCase):
    def test_dispatch_movement_aliases_and_unknown(self):
        session = make_session()
        commands.dispatch(session, "NORTE 2")
        self.assertEqual(session.state.pos, (30, 16))
        commands.dispatch(session, "2 s")
        self.assertEqual(session.state.pos, (30, 18))
        commands.dispatch(session, "mapx")
        self.assertIn("Você quis dizer 'mapa'?", self.output.getvalue())

    def test_accents_do_not_matter(self):
        session = make_session()
        self.type_in("")
        commands.dispatch(session, "INVENTÁRIO")
        self.assertIn("MOCHILA", self.output.getvalue())

    def test_go_to_known_place(self):
        session = make_session()
        session.walk("n", 3)
        session.walk("s", 3)
        commands.dispatch(session, "ir praça")
        self.assertEqual(session.state.pos, (30, 15))

    def test_every_full_screen_renders(self):
        session = make_session()
        for name in ("mapa", "ficha", "inventario", "pericias", "habilidades", "diario", "ajuda"):
            self.type_in("")
            commands.dispatch(session, name)
        commands.dispatch(session, "examinar")
        commands.dispatch(session, "hora")
        self.assertIn("PERÍCIAS", self.output.getvalue())


if __name__ == "__main__":
    unittest.main()
