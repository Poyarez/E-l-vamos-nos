"""Missões, quadro de avisos e o conteúdo da Etapa 4.

* Integridade: toda flag, pista, local, item ou missão citado numa condição existe e pode
  ser obtido — um erro de digitação aqui deixaria uma missão impossível de concluir.
* Regras: começo, etapas, abates, entregas, recompensas (inclusive por classe) e a espera
  por espaço na mochila; o quadro de avisos do dia; o save.
* Conteúdo: baús (chave, gazua e canção), segredos condicionais, o barco e, de ponta a
  ponta, a história principal e as missões secundárias.
"""

import unittest

from rpg import battle_ui, commands, crafting, npcs, quests, screens, shop, ui, world
from rpg.combat import OUTCOME_VICTORY
from rpg.conditions import CONDITION_KEYS, as_list, item_pairs
from rpg.data.classes import CLASSES
from rpg.data.gathering import NODES
from rpg.data.items import ITEMS
from rpg.data.monsters import MONSTERS
from rpg.data.npcs import NPCS
from rpg.data.quests import BOUNTIES, QUESTS
from rpg.data.shops import SHOPS
from rpg.npcs import EFFECT_KEYS
from rpg.save_system import load_game, save_game
from tests.helpers import QuietTestCase, TempSaveDirMixin, make_session, place, set_hour
from tests.test_combat import fight, win


# --------------------------------------------------------------------------- coleta de dados

def all_landmarks():
    for map_id in world.map_ids():
        yield from world.get_map(map_id).landmarks.values()


def dialogue_effects():
    for npc in npcs.all_npcs():
        for node in npc.dialogue.values():
            yield node.get("effects", {})
            for option in node.get("options", []):
                yield option.get("effects", {})


def condition_blocks():
    """Todos os blocos de condições do jogo, com uma etiqueta de onde estão."""
    for npc in npcs.all_npcs():
        for rule in npc.schedule:
            yield f"agenda de {npc.id}", rule.get("if")
        for node_id, node in npc.dialogue.items():
            for entry in node.get("text", []):
                if isinstance(entry, dict):
                    yield f"{npc.id}:{node_id}", entry["if"]
            for option in node.get("options", []):
                yield f"{npc.id}:{node_id}", option.get("if")
    for map_id in world.map_ids():
        game_map = world.get_map(map_id)
        for region in game_map.regions:
            for group in (region.encounters or {}).get("groups", []):
                yield f"encontros de {region.id}", group.get("if")
        for landmark in game_map.landmarks.values():
            for entry in list(landmark.resources) + list(landmark.stations):
                yield landmark.id, entry.get("if")
            for found in (landmark.secret, landmark.chest, landmark.encounter):
                if found:
                    yield landmark.id, found.get("if")
        for portal in game_map.portals:
            flags = [flag for flag in (portal.unlock_flag, portal.requires_flag) if flag]
            yield portal.id, {"flag": flags} if flags else None
    for quest_id, quest in QUESTS.items():
        yield f"início de {quest_id}", quest.get("start")
        for stage in quest["stages"]:
            yield f"etapa de {quest_id}", {key: value for key, value in stage["goal"].items() if key != "kill"}
    for bounty_id, bounty in BOUNTIES.items():
        yield bounty_id, bounty.get("if")
    for shop_id, data in SHOPS.items():
        for entry in data["stock"]:
            if isinstance(entry, dict):
                yield f"loja {shop_id}", entry["if"]
    for node_id, node in NODES.items():
        yield node_id, node.get("if")


def flatten(block):
    """Desdobra os blocos de ``any`` (as condições alternativas também precisam existir)."""
    if not block:
        return
    yield block
    for inner in block.get("any", []):
        yield from flatten(inner)


def settable_flags():
    flags = set()
    for effects in dialogue_effects():
        flags |= set(as_list(effects.get("set_flag", [])))
    for landmark in all_landmarks():
        for found in (landmark.secret, landmark.chest, landmark.loot, landmark.encounter):
            if found:
                flags.add(found["flag"])
    for quest in QUESTS.values():
        flags |= set(as_list(quest.get("rewards", {}).get("set_flag", [])))
    return flags


