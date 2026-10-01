"""Coleta e ofícios (Etapa 3): pontos de coleta, receitas, estações, bônus temporários,
bolsas, frascos e venenos em combate, NPCs dos ofícios, comandos e saves.

``FixedRandom(0.3)`` faz toda coleta acertar sem achados raros; ``FixedRandom(0.99)``
faz tudo errar; ``FixedRandom(0.01)`` acerta e ainda encontra o raro.
"""

import itertools
import unittest

from rpg import commands, crafting, npcs, save_system, ui, world
from rpg.combat import Battle, Charge, Hero
from rpg.data.recipes import RECIPES
from rpg.monsters import create_monster
from rpg.player import Player
from rpg.skills import xp_for_level
from tests.helpers import FixedRandom, QuietTestCase, TempSaveDirMixin, make_session, place, set_hour

AFLORAMENTO = (48, 17)
FORJA = (28, 16)
ESTALAGEM = (33, 14)
ACAMPAMENTO = (12, 14)
CARAVANA = (35, 9)
PIER = (41, 22)
SITIO = (36, 19)
SANTUARIO = (14, 5)
ENTRADA = (30, 18)


def set_skill(player, skill_id, level):
    player.skills.xp[skill_id] = xp_for_level(level)


def spot(session, node_id):
    landmark = session.map.landmark_at(*session.state.pos)
    return next(s for s in crafting.spots_at(landmark, session.state) if s.node_id == node_id)


def messages(session):
    return "\n".join(ui.strip_ansi(message) for message in session.pop_messages())


def fill_bag(player, item_id="adaga_curva"):
    while player.inventory.free_slots:
        player.inventory.add(item_id)


