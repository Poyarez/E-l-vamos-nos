"""Combate (Etapa 2): regras, lutas reprodutíveis, selos, efeitos, recargas, combos,
vitória e derrota, encontros, equipamento, consumíveis, comércio e bestiário.

As lutas usam ``FixedRandom(0.5)``: todo golpe acerta, nada é crítico e as criaturas só
usam habilidades com chance acima de 50% — assim cada turno é previsível.
"""

import itertools
import random
import re
import unittest

from rpg import battle_ui, combat, commands, monsters, npcs, save_system, shop, ui, world
from rpg.combat import Battle, Charge, Hero, armor_mitigation
from rpg.data.items import ITEMS
from rpg.session import ENCOUNTER_GRACE, RESPAWN, BattleRequest
from tests.helpers import FixedRandom, QuietTestCase, TempSaveDirMixin, make_session, place, set_hour

FOREST = (12, 3)       # Floresta Sussurrante, longe de qualquer local


def fight(session, *enemies, rng=None, **options):
    """Começa uma luta do herói da sessão contra ``(criatura, nível)``."""
    rng = rng or FixedRandom()
    monsters_ = [monsters.create_monster(template_id, level, rng) for template_id, level in enemies]
    battle = Battle(Hero(session.player), monsters_, rng, knowledge=session.state.knowledge(), **options)
    battle.summon = lambda template_id, level: monsters.create_monster(template_id, level, rng)
    battle.start()
    return battle


def win(battle, limit=300):
    """Vence na marra: o herói ataca e é curado a cada turno."""
    for _ in range(limit):
        if battle.outcome:
            break
        battle.hero.hp = battle.hero.max_hp
        battle.attack()
    return battle.outcome


def charging(monster, locks):
    """Faz a criatura começar a concentrar seu golpe especial com os selos indicados."""
    ability = next(a for a in monster.abilities if a.get("charge"))
    monster.charging = Charge(ability, 1, list(locks))
    return ability


def text(battle):
    return "\n".join(battle.log)


def ability(session, ability_id):
    return next(a for a in session.player.abilities() if a["id"] == ability_id)


class RulesTest(unittest.TestCase):
    def test_armor_mitigation(self):
        self.assertEqual(armor_mitigation(0, 10), 0)
        self.assertAlmostEqual(armor_mitigation(485, 1), 0.5)
        self.assertEqual(armor_mitigation(10 ** 6, 1), 0.75)

    def test_kill_xp_follows_the_classic_formula(self):
        self.assertEqual(monsters.kill_xp(1, 1), 100)       # (1 × 5 + 45) × XP_RATE
        self.assertEqual(monsters.kill_xp(5, 7), 154)       # +5% por nível acima
        self.assertEqual(monsters.kill_xp(5, 12), 168)      # ... até 4 níveis
        self.assertEqual(monsters.kill_xp(10, 6), 81)       # abaixo: "diferença zero" = 7
        self.assertEqual(monsters.kill_xp(10, 3), 0)
        self.assertEqual(monsters.kill_xp(5, 5, elite=True), 2 * monsters.kill_xp(5, 5))

    def test_difficulty_colors(self):
        self.assertEqual(monsters.con_color(5, 10), "bright_red")
        self.assertEqual(monsters.con_color(5, 8), "red")
        self.assertEqual(monsters.con_color(5, 7), "bright_yellow")
        self.assertEqual(monsters.con_color(5, 3), "bright_yellow")
        self.assertEqual(monsters.con_color(5, 2), "bright_green")
        self.assertEqual(monsters.con_color(10, 3), "gray")

    def test_monster_factory_follows_the_level_curve(self):
        wolf = monsters.create_monster("lobo_cinzento", 4)
        hp, damage, armor = monsters.stat_curve(4)
        self.assertEqual((wolf.level, wolf.max_hp, wolf.hp, wolf.armor), (4, round(hp), round(hp), round(armor)))
        self.assertAlmostEqual(sum(wolf.damage) / 2, damage * 1.05)
        rng = random.Random(3)
        levels = {monsters.create_monster("rato_gigante", rng=rng).level for _ in range(40)}
        self.assertEqual(levels, {1, 2, 3})
        with self.assertRaises(KeyError):
            monsters.create_monster("dragao")

    def test_boss_loot_is_guaranteed(self):
        boss = monsters.create_monster("presa_de_gelo")
        for seed in range(5):
            items, copper = monsters.roll_loot(boss, random.Random(seed))
            ids = [item_id for item_id, _quantity in items]
            self.assertIn("pele_presa_de_gelo", ids)
            self.assertEqual(len(set(ids) & {"presa_gelida", "manto_alfa_branco", "anel_uivo_gelido"}), 1)
            self.assertTrue(250 <= copper <= 500)

    def test_loot_chances(self):
        rat = monsters.create_monster("rato_gigante", 1)
        rng = random.Random(7)
        drops = sum(bool(monsters.roll_loot(rat, rng)[0]) for _ in range(2000))
        self.assertAlmostEqual(drops / 2000, 0.65, delta=0.04)