def journal_ids():
    ids = {"convocacao"}                          # anotado por main.py no começo do jogo
    for effects in dialogue_effects():
        ids |= {entry["id"] for entry in as_list(effects.get("journal", []))}
    for landmark in all_landmarks():
        if landmark.secret and landmark.secret.get("journal"):
            ids.add(landmark.secret["flag"])      # o segredo é anotado com o id da própria flag
        if landmark.encounter and landmark.encounter.get("journal"):
            ids.add(landmark.encounter["journal"]["id"])
    for quest in QUESTS.values():
        journal = quest.get("rewards", {}).get("journal")
        if journal:
            ids.add(journal["id"])
    return ids


class QuestDataTest(unittest.TestCase):
    def test_every_condition_points_to_something_that_exists(self):
        flags, journal = settable_flags(), journal_ids()
        landmarks = {landmark.id for landmark in all_landmarks()}
        for where, block in condition_blocks():
            for part in flatten(block):
                with self.subTest(where=where, block=part):
                    self.assertLessEqual(set(part), CONDITION_KEYS)
                    for flag in as_list(part.get("flag", [])) + as_list(part.get("not_flag", [])):
                        self.assertIn(flag, flags, f"{where}: a flag {flag!r} nunca é ativada")
                    for entry_id in as_list(part.get("journal", [])):
                        self.assertIn(entry_id, journal, f"{where}: a pista {entry_id!r} nunca é anotada")
                    for landmark_id in as_list(part.get("discovered", [])):
                        self.assertIn(landmark_id, landmarks)
                    for item_id, _quantity in item_pairs(part.get("item")):
                        self.assertIn(item_id, ITEMS)
                    for item_id in as_list(part.get("owns", [])):
                        self.assertIn(item_id, ITEMS)
                    for quest_id in as_list(part.get("quest_active", [])) + as_list(part.get("quest_done", [])):
                        self.assertIn(quest_id, QUESTS)
                    if "quest_stage" in part:
                        quest_id, stage = part["quest_stage"]
                        self.assertLess(stage, len(QUESTS[quest_id]["stages"]))

    def test_quests(self):
        started = {effects["start_quest"] for effects in dialogue_effects() if "start_quest" in effects}
        for quest_id, quest in QUESTS.items():
            with self.subTest(quest=quest_id):
                self.assertTrue(quest["name"] and quest["giver"] and quest["summary"])
                self.assertIn(quest["category"], quests.CATEGORIES)
                self.assertTrue(quest.get("start") or quest_id in started, "missão que nunca começa")
                self.assertTrue(quest["stages"])
                for stage in quest["stages"]:
                    self.assertTrue(stage["text"])
                    self.assertTrue(stage["goal"])
                    hunt = stage["goal"].get("kill")
                    if hunt:
                        self.assertLessEqual(set(hunt["monsters"]), set(MONSTERS))
                        self.assertGreater(hunt["count"], 0)
                    for item_id, quantity in item_pairs(stage.get("take_item")):
                        self.assertIn(item_id, ITEMS)
                rewards = quest["rewards"]
                self.assertGreater(rewards.get("xp", 0), 0)
                for item_id, _quantity in item_pairs(rewards.get("items")):
                    self.assertIn(item_id, ITEMS)
                for class_id, pairs in rewards.get("class_items", {}).items():
                    self.assertIn(class_id, CLASSES)
                    for item_id, _quantity in item_pairs(pairs):
                        self.assertIn(item_id, ITEMS)
                        self.assertIsNone(make_session(class_id=class_id).player.equip_problem(item_id))
        self.assertEqual(sum(quest["category"] == "principal" for quest in QUESTS.values()), 1)
        self.assertLessEqual(started, set(QUESTS))

    def test_bounties(self):
        for bounty_id, bounty in BOUNTIES.items():
            with self.subTest(bounty=bounty_id):
                self.assertTrue(bounty["name"] and bounty["description"])
                goal = bounty["goal"]
                self.assertTrue(goal.get("kill") or goal.get("deliver"))
                if goal.get("kill"):
                    self.assertLessEqual(set(goal["kill"]["monsters"]), set(MONSTERS))
                for item_id, quantity in item_pairs(goal.get("deliver")):
                    self.assertIn(item_id, ITEMS)
                    self.assertNotEqual(ITEMS[item_id]["type"], "missao")
                self.assertTrue(bounty["reward"].get("xp") and bounty["reward"].get("copper"))
                self.assertLessEqual(bounty.get("min_level", 1), bounty.get("max_level", 60))
        # há tarefas para todas as fases do jogo
        for level in (1, 5, 10, 13):
            pool = [b for b in BOUNTIES.values() if b.get("min_level", 1) <= level <= b.get("max_level", 60)]
            self.assertGreaterEqual(len(pool), quests.BOARD_SIZE, level)

    def test_dialogue_effects_are_known(self):
        for effects in dialogue_effects():
            self.assertLessEqual(set(effects), EFFECT_KEYS)
            if "start_quest" in effects:
                self.assertIn(effects["start_quest"], QUESTS)
            for item_id, _quantity in item_pairs(effects.get("give_item")) + item_pairs(effects.get("take_item")):
                self.assertIn(item_id, ITEMS)

    def test_new_npcs_exist(self):
        for npc_id in ("kael", "davi", "pip", "tome", "vigia"):
            self.assertIn(npc_id, NPCS)