class GatheringTest(QuietTestCase):
    def test_mining_needs_a_pickaxe_and_gives_ore_and_xp(self):
        session = make_session(rng=FixedRandom(0.3))
        place(session, *AFLORAMENTO)
        session.pop_messages()
        copper = spot(session, "veio_cobre")
        self.assertIsNone(session.gather(copper, 5))
        self.assertIn("picareta", messages(session))
        session.player.inventory.add("picareta_velha")
        minutes = session.clock.minutes
        report = session.gather(copper, 5)
        self.assertEqual(session.player.inventory.count("minerio_cobre"), 5)
        self.assertEqual(report.xp, 5 * crafting.skill_xp(17.5))
        self.assertEqual(session.player.skills.xp["mineracao"], report.xp)
        self.assertEqual(session.clock.minutes - minutes, 5 * 3)
        self.assertIn("Mineração subiu para o nível", messages(session))

    def test_examining_the_outcrop_finds_an_old_pickaxe(self):
        session = make_session()
        place(session, *AFLORAMENTO)
        session.examine()
        self.assertEqual(session.player.inventory.count("picareta_velha"), 1)
        session.examine()
        self.assertEqual(session.player.inventory.count("picareta_velha"), 1)

    def test_nodes_deplete_and_recover_little_by_little(self):
        session = make_session(rng=FixedRandom(0.3))
        place(session, *AFLORAMENTO)
        session.player.inventory.add("picareta_velha")
        copper = spot(session, "veio_cobre")
        report = session.gather(copper, crafting.ALL)
        self.assertEqual((report.gathered, report.stopped), (8, "esgotado"))
        self.assertIn("[esgotado]", ui.strip_ansi(" ".join(session.describe().resources)))
        session.pop_messages()
        self.assertIsNone(session.gather(copper, 1))
        self.assertIn("esgotado", messages(session))
        session.advance_time(15)                       # 120 min para recuperar 8: um a cada 15
        self.assertEqual(crafting.node_left(session.state, copper), 1)
        session.advance_time(200)
        self.assertEqual(crafting.node_left(session.state, copper), 8)
        self.assertEqual(session.state.nodes, {})

    def test_bad_luck_ends_the_session(self):
        session = make_session(rng=FixedRandom(0.99))
        place(session, *AFLORAMENTO)
        session.player.inventory.add("picareta_velha")
        report = session.gather(spot(session, "veio_cobre"), 2)
        self.assertEqual((report.gathered, report.attempts, report.stopped), (0, 2 * crafting.ATTEMPTS_PER_ITEM, "azar"))

    def test_long_sessions_stop_after_four_hours(self):
        session = make_session(rng=FixedRandom(0.99))      # nada morde...
        place(session, *PIER)
        session.player.inventory.add("rede_pesca")
        report = session.gather(spot(session, "cardume_camaroes"), crafting.ALL)
        self.assertEqual((report.stopped, report.minutes), ("cansaco", crafting.MAX_SESSION_MINUTES))
        self.assertIn("pedem uma pausa", messages(session))

    def test_rare_finds(self):
        session = make_session(rng=FixedRandom(0.01))
        place(session, *AFLORAMENTO)
        session.player.inventory.add("picareta_velha")
        report = session.gather(spot(session, "veio_estanho"), 2)
        self.assertEqual(report.rare, ["granada_bruta", "granada_bruta"])
        self.assertEqual(session.player.inventory.count("granada_bruta"), 2)

    def test_better_tools_and_levels_raise_the_chance(self):
        player = make_session().player
        data = crafting.NODES["veio_cobre"]
        player.inventory.add("picareta_velha")
        base = crafting.gather_chance(player, data)
        player.inventory.add("picareta_ferro")
        self.assertAlmostEqual(crafting.gather_chance(player, data), base + 0.14)
        set_skill(player, "mineracao", 50)
        self.assertEqual(crafting.gather_chance(player, data), crafting.MAX_CHANCE)

    def test_skill_secret_reveals_the_iron_vein(self):
        session = make_session(rng=FixedRandom(0.3))
        place(session, *AFLORAMENTO)
        session.examine()                              # a picareta abandonada
        hint = " ".join(ui.strip_ansi(text) for text in session.examine())
        self.assertIn("(Mineração 15)", hint)
        self.assertNotIn("veio_ferro", [s.node_id for s in crafting.spots_at(session.map.landmark_at(*AFLORAMENTO),
                                                                             session.state)])
        set_skill(session.player, "mineracao", 15)
        session.examine()
        self.assertTrue(session.state.has_flag("veio_ferro_raso"))
        report = session.gather(spot(session, "veio_ferro"), 2)
        self.assertEqual(session.player.inventory.count("minerio_ferro"), 2)
        self.assertEqual(report.xp, 2 * crafting.skill_xp(35))

    def test_level_requirement(self):
        session = make_session(rng=FixedRandom(0.3))
        place(session, *PIER)
        session.player.inventory.add("vara_pesca")
        session.player.inventory.add("isca_minhoca", 5)
        self.assertIsNone(session.gather(spot(session, "cardume_sardinhas"), 1))
        self.assertIn("Pesca 5", messages(session))

    def test_fishing_spends_bait(self):
        session = make_session(rng=FixedRandom(0.3))
        place(session, *PIER)
        set_skill(session.player, "pesca", 5)
        sardines = spot(session, "cardume_sardinhas")
        session.player.inventory.add("vara_pesca")
        self.assertIsNone(session.gather(sardines, 5))
        self.assertIn("sem isca", messages(session))
        session.player.inventory.add("isca_minhoca", 3)
        report = session.gather(sardines, 5)
        self.assertEqual((report.gathered, report.bait_used, report.stopped), (3, 3, "isca"))
        self.assertEqual(session.player.inventory.count("isca_minhoca"), 0)
        session.player.inventory.add("rede_pesca")
        session.gather(spot(session, "cardume_camaroes"), 2)
        self.assertEqual(session.player.inventory.count("camarao_cru"), 2)

    def test_moon_lilies_only_open_at_night(self):
        session = make_session(rng=FixedRandom(0.3))
        place(session, *SANTUARIO)
        landmark = session.map.landmark_at(*SANTUARIO)
        self.assertEqual(crafting.spots_at(landmark, session.state), [])
        set_skill(session.player, "alquimia", 30)
        session.examine()
        lilies = spot(session, "lirios_da_lua")
        set_hour(session, 12)
        self.assertIsNone(session.gather(lilies, 1))
        self.assertIn("só se abrem à noite", messages(session))
        set_hour(session, 23)
        session.gather(lilies, 2)
        self.assertEqual(session.player.inventory.count("lirio_lua"), 2)

    def test_full_bag_stops_gathering(self):
        session = make_session(rng=FixedRandom(0.3))
        place(session, *SITIO)
        fill_bag(session.player)
        self.assertIsNone(session.gather(spot(session, "linhal"), 3))
        self.assertIn("mochila está cheia", messages(session))