class BattleTest(unittest.TestCase):
    def test_same_level_fight(self):
        session = make_session()
        battle = fight(session, ("rato_gigante", 1))
        for _ in range(10):
            if battle.outcome:
                break
            battle.attack()
        self.assertEqual(battle.outcome, combat.OUTCOME_VICTORY)
        self.assertEqual([enemy.template_id for enemy in battle.defeated], ["rato_gigante"])
        self.assertGreater(session.player.hp, session.player.max_hp // 2)
        self.assertGreater(session.player.resource, 0, "o guerreiro ganha Raiva ao bater e apanhar")

    def test_stun_costs_exactly_one_turn(self):
        session = make_session()
        battle = fight(session, ("lobo_faminto", 2))
        hp = session.player.hp
        self.assertTrue(battle.use_ability("investida"))
        self.assertEqual(session.player.hp, hp, "o lobo atordoado não ataca")
        self.assertEqual(session.player.resource, 15)
        battle.attack()
        self.assertLess(session.player.hp, hp)
        self.assertEqual(text(battle).count("perde a vez"), 1)
        usable, reason = battle.ability_status(ability(session, "investida"))
        self.assertFalse(usable)
        self.assertIn("primeiro turno", reason)

    def test_hero_stunned_by_a_special_loses_one_turn(self):
        session = make_session()
        battle = fight(session, ("aranha_da_mata", 3))
        charging(battle.enemies[0], [])
        battle.analyze()
        self.assertEqual(battle.round, 3)
        self.assertEqual(text(battle).count("Você perde a vez (teia)"), 1)
        self.assertIsNone(battle.hero.incapacitation())

    def test_breaking_every_lock_cancels_the_special(self):
        session = make_session()
        battle = fight(session, ("javali_espinhento", 3))
        boar = battle.enemies[0]
        charging(boar, ["fisico"])
        hp = session.player.hp
        battle.attack()
        self.assertIsNone(boar.charging)
        self.assertIn("Todos os selos rompidos", text(battle))
        self.assertEqual(session.player.hp, hp, "sem concentração, o javali perde a vez")

    def test_breaking_some_locks_weakens_the_special(self):
        def damage_taken(action):
            session = make_session()
            battle = fight(session, ("javali_espinhento", 3))
            charging(battle.enemies[0], ["gelo", "fisico"])
            hp = session.player.hp
            action(battle)
            return hp - session.player.hp, battle

        full, _ = damage_taken(lambda battle: battle.analyze())
        weakened, battle = damage_taken(lambda battle: battle.attack())
        self.assertIn("1 selo rompido", text(battle))
        self.assertAlmostEqual(weakened, full * (1 - 0.75 / 2), delta=1)

    def test_kick_interrupts_the_special(self):
        session = make_session(class_id="ladino")
        session.player.level = 10
        session.player.restore()
        battle = fight(session, ("aranha_da_mata", 5))
        spider = battle.enemies[0]
        charging(spider, ["fogo", "fisico"])
        hp = session.player.hp
        self.assertTrue(battle.use_ability("chute"))
        self.assertIn("Você interrompe Teia Pegajosa", text(battle))
        self.assertIsNone(spider.charging)
        self.assertEqual(session.player.hp, hp)
        self.assertIn("recarga", battle.ability_status(ability(session, "chute"))[1])

    def test_stealth_cooldown_and_guaranteed_crit(self):
        session = make_session(class_id="ladino")
        battle = fight(session, ("lobo_faminto", 2))
        hp = session.player.hp
        self.assertTrue(battle.use_ability("furtividade"))
        self.assertEqual(session.player.hp, hp)
        self.assertIn("procura você nas sombras", text(battle))
        stealth = ability(session, "furtividade")
        self.assertIn("4 turnos", battle.ability_status(stealth)[1])
        battle.attack()
        self.assertIn("CRÍTICO!", text(battle))
        while not battle.ability_status(stealth)[0]:
            battle.defend()
        self.assertEqual(battle.round, 6)     # usada na rodada 1, recarga de 4 turnos

    def test_combo_points_feed_the_finisher(self):
        session = make_session(class_id="ladino")
        battle = fight(session, ("javali_espinhento", 5))
        hero, boar = battle.hero, battle.enemies[0]
        self.assertIn("combo", battle.ability_status(ability(session, "eviscerar"))[1])
        battle.use_ability("golpe_sinistro")
        battle.use_ability("golpe_sinistro")
        self.assertEqual(hero.combo, 2)
        hp = boar.hp
        self.assertTrue(battle.use_ability("eviscerar"))
        self.assertEqual(hero.combo, 0)
        self.assertLess(boar.hp, hp)
        self.assertIn("Eviscerar (2 combo)", text(battle))

    def test_resources_are_spent_and_regenerated(self):
        session = make_session(class_id="ladino")
        battle = fight(session, ("javali_espinhento", 5))
        battle.use_ability("golpe_sinistro")
        self.assertEqual(session.player.resource, 100 - 40 + combat.ENERGY_PER_TURN)
        mage = make_session(class_id="mago")
        battle = fight(mage, ("javali_espinhento", 5))
        mana = mage.player.resource
        battle.use_ability("bola_de_fogo")
        self.assertEqual(mage.player.resource, mana - 30 + battle.hero.mana_regen())
        mage.player.resource = 0
        battle.use_ability("bola_de_fogo")
        self.assertIn("Mana insuficiente", battle.log[-1])

    def test_periodic_damage_ticks_once_per_turn(self):
        session = make_session()
        session.player.level = 4
        session.player.restore()
        battle = fight(session, ("javali_espinhento", 5))
        battle.hero.resource = 10
        self.assertTrue(battle.use_ability("dilacerar"))
        for _ in range(4):
            battle.defend()
        self.assertEqual(len(re.findall(r"Sangrando: Javali Espinhento sofre \d+ de dano", text(battle))), 3)
        self.assertIsNone(battle.enemies[0].find("dilacerar"))

    def test_weakness_is_discovered_and_shown(self):
        session = make_session(class_id="mago")
        battle = fight(session, ("lobo_faminto", 2))
        wolf = battle.enemies[0]
        self.assertIn("?", combat.describe_knowledge(wolf, battle.known(wolf))[0])
        battle.use_ability("bola_de_fogo")
        self.assertIn("Fraqueza!", text(battle))
        self.assertIn("fraco:fogo", battle.knowledge["lobo_faminto"])
        battle.analyze()
        self.assertNotIn("?", ui.strip_ansi(combat.describe_knowledge(wolf, battle.known(wolf))[0]))

    def test_bosses_cannot_be_fled_nor_stunned(self):
        session = make_session()
        battle = fight(session, ("presa_de_gelo", 7), allow_flee=False)
        self.assertFalse(battle.flee())
        self.assertIsNone(battle.outcome)
        battle.use_ability("investida")
        self.assertIn("imune", text(battle))
        self.assertIsNone(battle.enemies[0].incapacitation())

    def test_summons_join_the_fight(self):
        session = make_session()
        battle = fight(session, ("varek_domador", 6))
        varek = battle.enemies[0]
        varek.hp = varek.max_hp // 2
        battle.defend()
        self.assertEqual([(enemy.template_id, enemy.level) for enemy in battle.enemies],
                         [("varek_domador", 6), ("lobo_faminto", 5)])
        battle.defend()
        self.assertEqual(len(battle.enemies), 2, "o assobio só funciona uma vez")

    def test_items_in_combat(self):
        session = make_session()
        battle = fight(session, ("lobo_faminto", 2))
        self.assertFalse(battle.use_item("pao_de_viagem"))
        self.assertIn("no meio da luta", battle.log[-1])
        session.player.hp = 10
        self.assertTrue(battle.use_item("pocao_cura_menor"))
        self.assertEqual(session.player.inventory.count("pocao_cura_menor"), 1)
        healed = int(re.search(r"\+(\d+) de vida", text(battle)).group(1))
        self.assertTrue(60 <= healed <= 80)

    def test_ambush_and_flight(self):
        session = make_session()
        hp = session.player.hp
        battle = fight(session, ("lobo_faminto", 1), enemies_first=True)
        self.assertLess(session.player.hp, hp)
        self.assertEqual(battle.round, 2)
        self.assertTrue(battle.flee())
        self.assertEqual(battle.outcome, combat.OUTCOME_FLED)


class AfterBattleTest(QuietTestCase):
    def test_victory_grants_xp_loot_and_bestiary(self):
        session = make_session()
        battle = fight(session, ("rato_gigante", 1))
        win(battle)
        report = session.finish_battle(battle, BattleRequest([("rato_gigante", 1)], "caca"))
        self.assertEqual((report.outcome, report.xp), ("vitoria", 100))
        self.assertEqual(session.player.xp, 100)
        for item_id, quantity in report.items:
            self.assertGreaterEqual(session.player.inventory.count(item_id), quantity)
        self.assertEqual(session.state.bestiary["rato_gigante"]["kills"], 1)
        self.assertEqual(session.state.stats["vitorias"], 1)
        self.assertEqual(session.player.resource, 0, "a Raiva se dissipa depois da luta")
        self.assertEqual(session.encounter_grace, ENCOUNTER_GRACE)
        self.assertIsNone(session.pending_battle)

    def test_fixed_encounter_victory_sets_flag_and_journal(self):
        session = make_session()
        landmark = world.get_map("toca_dos_lobos").landmarks["acampamento_domador"]
        encounter = landmark.encounter
        battle = fight(session, *[tuple(entry) for entry in encounter["monsters"]])
        self.assertEqual(win(battle), combat.OUTCOME_VICTORY)
        request = BattleRequest(encounter["monsters"], "fixo", landmark_id=landmark.id, encounter=encounter)
        report = session.finish_battle(battle, request)
        self.assertTrue(session.state.has_flag("varek_derrotado"))
        self.assertIn("diario_domador", {entry.id for entry in session.state.journal})
        self.assertEqual(session.player.inventory.count("coleira_lua_cortada"), 1)
        self.assertEqual(report.xp, sum(monsters.kill_xp(1, enemy.level) for enemy in battle.defeated))
        self.assertTrue(report.text)

    def test_defeat_wakes_the_hero_at_the_chapel(self):
        session = make_session()
        player = session.player
        player.copper, player.hp = 250, 1
        battle = fight(session, ("lobo_cinzento", 5))
        battle.defend()
        self.assertEqual(battle.outcome, combat.OUTCOME_DEFEAT)
        minutes = session.clock.minutes
        report = session.finish_battle(battle, BattleRequest([("lobo_cinzento", 5)], "aleatorio"))
        self.assertEqual((report.copper_lost, player.copper), (25, 225))
        self.assertEqual((session.state.map_id, *session.state.pos), RESPAWN)
        self.assertEqual(player.hp, player.max_hp // 2)
        self.assertEqual(session.clock.minutes - minutes, 240)
        self.assertEqual(session.state.stats["derrotas"], 1)


class EncounterTest(QuietTestCase):
    def test_hunting_in_the_forest(self):
        session = make_session()
        place(session, *FOREST)
        minutes = session.clock.minutes
        self.assertTrue(session.hunt())
        request = session.pending_battle
        self.assertEqual(request.kind, "caca")
        groups = session.map.region_at(*FOREST).encounters["groups"]
        self.assertLessEqual({template_id for template_id, _level in request.monsters},
                             {template_id for group in groups for template_id in group["monsters"]})
        self.assertEqual(session.clock.minutes - minutes, 20)
        self.assertEqual(session.danger(), (2, 4))      # de dia: lobos, javalis e aranhas

    def test_nothing_to_hunt_in_the_village(self):
        session = make_session()
        self.assertFalse(session.hunt())
        self.assertIsNone(session.pending_battle)
        self.assertIsNone(session.danger())

    def test_groups_depend_on_time_and_flags(self):
        session = make_session()
        forest = session.map.region_at(*FOREST).encounters
        set_hour(session, 12)
        day = monsters.available_groups(forest, session.state)
        set_hour(session, 23)
        night = monsters.available_groups(forest, session.state)
        self.assertNotIn("espirito_sussurrante", {t for group in day for t in group["monsters"]})
        self.assertIn("espirito_sussurrante", {t for group in night for t in group["monsters"]})
        den = world.get_map("toca_dos_lobos").regions[0].encounters
        self.assertIn(["lobo_gelido"], [g["monsters"] for g in monsters.available_groups(den, session.state)])
        session.state.flags["presa_de_gelo_derrotado"] = True
        self.assertNotIn(["lobo_gelido"], [g["monsters"] for g in monsters.available_groups(den, session.state)])

    def test_random_encounters_and_grace_period(self):
        session = make_session(rng=FixedRandom(0.0))
        place(session, *FOREST)
        session.walk("s")
        self.assertIsNotNone(session.pending_battle)
        self.assertEqual(session.pending_battle.kind, "aleatorio")
        session.pending_battle = None
        session.encounter_grace = 2
        session.walk("n")
        session.walk("s")
        self.assertIsNone(session.pending_battle)
        session.walk("n")
        self.assertIsNotNone(session.pending_battle)

    def test_resting_in_the_wild(self):
        session = make_session(rng=FixedRandom(0.0))
        place(session, *FOREST)
        session.rest()
        self.assertTrue(session.pending_battle.ambush)
        calm = make_session(rng=FixedRandom(0.99))
        place(calm, *FOREST)
        calm.player.hp = 1
        calm.rest()
        self.assertIsNone(calm.pending_battle)
        self.assertEqual(calm.player.hp, calm.player.max_hp)

    def test_fixed_encounter_and_retreat(self):
        session = make_session(rng=FixedRandom(0.99))
        place(session, 4, 13, "toca_dos_lobos")
        session.walk("n", 10)
        self.assertEqual(session.state.pos, (4, 6))
        request = session.pending_battle
        self.assertEqual((request.kind, request.landmark_id), ("fixo", "galeria_ossos"))
        session.pending_battle = None
        session.retreat(request)
        self.assertEqual(session.state.pos, (4, 7))
        session.walk("n")
        self.assertIsNone(session.pending_battle, "recuou: o encontro espera o herói se afastar")
        session.walk("s")
        session.walk("n")
        self.assertEqual(session.pending_battle.landmark_id, "galeria_ossos")

    def test_den_requires_level_four(self):
        session = make_session()
        place(session, 3, 15)
        session.use_verb("entrar")
        self.assertEqual(session.state.map_id, "vale_primordia")
        self.assertTrue(any("nível 4" in message for message in session.pop_messages()))
        self.assertIn("(nível 4+)", " ".join(session.describe().passages))
        session.player.level = 4
        session.use_verb("entrar")
        self.assertEqual((session.state.map_id, session.state.pos), ("toca_dos_lobos", (4, 13)))


class BattleScreenTest(QuietTestCase):
    def play(self, session, *answers):
        stream = itertools.chain(answers, itertools.repeat("a"))
        ui.input_func = lambda _prompt: next(stream)
        battle_ui.run(session)

    def test_hunt_and_win_through_the_interface(self):
        session = make_session(rng=FixedRandom(0.5))
        place(session, *FOREST)
        commands.dispatch(session, "cacar")
        self.play(session, "1")
        self.assertIsNone(session.pending_battle)
        self.assertGreater(session.player.xp, 0)
        self.assertIn("VITÓRIA", self.output.getvalue())

    def test_leave_the_prey_alone(self):
        session = make_session()
        place(session, *FOREST)
        session.hunt()
        xp = session.player.xp
        self.play(session, "2")
        self.assertIsNone(session.pending_battle)
        self.assertEqual(session.player.xp, xp)
        self.assertNotIn("VITÓRIA", self.output.getvalue())

    def test_every_combat_command_works(self):
        session = make_session(class_id="sacerdote", rng=FixedRandom(0.5))
        place(session, *FOREST)
        session.hunt()
        self.play(session, "1", "?", "", "x", "i", "0", "d", "1", "2", "cura", "zzz", "9")
        self.assertIsNone(session.pending_battle)
        self.assertIn("VITÓRIA", self.output.getvalue())


class EquipmentTest(unittest.TestCase):
    def test_class_proficiencies(self):
        mage = make_session(class_id="mago").player
        self.assertIn("malha", mage.equip_problem("cota_malha_recruta"))
        self.assertIn("escudos", mage.equip_problem("escudo_madeira_reforcada"))
        priest = make_session(class_id="sacerdote").player
        self.assertIn("duas armas", priest.equip_problem("adaga_curva"))
        self.assertIn("espada", priest.equip_problem("espada_curta_gasta"))
        self.assertIn("não é um equipamento", priest.equip_problem("pao_de_viagem"))
        self.assertIsNone(make_session().player.equip_problem("cota_malha_recruta"))

    def test_two_handed_weapon_frees_the_offhand(self):
        player = make_session().player
        player.inventory.add("cajado_aprendiz")
        removed = player.equip(player.inventory.find("cajado_aprendiz"))
        self.assertEqual({stack.item_id for stack in removed}, {"espada_curta_gasta", "escudo_madeira_reforcada"})
        self.assertEqual(player.equipment["arma"].item_id, "cajado_aprendiz")
        self.assertNotIn("secundaria", player.equipment)
        self.assertEqual(player.inventory.count("escudo_madeira_reforcada"), 1)
        self.assertIn("duas mãos", player.equip_problem("escudo_madeira_reforcada"))

    def test_swaps_need_room_in_the_bag(self):
        player = make_session().player
        player.inventory.add("cajado_aprendiz")
        while player.inventory.free_slots:
            player.inventory.add("adaga_curva")
        with self.assertRaises(ValueError):
            player.equip(player.inventory.find("cajado_aprendiz"))
        self.assertEqual(player.equipment["arma"].item_id, "espada_curta_gasta")
        with self.assertRaises(ValueError):
            player.unequip("pes")
        player.inventory.take(player.inventory.find("adaga_curva"))
        self.assertEqual(player.unequip("pes").item_id, "botas_gastas")
        with self.assertRaises(ValueError):
            player.unequip("pes")

    def test_gear_changes_combat_stats(self):
        player = make_session().player
        armor = Hero(player).armor
        player.unequip("peito")
        self.assertLess(Hero(player).armor, armor)


class ConsumableTest(QuietTestCase):
    def test_bread_heals_out_of_combat(self):
        session = make_session()
        player = session.player
        player.hp = 1
        count, minutes = player.inventory.count("pao_de_viagem"), session.clock.minutes
        self.assertTrue(session.use_item(player.inventory.find("pao_de_viagem")))
        self.assertEqual(player.inventory.count("pao_de_viagem"), count - 1)
        self.assertEqual(session.clock.minutes - minutes, 10)
        self.assertGreaterEqual(player.hp, 1 + round(player.max_hp * 0.35))

    def test_water_restores_mana(self):
        session = make_session(class_id="mago")
        player = session.player
        player.resource = 0
        session.use_item(player.inventory.find("cantil_agua"))
        self.assertGreaterEqual(player.resource, round(player.max_resource * 0.35))

    def test_use_command(self):
        session = make_session()
        session.player.hp = 1
        commands.dispatch(session, "comer pao")
        self.assertGreater(session.player.hp, 1)
        commands.dispatch(session, "usar cartaz")
        self.assertIn("Você não tem nada chamado 'cartaz' para usar.", self.output.getvalue())


    def test_drop_command(self):
        session = make_session()
        inventory = session.player.inventory
        commands.dispatch(session, "largar pao 0")
        commands.dispatch(session, "largar pao 1")
        self.assertEqual(inventory.count("pao_de_viagem"), 3)
        commands.dispatch(session, "largar pao tudo")
        self.assertEqual(inventory.count("pao_de_viagem"), 0)
        commands.dispatch(session, "largar cartaz")
        self.assertEqual(inventory.count("cartaz_convocacao"), 1)


class ShopTest(QuietTestCase):
    def test_buy_and_sell(self):
        player = make_session().player
        player.copper = 250
        self.assertEqual(shop.buy(player, "graca", "pocao_cura_menor", 2), 200)
        self.assertEqual((player.copper, player.inventory.count("pocao_cura_menor")), (50, 4))
        with self.assertRaises(ValueError):
            shop.buy(player, "graca", "pocao_cura")             # 240 de cobre
        with self.assertRaises(ValueError):
            shop.buy(player, "graca", "presa_gelida")           # não está à venda
        self.assertEqual(shop.sell(player, player.inventory.find("pocao_cura_menor"), 3), 75)
        self.assertEqual((player.copper, player.inventory.count("pocao_cura_menor")), (125, 1))
        with self.assertRaises(ValueError):
            shop.sell(player, player.inventory.find("cartaz_convocacao"), 1)

    def test_full_bag_refunds_the_purchase(self):
        player = make_session().player
        player.copper = 1000
        while player.inventory.free_slots:
            player.inventory.add("adaga_curva")
        with self.assertRaises(ValueError):
            shop.buy(player, "graca", "pocao_cura", 1)
        self.assertEqual((player.copper, player.inventory.count("pocao_cura")), (1000, 0))

    def test_sell_junk(self):
        player = make_session().player
        player.inventory.add("pena_corvo", 3)
        player.inventory.add("presa_lobo")
        copper = player.copper
        units, earned = shop.sell_junk(player)
        self.assertEqual(units, 4)
        self.assertEqual(earned, 3 * ITEMS["pena_corvo"]["value"] + ITEMS["presa_lobo"]["value"])
        self.assertEqual(player.copper, copper + earned)
        self.assertEqual(shop.junk(player), [])

    def test_merchant_opens_the_shop(self):
        session = make_session()
        self.assertEqual(npcs.get_npc("graca").shop, "graca")
        npcs.apply_effects({"open_shop": True}, session)
        self.assertTrue(session.pending_shop)

    def test_shop_screen(self):
        session = make_session()
        session.player.copper = 500
        session.player.inventory.add("pena_corvo", 2)
        self.type_in("1", "4", "2", "3", "0")   # compra 2 poções de cura menor, vende a sucata, sai
        shop.run(session, "graca")
        self.assertEqual(session.player.inventory.count("pocao_cura_menor"), 4)
        self.assertEqual(session.player.inventory.count("pena_corvo"), 0)


class BestiaryTest(TempSaveDirMixin):
    def test_bestiary_survives_saving(self):
        session = make_session()
        session.state.learn({"lobo_cinzento": {"fraco:fogo", "analisado"}})
        session.state.record_kill("lobo_cinzento", ["pele_lobo"])
        loaded = save_system.load_game(session.save())
        self.assertEqual(loaded.bestiary, session.state.bestiary)
        self.assertEqual(loaded.knowledge()["lobo_cinzento"], {"fraco:fogo", "analisado"})
        self.assertEqual(loaded.bestiary["lobo_cinzento"]["kills"], 1)

    def test_unknown_creatures_are_dropped_from_old_saves(self):
        session = make_session()
        session.state.record_kill("lobo_cinzento", [])
        data = session.state.to_dict()
        data["bestiary"]["dragao_extinto"] = {"kills": 3, "facts": [], "loot": []}
        loaded = type(session.state).from_dict(data)
        self.assertEqual(set(loaded.bestiary), {"lobo_cinzento"})


if __name__ == "__main__":
    unittest.main()