# --------------------------------------------------------------------------- regras

class QuestRulesTest(QuietTestCase):
    def test_start_stages_kills_and_rewards(self):
        session = make_session()
        state, player = session.state, session.player
        npcs.apply_effects(npcs.get_npc("tobias").dialogue["ratos"]["effects"], session)
        self.assertTrue(quests.is_active(state, "ratos"))
        self.assertFalse(quests.start(state, "ratos"), "uma missão não começa duas vezes")
        self.assertIn("Rato Gigante: 0/6", quests.progress_text(state, "ratos"))
        for _ in range(6):
            quests.record_kill(state, "rato_gigante")
        quests.record_kill(state, "lobo_cinzento")          # não conta
        session.update_quests()
        self.assertEqual(state.quests["ratos"]["stage"], 1)
        copper, xp = player.copper, player.xp
        state.flags["tobias_ratos"] = True
        session.update_quests()
        self.assertTrue(quests.is_done(state, "ratos"))
        self.assertEqual(player.copper - copper, 150)
        self.assertGreater(player.xp + 1000 * (player.level - 1), xp)
        self.assertEqual(player.inventory.count("pao_de_viagem"), 4 + 5)
        self.assertIn("Missão concluída", "\n".join(session.pop_messages()))

    def test_automatic_start_and_class_rewards(self):
        session = make_session(class_id="mago")
        state = session.state
        state.add_journal("pista_davi", "O aprendiz", "Davi sumiu.")
        session.update_quests()
        self.assertTrue(quests.is_active(state, "aprendiz"))
        state.discovered.add("boca_mina")
        state.flags.update(davi_resgatado=True, brom_davi_voltou=True)
        session.update_quests()
        self.assertTrue(quests.is_done(state, "aprendiz"))
        self.assertEqual(session.player.inventory.count("cajado_aco"), 1)
        self.assertEqual(session.player.inventory.count("escudo_davi"), 0)
        self.assertTrue(state.has_flag("mina_livre"))
        self.assertIn("cota_aco", shop.stock("brom", state))
        self.assertNotIn("cota_aco", shop.stock("brom"))

    def test_handing_in_during_the_same_conversation(self):
        """Entregar na mesma conversa em que a missão começou não pode travar a etapa."""
        session = make_session()
        session.player.inventory.add("pocao_cura_menor", 3)
        celeste = npcs.get_npc("celeste")
        npcs.apply_effects(celeste.dialogue["ajuda"]["effects"], session)
        npcs.apply_effects(celeste.dialogue["pocoes"]["effects"], session)
        session.update_quests()
        self.assertTrue(quests.is_done(session.state, "remedios"))
        self.assertEqual(session.player.inventory.count("simbolo_aurora"), 1)

    def test_rewards_wait_for_room_in_the_bag(self):
        session = make_session()
        state, player = session.state, session.player
        quests.start(state, "peles")
        filler = ["pele_lobo", "carne_lobo", "presa_lobo", "teia_pegajosa", "ectoplasma", "asa_morcego",
                  "pena_corvo", "rabo_rato", "escama_lagarto", "couro_javali", "carne_javali", "presa_javali"]
        for item_id in filler:
            player.inventory.add(item_id, 1)
        while player.inventory.free_slots:
            player.inventory.add("comida_queimada", 20)
        state.flags["graca_peles"] = True
        session.update_quests()
        self.assertFalse(quests.is_done(state, "peles"))
        self.assertIn("mochila está cheia", "\n".join(session.pop_messages()))
        session.update_quests()
        self.assertEqual(session.pop_messages(), [], "o aviso aparece uma vez só")
        last = player.inventory.stacks[-1]
        player.inventory.take(last, last.quantity)          # abre um espaço
        session.update_quests()
        self.assertTrue(quests.is_done(state, "peles"))
        self.assertEqual(player.inventory.count("bolsa_la"), 1)

    def test_rescuing_davi_first_still_starts_the_apprentice_quest(self):
        session = make_session()
        state = session.state
        state.discovered.add("boca_mina")
        state.flags["davi_resgatado"] = True
        session.update_quests()
        self.assertEqual(state.quests["aprendiz"]["stage"], 2)
        talk(session, "brom", "davi_voltou")
        self.assertTrue(state.has_flag("mina_livre"))

    def test_brom_can_use_his_own_silver(self):
        session = make_session()
        player = session.player
        player.inventory.add("metades_lua_minguante")
        player.copper = 400
        brom = npcs.get_npc("brom")
        options = [o["next"] for o in npcs.node_options(brom.dialogue["metades"], session.state, True)]
        self.assertIn("juntar_lua_pago", options)
        self.assertNotIn("juntar_lua", options)            # sem barra de prata
        talk(session, "brom", "juntar_lua_pago")
        self.assertEqual(player.inventory.count("lua_minguante"), 1)
        self.assertEqual(player.inventory.count("metades_lua_minguante"), 0)
        self.assertEqual(player.copper, 100)

    def test_quest_items_never_fill_the_bag(self):
        session = make_session()
        player = session.player
        while player.inventory.free_slots:
            player.inventory.add("comida_queimada", 20)
        self.assertEqual(player.inventory.add("lua_cheia"), 0)
        self.assertEqual(player.inventory.count("lua_cheia"), 1)
        self.assertEqual(player.inventory.free_slots, 0)

    def test_quests_survive_saving(self):
        session = make_session()
        quests.start(session.state, "ratos")
        quests.record_kill(session.state, "rato_gigante")
        loaded = type(session.state).from_dict(session.state.to_dict())
        self.assertEqual(loaded.quests["ratos"]["kills"], 1)
        self.assertTrue(quests.is_active(loaded, "ratos"))

    def test_quest_log_screen(self):
        session = make_session()
        quests.start(session.state, "tres_luas")
        quests.start(session.state, "barco")
        session.player.inventory.add("pregos_bronze", 4)
        self.type_in("")
        commands.dispatch(session, "missoes")
        text = self.output.getvalue()
        self.assertIn("As Três Luas", text)
        self.assertIn("Pregos de Bronze: 4/10", text)