class CraftingTest(QuietTestCase):
    def forge(self, rng=None):
        session = make_session(rng=rng or FixedRandom(0.3))
        place(session, *FORJA)
        set_hour(session, 10)
        session.pop_messages()
        return session

    def test_smelting_and_smithing(self):
        session = self.forge()
        player = session.player
        player.inventory.add("minerio_cobre", 3)
        player.inventory.add("minerio_estanho", 3)
        report = session.craft("barra_bronze", 10)
        self.assertEqual((report.made, player.inventory.count("barra_bronze")), (3, 3))
        self.assertEqual(player.inventory.count("minerio_cobre"), 0)
        self.assertIsNone(session.craft("adaga_bronze", 1))
        self.assertIn("martelo", messages(session))
        player.inventory.add("martelo_ferreiro")
        session.craft("adaga_bronze", 1)
        self.assertEqual(player.inventory.count("adaga_bronze"), 1)
        self.assertEqual(player.skills.xp["metalurgia"], 3 * crafting.skill_xp(6.2) + crafting.skill_xp(12.5))

    def test_the_forge_closes_at_night(self):
        session = self.forge()
        session.player.inventory.add("minerio_cobre")
        session.player.inventory.add("minerio_estanho")
        set_hour(session, 22)
        self.assertIsNone(session.craft("barra_bronze", 1))
        self.assertIn("trancada", messages(session))
        self.assertIn("[fechada]", ui.strip_ansi(" ".join(session.describe().stations)))

    def test_stations_are_required(self):
        session = make_session()
        session.player.inventory.add("minerio_cobre")
        session.player.inventory.add("minerio_estanho")
        self.assertIsNone(session.craft("barra_bronze", 1))
        text = messages(session)
        self.assertIn("Fornalha", text)
        self.assertIn("Forja do Martelo Rubro", text)

    def test_level_and_ingredients(self):
        session = self.forge()
        self.assertIsNone(session.craft("barra_ferro", 1))
        self.assertIn("Metalurgia 15", messages(session))
        self.assertIsNone(session.craft("barra_bronze", 1))
        self.assertIn("Faltam ingredientes", messages(session))
        session.player.inventory.add("minerio_cobre", 2)
        session.player.inventory.add("minerio_estanho", 1)
        self.assertEqual(session.craft("barra_bronze", 5).made, 1)

    def test_iron_can_crumble_until_the_smith_gets_good(self):
        session = self.forge(FixedRandom(0.1))
        set_skill(session.player, "metalurgia", 15)
        session.player.inventory.add("minerio_ferro", 4)
        report = session.craft("barra_ferro", 2)
        self.assertEqual((report.made, report.failed), (0, 2))
        self.assertIn("esfarelou", messages(session))
        set_skill(session.player, "metalurgia", 45)
        self.assertEqual(session.craft("barra_ferro", 2).made, 2)

    def test_burn_chance(self):
        self.assertEqual(crafting.scaled_chance([0.5, 18], 1, 1), 0.5)
        self.assertAlmostEqual(crafting.scaled_chance([0.5, 21], 1, 11), 0.25)
        self.assertEqual(crafting.scaled_chance([0.5, 18], 1, 18), 0)
        self.assertEqual(crafting.scaled_chance(None, 1, 1), 0)
        camp = make_session(rng=FixedRandom(0.4))
        place(camp, *CARAVANA)
        camp.player.inventory.add("camarao_cru", 2)
        self.assertEqual(camp.craft("camarao_assado", 1).burnt, 1)          # 0.4 < 50%
        self.assertEqual(camp.player.inventory.count("comida_queimada"), 1)
        inn = make_session(rng=FixedRandom(0.4))
        place(inn, *ESTALAGEM)
        inn.player.inventory.add("camarao_cru", 2)
        self.assertEqual(inn.craft("camarao_assado", 1).made, 1)           # a cozinha queima menos: 37,5%
        set_skill(camp.player, "culinaria", 18)
        self.assertEqual(camp.craft("camarao_assado", 1).made, 1)

    def test_the_hunters_campfire_needs_a_torch(self):
        session = make_session(rng=FixedRandom(0.99))
        place(session, *ACAMPAMENTO)
        session.player.inventory.add("camarao_cru", 4)
        torches = session.player.inventory.count("tocha")
        session.craft("camarao_assado", 2)
        self.assertEqual(session.player.inventory.count("tocha"), torches - 1)
        session.player.inventory.remove("tocha", torches - 1)
        self.assertIsNone(session.craft("camarao_assado", 2))
        self.assertIn("apagada", messages(session))

    def test_crafted_clothes_take_the_hero_color(self):
        session = make_session()
        player = session.player
        set_skill(player, "alfaiataria", 4)
        player.inventory.add("kit_costura")
        player.inventory.add("fio_linho", 3)
        session.craft("tunica_linho", 1)
        self.assertEqual(player.inventory.find("tunica_linho").dye, player.appearance.armor_color)

    def test_full_bag_returns_the_ingredients(self):
        session = make_session()
        player = session.player
        set_skill(player, "alfaiataria", 6)
        player.inventory.add("kit_costura")
        player.inventory.add("fio_linho", 10)
        fill_bag(player)
        report = session.craft("bolsa_linho", 1)
        self.assertEqual((report.made, report.stopped), (0, "mochila"))
        self.assertEqual(player.inventory.count("fio_linho"), 10)

    def test_alchemy_anywhere_but_strong_brews_need_the_cauldron(self):
        session = make_session()
        player = session.player
        player.inventory.add("almofariz")
        player.inventory.add("folha_charco", 2)
        player.inventory.add("frasco_vazio", 2)
        potions = player.inventory.count("pocao_cura_menor")
        session.craft("pocao_cura_menor", 1)          # em qualquer lugar, só com o almofariz
        self.assertEqual(player.inventory.count("pocao_cura_menor"), potions + 1)
        set_skill(player, "alquimia", 15)
        player.inventory.add("flor_breu", 2)
        self.assertIsNone(session.craft("oleo_inflamavel", 1))
        self.assertIn("Caldeirão", messages(session))

    def test_level_ups_announce_new_recipes(self):
        session = self.forge()
        session.player.inventory.add("minerio_cobre", 5)
        session.player.inventory.add("minerio_estanho", 5)
        session.craft("barra_bronze", 5)
        self.assertIn("Metalurgia subiu para o nível 2! Novo: Machadinha de Bronze.", messages(session))

    def test_unlocks(self):
        self.assertIn("Veio de Ferro Raso", crafting.unlocks("mineracao", 15))
        self.assertIn("Barra de Ferro", crafting.unlocks("metalurgia", 15))
        self.assertEqual(crafting.next_unlock("mineracao", 1), (15, ["Veio de Ferro Raso", "Veio de Ferro"]))
        self.assertIsNone(crafting.next_unlock("mineracao", 99))


class BuffTest(QuietTestCase):
    def eat(self, session, item_id):
        session.player.inventory.add(item_id)
        session.use_item(session.player.inventory.find(item_id))

    def test_food_buff_raises_stats_and_expires(self):
        session = make_session()
        player = session.player
        intellect = player.stat("intelecto")
        self.eat(session, "torta_truta")
        self.assertEqual(player.stat("intelecto"), intellect + 3)
        self.assertIn("Bem alimentado", ui.strip_ansi("\n".join(screen_lines(session))))
        session.advance_time(120)
        self.assertEqual(player.stat("intelecto"), intellect)
        self.assertIn("O efeito de Bem alimentado terminou.", messages(session))

    def test_one_buff_per_group(self):
        session = make_session()
        self.eat(session, "torta_truta")
        self.eat(session, "espetinho_lobo")
        self.eat(session, "elixir_javali")
        self.assertEqual(sorted(buff["id"] for buff in session.player.buffs), ["bem_alimentado", "elixir_javali"])
        self.assertEqual(session.player.buffs[0]["stats"], {"forca": 3, "agilidade": 2})

    def test_vigor_buff_ending_clamps_hp(self):
        session = make_session()
        player = session.player
        base = player.max_hp
        self.eat(session, "elixir_javali")
        self.assertEqual(player.max_hp, base + 8)
        player.hp = player.max_hp
        session.advance_time(90)
        self.assertEqual(player.hp, base)

    def test_bat_eyes_widen_the_view(self):
        session = make_session()
        set_hour(session, 23)
        radius = session.vision_radius()
        self.eat(session, "elixir_morcego")
        self.assertEqual(session.vision_radius(), radius + 1)

    def test_flasks_only_in_combat(self):
        session = make_session()
        session.player.inventory.add("oleo_inflamavel")
        self.assertFalse(session.use_item(session.player.inventory.find("oleo_inflamavel")))
        self.assertIn("só serve no meio de uma luta", messages(session))
        self.assertEqual(session.player.inventory.count("oleo_inflamavel"), 1)

    def test_weapon_poison_adds_nature_damage(self):
        session = make_session()
        self.eat(session, "veneno_aranha")
        rng = FixedRandom(0.5)
        battle = Battle(Hero(session.player), [create_monster("javali_espinhento", 4, rng)], rng)
        battle.start()
        battle.attack()
        self.assertIn("Lâmina envenenada atinge Javali Espinhento", "\n".join(battle.log))

    def test_fire_flask_breaks_a_fire_seal(self):
        session = make_session()
        session.player.inventory.add("oleo_inflamavel")
        rng = FixedRandom(0.5)
        spider = create_monster("aranha_da_mata", 3, rng)
        battle = Battle(Hero(session.player), [spider], rng)
        battle.start()
        web = next(a for a in spider.abilities if a.get("charge"))
        spider.charging = Charge(web, 1, ["fogo"])
        self.assertTrue(battle.use_item("oleo_inflamavel", 0))
        self.assertIsNone(spider.charging)
        log = "\n".join(battle.log)
        self.assertIn("Óleo Inflamável atinge Aranha da Mata", log)
        self.assertIn("Fraqueza!", log)
        self.assertEqual(session.player.inventory.count("oleo_inflamavel"), 0)

    def test_food_cannot_be_eaten_in_combat(self):
        session = make_session()
        session.player.inventory.add("torta_truta")
        rng = FixedRandom(0.5)
        battle = Battle(Hero(session.player), [create_monster("lobo_faminto", 2, rng)], rng)
        battle.start()
        self.assertFalse(battle.use_item("torta_truta"))