class BountyBoardTest(QuietTestCase, TempSaveDirMixin):
    def test_daily_offers_accept_and_turn_in(self):
        session = make_session()
        state, player = session.state, session.player
        offers = quests.offers(state)
        self.assertEqual(len(offers), quests.BOARD_SIZE)
        self.assertEqual(quests.offers(state), offers, "as ofertas não mudam no mesmo dia")
        for bounty_id in offers:
            bounty = BOUNTIES[bounty_id]
            self.assertLessEqual(bounty.get("min_level", 1), player.level)
        bounty_id = next(b for b in offers if BOUNTIES[b]["goal"].get("deliver"))
        self.assertIsNone(quests.accept_bounty(state, bounty_id))
        self.assertIsNotNone(quests.accept_bounty(state, bounty_id))
        self.assertEqual(quests.bounty_status(state, bounty_id), "aceita")
        for item_id, quantity in item_pairs(BOUNTIES[bounty_id]["goal"]["deliver"]):
            player.inventory.add(item_id, quantity)
        self.assertEqual(quests.bounty_status(state, bounty_id), "pronta")
        copper = player.copper
        self.assertTrue(quests.turn_in_bounty(session, bounty_id))
        self.assertEqual(player.copper - copper, BOUNTIES[bounty_id]["reward"]["copper"])
        self.assertEqual(quests.bounty_status(state, bounty_id), "feita")
        self.assertIsNotNone(quests.accept_bounty(state, bounty_id), "uma vez por dia")
        session.advance_time(24 * 60)
        self.assertNotIn(bounty_id, quests.active_bounties(state))
        self.assertNotEqual(quests.offers(state), offers, "um novo dia, um novo quadro")

    def test_hunts_limits_abandon_and_save(self):
        session = make_session()
        state = session.state
        for day in range(30):
            hunts = [b for b in quests.offers(state) if BOUNTIES[b]["goal"].get("kill")]
            if hunts:
                break
            session.advance_time(24 * 60)
        bounty_id = hunts[0]
        quests.accept_bounty(state, bounty_id)
        hunt = BOUNTIES[bounty_id]["goal"]["kill"]
        for _ in range(hunt["count"]):
            quests.record_kill(state, hunt["monsters"][0])
        self.assertTrue(quests.bounty_ready(state, bounty_id))
        path = save_game(state)
        loaded = load_game(path)
        self.assertTrue(quests.bounty_ready(loaded, bounty_id))
        self.assertTrue(quests.abandon_bounty(state, bounty_id))
        self.assertEqual(quests.bounty_status(state, bounty_id), "livre")

    def test_board_command_at_the_square(self):
        session = make_session()
        state = session.state
        self.type_in("1", "0")
        commands.dispatch(session, "avisos")
        self.assertIn("Praça do Poço", self.output.getvalue())       # longe do quadro
        place(session, 30, 15)
        self.assertIn("avisos", session.describe().board)
        self.type_in("1", "0")
        commands.dispatch(session, "avisos")
        self.assertEqual(len(quests.active_bounties(state)), 1)
        self.assertIn("Tarefa aceita", self.output.getvalue())