def screen_lines(session):
    from rpg import screens
    return screens.hud(session, 100)


class BagTest(unittest.TestCase):
    def test_bags_expand_the_backpack(self):
        player = make_session().player
        player.inventory.add("bolsa_linho")
        player.equip(player.inventory.find("bolsa_linho"))
        self.assertEqual(player.inventory.capacity, 20)
        player.inventory.add("bolsa_la")
        player.equip(player.inventory.find("bolsa_la"))
        self.assertEqual(player.inventory.capacity, 22)
        self.assertEqual(player.inventory.count("bolsa_linho"), 1)

    def test_cannot_remove_a_bag_full_of_things(self):
        player = make_session().player
        player.inventory.add("bolsa_linho")
        player.equip(player.inventory.find("bolsa_linho"))
        fill_bag(player)
        with self.assertRaises(ValueError):
            player.unequip("bolsa")
        player.inventory.add("bolsa_la")      # não cabe: a mochila está cheia
        self.assertEqual(player.inventory.count("bolsa_la"), 0)
        player.inventory.take(player.inventory.find("adaga_curva"), 1)
        player.inventory.add("bolsa_la")
        player.equip(player.inventory.find("bolsa_la"))          # a maior entra no lugar da menor
        self.assertEqual(player.inventory.capacity, 22)

    def test_capacity_survives_loading(self):
        player = make_session().player
        player.inventory.add("bolsa_seda")
        player.equip(player.inventory.find("bolsa_seda"))
        loaded = Player.from_dict(player.to_dict())
        self.assertEqual(loaded.inventory.capacity, 24)


class CraftNpcTest(QuietTestCase):
    def options(self, session, npc_id):
        node = npcs.get_npc(npc_id).dialogue["inicio"]
        return [option["next"] for option in npcs.node_options(node, session.state, met=True)]

    def test_brom_gives_a_hammer_once_and_praises_the_first_bar(self):
        session = make_session()
        brom = npcs.get_npc("brom")
        self.assertIn("metalurgia", self.options(session, "brom"))
        npcs.apply_effects(brom.dialogue["metalurgia"]["effects"], session)
        self.assertEqual(session.player.inventory.count("martelo_ferreiro"), 1)
        self.assertNotIn("metalurgia", self.options(session, "brom"))
        self.assertIn("forja_ajuda", self.options(session, "brom"))
        self.assertNotIn("primeira_barra", self.options(session, "brom"))
        session.player.inventory.add("barra_bronze")
        self.assertIn("primeira_barra", self.options(session, "brom"))

    def test_teachers_hand_out_starter_tools(self):
        session = make_session()
        for npc_id, node_id, item_id in (("anselmo", "pescar", "rede_pesca"), ("brigida", "remedios", "almofariz"),
                                         ("marta", "cozinhar", "carne_javali")):
            npcs.apply_effects(npcs.get_npc(npc_id).dialogue[node_id]["effects"], session)
            self.assertGreater(session.player.inventory.count(item_id), 0, npc_id)
        self.assertEqual(session.player.inventory.count("frasco_vazio"), 3)

    def test_tobias_pays_rat_tails_in_flour(self):
        session = make_session()
        session.player.inventory.add("rabo_rato", 6)
        self.assertNotIn("rabos", self.options(session, "tobias"))
        npcs.apply_effects(npcs.get_npc("tobias").dialogue["ratos"]["effects"], session)
        self.assertIn("rabos", self.options(session, "tobias"))
        npcs.apply_effects(npcs.get_npc("tobias").dialogue["rabos"]["effects"], session)
        self.assertEqual((session.player.inventory.count("rabo_rato"), session.player.inventory.count("farinha")),
                         (1, 5))
        self.assertNotIn("rabos", self.options(session, "tobias"))

    def test_zahir_opens_a_bale_after_explaining(self):
        session = make_session()
        self.assertNotIn("fardo", self.options(session, "zahir"))
        npcs.apply_effects(npcs.get_npc("zahir").dialogue["mercadorias"]["effects"], session)
        self.assertIn("fardo", self.options(session, "zahir"))