# --------------------------------------------------------------------------- conteúdo

def talk(session, npc_id, *nodes):
    npc = npcs.get_npc(npc_id)
    for node_id in nodes:
        npcs.apply_effects(npc.dialogue[node_id].get("effects"), session)
    session.update_quests()


def fixed_fight(session, map_id, landmark_id):
    landmark = world.get_map(map_id).landmarks[landmark_id]
    place(session, landmark.x, landmark.y, map_id)
    session._check_encounters()
    request = session.pending_battle
    assert request is not None and request.landmark_id == landmark_id, (request, landmark_id)
    battle = fight(session, *[tuple(entry) for entry in request.monsters])
    assert win(battle) == OUTCOME_VICTORY
    report = session.finish_battle(battle, request)
    session.update_quests()
    return report


def strong_session(class_id="guerreiro", level=13):
    session = make_session(class_id=class_id)
    while session.player.level < level:
        session.gain_xp(session.player.xp_needed)
    session.player.inventory.capacity = 60
    session.pop_messages()
    session.level_ups.clear()
    return session


class ContentTest(QuietTestCase):
    def test_chest_needs_key_pick_or_song(self):
        session = strong_session("ladino", 11)
        state, player = session.state, session.player
        place(session, 31, 2, "mina_ferro_velho")
        texts = session.examine()
        self.assertIn("falta Chave do Capataz", texts[-1])
        player.inventory.add("chave_capataz")
        session.examine()
        self.assertTrue(state.has_flag("cofre_capataz_aberto"))
        self.assertEqual(player.inventory.count("chave_capataz"), 0)
        self.assertEqual(player.inventory.count("carta_capataz"), 1)
        session.update_quests()
        self.assertTrue(quests.is_active(state, "corvo"), "a carta começa a missão do Corvo")
        place(session, 40, 11, "rota_mercadores")      # ladino de nível 11 arromba o baú do Corvo
        session.examine()
        self.assertTrue(state.has_flag("bau_corvo_aberto"))
        self.assertEqual(player.inventory.count("fardo_zahir"), 1)
        place(session, 12, 2, "ilhota_garca")          # a arca só abre com a canção
        self.assertIn("ainda não conhece", session.examine()[-1])
        state.flags["cancao_tres_notas"] = True
        session.examine()
        self.assertTrue(state.has_flag("arca_vigia_aberta"))

    def test_rune_circle_opens_on_full_moon_or_with_the_key(self):
        session = strong_session()
        state = session.state
        set_hour(session, 22)
        while state.clock.moon_phase == "Lua cheia":
            session.advance_time(24 * 60)
        place(session, 50, 4, "vale_primordia")
        self.assertIn("lua cheia", " ".join(session.examine()))
        self.assertFalse(state.has_flag("passagem_circulo"))
        self.assertFalse(session.use_verb("entrar"))
        while state.clock.moon_phase != "Lua cheia":
            session.advance_time(24 * 60)
        session.examine()
        self.assertTrue(state.has_flag("passagem_circulo"))
        self.assertTrue(session.use_verb("entrar"))
        self.assertEqual(state.map_id, "santuario_profano")

    def test_boat_needs_repairs(self):
        session = strong_session()
        place(session, 41, 22, "vale_primordia")
        self.assertFalse(session.use_verb("navegar"))
        session.state.flags["barco_consertado"] = True
        self.type_in()
        commands.dispatch(session, "navegar")
        self.assertEqual(session.state.map_id, "ilhota_garca")
        commands.dispatch(session, "navegar")
        self.assertEqual(session.state.map_id, "vale_primordia")

    def test_boss_fight_warns_about_a_full_bag(self):
        session = strong_session("guerreiro", 10)
        session.player.inventory.capacity = 16
        while session.player.inventory.free_slots > 1:
            session.player.inventory.add("comida_queimada", 20)
        landmark = world.get_map("mina_ferro_velho").landmarks["fosso_forja"]
        place(session, landmark.x, landmark.y, "mina_ferro_velho")
        session._check_encounters()
        self.type_in("2")                                    # recuar
        battle_ui.run(session)
        self.assertIn("mochila só tem 1 espaço livre", self.output.getvalue())
        self.assertFalse(session.state.has_flag("gorran_derrotado"))

    def test_mine_requires_level_eight(self):
        session = make_session()
        place(session, 53, 12, "vale_primordia")
        session.use_verb("entrar")
        self.assertEqual(session.state.map_id, "vale_primordia")
        self.assertIn("nível 8", "\n".join(session.pop_messages()))

    def test_the_king_of_the_lake_needs_a_master_angler(self):
        session = strong_session()
        player = session.player
        spot = crafting.spots_at(world.get_map("ilhota_garca").landmarks["poco_do_rei"], session.state)[0]
        player.inventory.add("vara_pesca")
        player.inventory.add("isca_minhoca", 20)
        player.skills.add_xp("pesca", 9_000)        # nível 20: pesca carpas, mas não o rei
        rng = session.rng
        rng.random = lambda: 0.0                     # todas as tentativas dão certo (e todos os achados)
        place(session, 21, 5, "ilhota_garca")
        report = session.gather(spot, 5)
        self.assertGreater(report.items.get("carpa_prateada", 0), 0)
        self.assertEqual(player.inventory.count("rei_do_lago"), 0)
        player.skills.add_xp("pesca", 30_000)       # nível 35+
        session.state.nodes.clear()
        session.gather(spot, 1)
        self.assertEqual(player.inventory.count("rei_do_lago"), 1)

    def test_main_story_from_start_to_end(self):
        session = strong_session("guerreiro", 13)
        state, player = session.state, session.player
        state.flags["lenda_primordial"] = True
        talk(session, "ysolde", "primordial")
        self.assertTrue(quests.is_active(state, "tres_luas"))
        place(session, 11, 1, "gruta_veu_prata")
        session.examine()                                         # o baú do véu: a lua crescente
        set_hour(session, 22)
        place(session, 37, 11, "vale_primordia")
        self.assertIn("kael", [npc.id for npc in session.npcs_here()])
        talk(session, "kael", "luas")
        talk(session, "anselmo", "barco")
        for item_id, quantity in (("pregos_bronze", 10), ("piche", 2), ("remendo_lona", 1)):
            player.inventory.add(item_id, quantity)
        session.update_quests()
        talk(session, "anselmo", "barco_pronto")
        self.assertTrue(quests.is_done(state, "barco"))
        place(session, 41, 22, "vale_primordia")
        self.assertTrue(session.use_verb("navegar"))
        set_hour(session, 22)
        place(session, 13, 4, "ilhota_garca")
        session.examine()                                         # as pedras que cantam
        session.update_quests()
        place(session, 10, 7, "ilhota_garca")
        session.use_verb("navegar")
        set_hour(session, 23)
        place(session, 5, 6, "vale_primordia")
        session.examine()                                         # o Carvalho Ancião: a lua cheia
        session.update_quests()
        self.assertEqual(player.inventory.count("lua_cheia"), 1)
        set_hour(session, 22)
        report = fixed_fight(session, "vale_primordia", "arvore_enforcados")
        self.assertIn(("chave_lua_cortada", 1), report.items)
        place(session, 50, 4, "vale_primordia")
        session.examine()
        self.assertTrue(session.use_verb("entrar"))
        report = fixed_fight(session, "santuario_profano", "altar_profano")
        self.assertIn(("metades_lua_minguante", 1), report.items)
        player.inventory.add("barra_prata")
        talk(session, "brom", "metades", "juntar_lua")
        self.assertEqual(player.inventory.count("lua_minguante"), 1)
        place(session, 13, 3, "gruta_veu_prata")
        session.examine()                                         # a porta das três luas
        session.update_quests()
        self.assertTrue(session.use_verb("entrar"))
        self.assertEqual(state.map_id, "camara_vigia")
        report = fixed_fight(session, "camara_vigia", "leito_vigia")
        self.assertIn(("lagrima_vigia", 1), report.items)
        self.assertIn("vigia", [npc.id for npc in npcs.npcs_at(state, "camara_vigia", 13, 4)])
        self.assertEqual(state.quests["tres_luas"]["stage"], 8)
        talk(session, "ysolde", "final")
        self.assertTrue(quests.is_done(state, "tres_luas"))
        self.assertEqual(player.inventory.count("manto_vigias"), 1)
        self.assertTrue(state.has_flag("vale_salvo"))
        messages = "\n".join(session.pop_messages())
        self.assertIn("Missão concluída: As Três Luas!", messages)

    def test_side_stories(self):
        session = strong_session("ladino", 11)
        state, player = session.state, session.player
        talk(session, "brom", "davi")
        place(session, 53, 12, "vale_primordia")
        self.assertTrue(session.use_verb("entrar"))
        session.update_quests()
        report = fixed_fight(session, "mina_ferro_velho", "fosso_forja")
        self.assertIn(("chave_capataz", 1), report.items)
        self.assertIn("davi", [npc.id for npc in session.npcs_here()])
        talk(session, "davi", "resgate")
        set_hour(session, 10)
        self.assertIn("pip", [npc.id for npc in npcs.npcs_at(state, "mina_ferro_velho", 4, 3)])
        self.assertIn("davi", [npc.id for npc in npcs.npcs_at(state, "vale_primordia", 28, 16)])
        talk(session, "brom", "davi_voltou")
        self.assertTrue(quests.is_done(state, "aprendiz"))
        self.assertEqual(player.inventory.count("adaga_davi"), 1)
        # o Bando do Corvo
        place(session, 31, 2, "mina_ferro_velho")
        session.examine()
        session.update_quests()
        place(session, 30, 29, "vale_primordia")
        self.assertFalse(session.step(0, 1), "o Portão Sul continua fechado")
        talk(session, "renna", "carta")
        self.assertTrue(session.step(0, 1))
        self.assertEqual(state.map_id, "rota_mercadores")
        fixed_fight(session, "rota_mercadores", "desfiladeiro")
        fixed_fight(session, "rota_mercadores", "acampamento_corvo")
        talk(session, "renna", "rota_livre")
        self.assertTrue(quests.is_done(state, "corvo"))
        self.assertEqual(player.inventory.count("anel_guarda"), 1)
        set_hour(session, 10)
        self.assertIn("zahir", [npc.id for npc in npcs.npcs_at(state, "vale_primordia", 32, 16)])
        self.assertIn("frasco_luz", shop.stock("zahir", state))
        # o sobrinho da capitã
        talk(session, "renna", "tome_sumiu")
        set_hour(session, 22)
        fixed_fight(session, "vale_primordia", "torre_tombada")
        self.assertIn("tome", [npc.id for npc in session.npcs_here()])
        talk(session, "tome", "salvo", "viu")
        talk(session, "renna", "tome_salvo")
        self.assertTrue(quests.is_done(state, "sobrinho"))
        self.assertEqual(player.inventory.count("capa_guarda"), 1)


class Etapa4ScreensTest(QuietTestCase):
    def test_new_screens_render_at_every_width(self):
        session = strong_session("mago", 12)
        quests.start(session.state, "tres_luas")
        session.player.learn_talent("fogo_intenso")
        place(session, 30, 15)
        quests.accept_bounty(session.state, quests.offers(session.state)[0])
        self.addCleanup(setattr, ui, "term_width", ui.term_width)
        for width in (80, 100, 120):
            ui.term_width = lambda width=width: width
            screens.quest_log_screen(session)
            screens.talents_screen(session)
            screens.abilities_screen(session)
            screens.character_sheet(session)
            screens.render_location(session)
        for line in self.output.getvalue().splitlines():
            self.assertLessEqual(ui.visible_len(line), 120)


if __name__ == "__main__":
    unittest.main()