class CommandTest(QuietTestCase):
    def test_mine_command(self):
        session = make_session(rng=FixedRandom(0.3))
        place(session, *AFLORAMENTO)
        session.player.inventory.add("picareta_velha")
        commands.dispatch(session, "minerar cobre 3")
        self.assertEqual(session.player.inventory.count("minerio_cobre"), 3)
        self.assertTrue(session.needs_redraw)
        self.type_in("2")                      # dois veios: escolhe o de estanho
        commands.dispatch(session, "minerar 2")
        self.assertEqual(session.player.inventory.count("minerio_estanho"), 2)

    def test_forge_menu_and_quantity(self):
        session = make_session(rng=FixedRandom(0.3))
        place(session, *FORJA)
        set_hour(session, 10)
        session.player.inventory.add("minerio_cobre", 4)
        session.player.inventory.add("minerio_estanho", 4)
        session.player.inventory.add("martelo_ferreiro")
        self.type_in("t")                      # só a barra de bronze tem ingredientes... mas o menu lista as outras
        commands.dispatch(session, "forjar barra")
        self.assertEqual(session.player.inventory.count("barra_bronze"), 4)
        self.type_in("1", "")                  # adaga de bronze, Enter = 1
        commands.dispatch(session, "forjar")
        self.assertEqual(session.player.inventory.count("adaga_bronze"), 1)

    def test_nothing_to_do_here(self):
        session = make_session()
        commands.dispatch(session, "minerar")
        commands.dispatch(session, "cozinhar")
        output = ui.strip_ansi(self.output.getvalue())
        self.assertIn("Não há nada para minerar aqui", output)
        self.assertIn("Fogo de cozinha", output)

    def test_screens(self):
        session = make_session()
        self.type_in("", "")
        commands.dispatch(session, "receitas metal")
        commands.dispatch(session, "pericias")
        output = ui.strip_ansi(self.output.getvalue())
        self.assertIn("Barra de Bronze", output)
        self.assertIn("Próximo, no nível 15: Veio de Ferro Raso", output)

    def test_location_panel_lists_crafts(self):
        session = make_session()
        place(session, *FORJA)
        set_hour(session, 10)
        view = session.describe()
        self.assertEqual(view.actions, ["forjar"])
        self.assertEqual([ui.strip_ansi(name) for name in view.stations], ["Fornalha do Brom", "Bigorna do Brom"])
        place(session, *SITIO)
        self.assertEqual(session.describe().actions, ["colher", "costurar"])

    def test_throw_a_flask_through_the_battle_screen(self):
        from rpg import battle_ui
        session = make_session(rng=FixedRandom(0.5))
        place(session, 12, 3)
        session.player.inventory.add("oleo_inflamavel", 2)
        session.hunt()
        stream = itertools.chain(["1", "i", "óleo"], itertools.repeat("a"))
        ui.input_func = lambda _prompt: next(stream)
        battle_ui.run(session)
        self.assertEqual(session.player.inventory.count("oleo_inflamavel"), 1)
        self.assertIn("Óleo Inflamável atinge", ui.strip_ansi(self.output.getvalue()))


class CraftingSaveTest(TempSaveDirMixin):
    def test_nodes_and_buffs_are_saved(self):
        session = make_session(rng=FixedRandom(0.3))
        place(session, *AFLORAMENTO)
        session.player.inventory.add("picareta_velha")
        session.player.inventory.add("torta_truta")
        session.gather(spot(session, "veio_cobre"), 3)
        session.use_item(session.player.inventory.find("torta_truta"))
        loaded = save_system.load_game(session.save())
        self.assertEqual(loaded.nodes, session.state.nodes)
        self.assertEqual(loaded.player.buffs, session.player.buffs)
        self.assertEqual(loaded.player.stat("intelecto"), session.player.stat("intelecto"))


class WorldCraftTest(unittest.TestCase):
    def test_every_station_and_gathering_spot_is_reachable_on_foot(self):
        from tests.test_world import reachable
        for map_id in world.map_ids():
            game_map = world.get_map(map_id)
            tiles = reachable(game_map, game_map.start)
            for landmark in game_map.landmarks.values():
                if landmark.resources or landmark.stations:
                    self.assertIn(landmark.pos, tiles, landmark.id)

    def test_recipes_in_order(self):
        levels = [RECIPES[recipe_id]["level"] for recipe_id in crafting.recipes_for("alquimia")]
        self.assertEqual(levels, sorted(levels))


if __name__ == "__main__":
    unittest.main()
