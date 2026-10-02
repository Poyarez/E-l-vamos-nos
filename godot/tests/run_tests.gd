extends Node
## Testes da versão Godot, rodados sem janela (saem com código 1 se algo falhar):
##     godot --headless --path godot res://tests/run_tests.tscn
## Conferem os dados exportados, o TileSet e as cenas de mapa, os diálogos de todos os NPCs,
## as condições, as missões, o save e o mundo de verdade: andar, bater em água, passagens
## trancadas e abertas, conversas inteiras pela caixa de diálogo e o combate em tempo real
## (as contas iguais às do terminal, selos, interrupção, derrota, chefes e lutas simuladas).

const MAIN_SCENE := preload("res://scenes/main.tscn")
const Sim := preload("res://tests/sim.gd")

var checks := 0
var failures := 0
var warnings := PackedStringArray()


func _ready() -> void:
	test_data()
	test_tileset_and_maps()
	test_dialogue_graphs()
	test_conditions()
	test_story()
	test_save_roundtrip()
	await test_world()
	await test_conversations()
	test_combat_rules()
	await test_combat()
	for warning in warnings:
		print("aviso: ", warning)
	print("%d verificações, %d falha(s)" % [checks, failures])
	get_tree().quit(1 if failures else 0)


func check(condition: bool, message: String) -> void:
	checks += 1
	if not condition:
		failures += 1
		printerr("FALHOU: ", message)


func frames(count: int = 1) -> void:
	for i in count:
		await get_tree().process_frame


func seconds(duration: float) -> void:
	await get_tree().create_timer(duration).timeout


# --------------------------------------------------------------------------- dados

func test_data() -> void:
	check("vale_primordia" in Data.map_ids, "o vale está entre os mapas")
	check(Data.npcs.size() >= 16, "NPCs carregados")
	check(Data.rules.periods.size() == 6, "seis períodos do dia")
	for map_id: String in Data.map_ids:
		var data := Data.map_data(map_id)
		check(not data.is_empty(), "mapa %s carregado" % map_id)
		for terrain_id: String in data.legend.values():
			check(Data.terrain.has(terrain_id), "%s: terreno %s existe" % [map_id, terrain_id])
			check(Data.art.tiles.has(terrain_id), "%s: terreno %s tem tile" % [map_id, terrain_id])
	for npc_id: String in Data.npcs:
		check(Data.art.npcs.rows.has(npc_id), "NPC %s tem sprite" % npc_id)
		check(Data.map_ids.has(Data.npcs[npc_id].map), "NPC %s mora num mapa que existe" % npc_id)


# --------------------------------------------------------------------------- tiles e mapas

func test_tileset_and_maps() -> void:
	var tileset := MapBuilder.tileset()
	var source: TileSetAtlasSource = tileset.get_source(MapBuilder.SOURCE_ID)
	for terrain_id: String in Data.art.tiles:
		var coords := Vector2i(0, int(Data.art.tiles[terrain_id][0]))
		check(source.has_tile(coords), "tile do terreno %s existe" % terrain_id)
		if source.has_tile(coords):
			check(source.get_tile_data(coords, 0).get_custom_data("terrain") == terrain_id,
					"tile do terreno %s guarda o id certo" % terrain_id)
	for map_id: String in Data.map_ids:
		check(ResourceLoader.exists(MapBuilder.scene_path(map_id)), "cena do mapa %s existe" % map_id)
		var data := Data.map_data(map_id)
		var scene := MapBuilder.instantiate_map(map_id)
		var ground: TileMapLayer = scene.get_node_or_null("Ground")
		check(ground != null, "mapa %s tem a camada Ground" % map_id)
		if ground == null:
			scene.free()
			continue
		var drift := 0
		for y in data.rows.size():
			for x in data.rows[y].length():
				var tile := ground.get_cell_tile_data(Vector2i(x, y))
				if tile == null or tile.get_custom_data("terrain") != data.legend[data.rows[y][x]]:
					drift += 1
		if drift:
			warnings.append("%s: %d tile(s) diferentes do desenho em texto (pintados no editor?)" % [map_id, drift])
		for landmark: Dictionary in data.get("landmarks", []):
			check(_passable(ground, Vector2i(int(landmark.x), int(landmark.y))),
					"%s: dá para pisar no local %s" % [map_id, landmark.id])
		for portal: Dictionary in data.get("portals", []):
			check(_passable(ground, Vector2i(int(portal.x), int(portal.y))),
					"%s: dá para pisar na passagem %s" % [map_id, portal.id])
			if portal.get("target") is Array:
				var target: Array = portal.target
				var other := Data.map_data(str(target[0]))
				check(not other.is_empty(), "%s: a passagem %s leva a um mapa que existe" % [map_id, portal.id])
		scene.free()


func _passable(ground: TileMapLayer, cell: Vector2i) -> bool:
	var tile := ground.get_cell_tile_data(cell)
	return tile != null and bool(Data.terrain.get(str(tile.get_custom_data("terrain")), {}).get("passable", false))


# --------------------------------------------------------------------------- diálogos

func test_dialogue_graphs() -> void:
	for npc_id: String in Data.npcs:
		var dialogue: Dictionary = Data.npcs[npc_id].dialogue
		check(dialogue.has("inicio"), "%s começa no trecho 'inicio'" % npc_id)
		for node_id: String in dialogue:
			var node: Dictionary = dialogue[node_id]
			_check_block(node.get("effects"), Story.EFFECT_KEYS, "%s/%s: efeitos" % [npc_id, node_id])
			for entry: Variant in node.get("text", []):
				if entry is Dictionary:
					_check_conditions(entry.get("if"), "%s/%s: fala" % [npc_id, node_id])
			var targets: Array = [node.get("next")]
			for option: Dictionary in node.get("options", []):
				targets.append(option.get("next"))
				_check_conditions(option.get("if"), "%s/%s: opção" % [npc_id, node_id])
				_check_block(option.get("effects"), Story.EFFECT_KEYS, "%s/%s: efeitos da opção" % [npc_id, node_id])
			for target: Variant in targets:
				check(target == null or dialogue.has(target), "%s/%s: o trecho '%s' existe" % [npc_id, node_id, target])
		for rule: Dictionary in Data.npcs[npc_id].schedule:
			_check_conditions(rule.get("if"), "%s: agenda" % npc_id)


func _check_conditions(block: Variant, where: String) -> void:
	if block is Dictionary:
		_check_block(block, Conditions.KEYS, where)
		for nested: Variant in block.get("any", []):
			_check_conditions(nested, where)


func _check_block(block: Variant, allowed: Array, where: String) -> void:
	if block is Dictionary:
		for key: String in block:
			check(key in allowed, "%s: chave conhecida '%s'" % [where, key])


# --------------------------------------------------------------------------- condições

func test_conditions() -> void:
	Game.new_game({"class_id": "guerreiro", "alignment": "neutro_bom"})
	check(Conditions.met(null) and Conditions.met({}), "bloco vazio vale")
	check(not Conditions.met({"flag": "teste"}), "flag ausente")
	Game.set_flag("teste")
	check(Conditions.met({"flag": "teste"}) and not Conditions.met({"not_flag": "teste"}), "flag presente")
	check(Conditions.met({"any": [{"flag": "nada"}, {"flag": "teste"}]}), "any: basta um")
	check(not Conditions.met({"any": [{"flag": "nada"}, {"flag": "outra"}]}), "any: nenhum")
	Game.give_item("pedra_teste", 3, false)
	check(Conditions.met({"item": ["pedra_teste", 3]}) and not Conditions.met({"item": ["pedra_teste", 4]}), "item")
	check(Conditions.met({"item": "pedra_teste"}), "item sem quantidade")
	check(not Conditions.met({"item": [["pedra_teste", 1], ["outra", 1]]}), "lista de itens")
	check(Conditions.met({"owns": "espada_curta_gasta"}), "equipamento inicial conta como posse")
	check(Conditions.met({"class": ["guerreiro", "ladino"], "moral": "bom"}), "classe e moral")
	check(not Conditions.met({"law": "leal"}), "lei")
	check(Conditions.met({"met": true}, true) and not Conditions.met({"met": true}, false), "met")
	check(Conditions.met({"skill": {"mineracao": 1}}) and not Conditions.met({"skill": {"mineracao": 15}}), "perícia")
	check(Conditions.met({"copper": Game.copper}) and not Conditions.met({"copper": Game.copper + 1}), "cobre")
	check(Conditions.met({"moon": Game.moon_phase()}), "lua")
	check(Conditions.met({"talents": false}), "sem talentos")
	Game.talents["teste"] = 1
	check(Conditions.met({"talents": true}), "com talentos")
	Game.minutes = 21 * 60
	check(Game.period() == "noite" and Conditions.met({"night": true, "period": "noite"}), "noite")
	Game.minutes = 9 * 60
	check(Game.period() == "manha" and Conditions.met({"night": false}), "manhã")
	Game.quests["missao_teste"] = {"stage": 2, "kills": 0, "done": false}
	check(Conditions.met({"quest_active": "missao_teste", "quest_stage": ["missao_teste", 2]}), "etapa da missão")
	check(not Conditions.met({"quest_done": "missao_teste"}), "missão não concluída")


# --------------------------------------------------------------------------- missões e efeitos

func test_story() -> void:
	Game.new_game()
	Story.update_quests()
	check(not Game.quests.has("tres_luas"), "a missão principal espera a conversa com Ysolde")
	Game.set_flag("ysolde_tres_luas")
	Story.update_quests()
	check(Game.quest_stage("tres_luas") == 0, "a missão principal começa")
	Game.set_flag("bau_gruta_aberto")
	Story.update_quests()
	check(Game.quest_stage("tres_luas") == 1, "a missão avança quando o objetivo se cumpre")
	var copper := Game.copper
	var xp := Game.xp
	Story.apply_effects({"set_flag": ["a", "b"], "give_item": [["pao_viagem", 2]], "take_copper": 10, "xp": 30,
			"journal": {"id": "pista_teste", "title": "Pista", "text": "Texto"}})
	check(Game.has_flag("a") and Game.has_flag("b"), "efeito: flags")
	check(Game.copper == copper - 10, "efeito: pagar")
	check(Game.xp == xp + 30, "efeito: experiência")
	check(Game.has_journal("pista_teste"), "efeito: diário")


func test_save_roundtrip() -> void:
	Game.new_game({"name": "Teste"})
	Game.cell = Vector2i(12, 7)
	Game.set_flag("salvo")
	Game.met["ysolde"] = true
	Game.discovered["praca_poco"] = true
	Game.minutes = 2000
	var text := JSON.stringify(Game.to_dict())
	Game.new_game()
	Game.from_dict(JSON.parse_string(text))
	check(Game.hero.name == "Teste" and Game.cell == Vector2i(12, 7) and Game.minutes == 2000, "save: herói e lugar")
	check(Game.has_flag("salvo") and Game.met.has("ysolde") and Game.discovered.has("praca_poco"), "save: memória")


# --------------------------------------------------------------------------- o mundo

## Responde a caixa de diálogo até ela fechar: avança as falas e escolhe opções
## (picks[n] na n-ésima escolha; acabando a lista, a última opção, que costuma ser a despedida).
func drive_dialogue(dialogue: Node, picks: Array = [], limit: int = 400) -> int:
	var choices := 0
	for step in limit:
		await frames()
		if not dialogue.is_open:
			return choices
		if dialogue._typing and dialogue._typing.is_running():
			dialogue._typing.custom_step(60.0)
		elif dialogue._waiting:
			dialogue.advanced.emit()
		elif dialogue._choosing:
			var count: int = dialogue.option_list.get_child_count()
			var pick: int = picks[choices] if choices < picks.size() else count - 1
			choices += 1
			dialogue._pick(clampi(pick, 0, count - 1))
	check(false, "a conversa terminou")
	return choices


func test_world() -> void:
	Game.new_game({"name": "Teste"})
	var main: Node = MAIN_SCENE.instantiate()
	add_child(main)
	await frames(3)
	var world: Node = main.world
	check(Game.regions.has("vila_primordia") and Game.discovered.has("entrada_vila"), "chegada: vila descoberta")
	check(world.npc_at(Vector2i(28, 13)) == "ysolde", "Ysolde está em casa de manhã")
	# andar
	check(world.try_move(Vector2i(0, -1)), "anda para o norte")
	await world.hero.step_finished
	check(Game.cell == Vector2i(30, 17), "o herói chegou ao tile de cima")
	# água bloqueia
	var shore := _find_shore(world)
	world.load_map("vale_primordia", shore[0], "down")
	check(not world.try_move(shore[1]), "não dá para entrar na água funda")
	check(Game.cell == shore[0], "o herói continua na margem")
	# passagem trancada (Portão Sul) e depois aberta
	world.load_map("vale_primordia", Vector2i(30, 29), "down")
	world.try_move(Vector2i(0, 1))
	await drive_dialogue(main.dialogue)
	await seconds(0.2)
	check(Game.map_id == "vale_primordia", "o Portão Sul está fechado no começo")
	Game.set_flag("rota_aberta")
	world.try_move(Vector2i(0, 1))
	await drive_dialogue(main.dialogue)
	await seconds(0.8)
	check(Game.map_id == "rota_mercadores" and Game.cell == Vector2i(21, 0), "o Portão Sul leva à Rota dos Mercadores")
	check(not world.busy, "a viagem terminou")
	# a agenda: de noite, Kael aparece no cemitério (depois do baú da gruta)
	world.load_map("vale_primordia", Vector2i(30, 18), "down")
	Game.set_flag("bau_gruta_aberto")
	Game.minutes = 22 * 60
	world.refresh_npcs()
	check(world.npc_at(Vector2i(37, 11)) == "kael", "o fantasma de Kael aparece à noite")
	Game.minutes = 9 * 60
	world.refresh_npcs()
	check(world.npc_at(Vector2i(37, 11)) == "", "de dia, Kael some")
	# examinar um local mostra o texto e passa o tempo
	var spot := Vector2i(-1, -1)
	for landmark: Dictionary in Data.map_data("vale_primordia").landmarks:
		var cell := Vector2i(int(landmark.x), int(landmark.y))
		world.load_map("vale_primordia", cell, "down")
		if world.npc_to_talk() == "" and world._verb_portal(cell).is_empty():
			spot = cell
			break
	check(spot != Vector2i(-1, -1), "há um local sem ninguém por perto para examinar")
	var before := Game.minutes
	world.interact()
	await drive_dialogue(main.dialogue)
	check(Game.minutes >= before + 5, "examinar leva alguns minutos")
	main.queue_free()
	await frames(2)


func _find_shore(world: Node) -> Array:
	var rows: Array = Data.map_data("vale_primordia").rows
	for y in range(1, rows.size() - 1):
		for x in range(1, rows[y].length() - 1):
			if rows[y][x] != "~":
				continue
			for delta: Vector2i in [Vector2i(0, 1), Vector2i(0, -1), Vector2i(1, 0), Vector2i(-1, 0)]:
				var shore := Vector2i(x, y) + delta
				if world.passable(shore) and world.portals_at(shore).is_empty():
					return [shore, -delta]
	return [Vector2i(30, 18), Vector2i(0, 0)]


func test_conversations() -> void:
	Game.new_game({"name": "Teste"})
	var main: Node = MAIN_SCENE.instantiate()
	add_child(main)
	await frames(3)
	var world: Node = main.world
	# uma conversa de verdade: chegar perto da Ysolde e apertar E
	world.load_map("vale_primordia", Vector2i(28, 14), "up")
	world.interact()
	var asked := await drive_dialogue(main.dialogue, [0])
	check(asked >= 2, "a conversa com Ysolde teve escolhas")
	check(Game.met.has("ysolde"), "agora o herói conhece Ysolde")
	check(Game.has_flag("visto:ysolde:inicio") and Game.has_flag("visto:ysolde:quem"), "os trechos vistos ficam marcados")
	check(not world.busy, "o mundo volta a andar depois da conversa")
	# todos os NPCs, por vários caminhos: nenhum erro de script em falas, condições ou efeitos
	for npc_id: String in Data.npcs:
		for route in 4:
			main.dialogue.run_npc(npc_id)
			await drive_dialogue(main.dialogue, [route, route, route, route])
			check(not main.dialogue.is_open, "conversa com %s (caminho %d) termina" % [npc_id, route])
	main.queue_free()
	await frames(2)


# --------------------------------------------------------------------------- combate

## Os números do herói e das criaturas batem com os do terminal (rpg/player.py, rpg/monsters.py).
func test_combat_rules() -> void:
	var expected := {
		"guerreiro": {1: [104, 100, 93, 46.0, 0.0], 5: [176, 100, 101, 62.0, 0.0]},
		"mago": {1: [76, 138, 45, 17.0, 15.8], 5: [114, 234, 47, 17.0, 26.2]},
		"sacerdote": {1: [81, 126, 45, 17.0, 15.5], 5: [125, 215, 47, 18.0, 25.9]},
		"ladino": {1: [90, 100, 79, 45.0, 0.0], 5: [144, 100, 97, 58.0, 0.0]},
	}
	for class_id: String in expected:
		for level: int in expected[class_id]:
			Sim.prepare_hero(class_id, level)
			var numbers: Array = expected[class_id][level]
			var got := [HeroStats.max_hp(), HeroStats.max_resource(), HeroStats.armor(), HeroStats.attack_power(),
					HeroStats.spell_power()]
			var same := true
			for index in numbers.size():
				same = same and absf(float(got[index]) - float(numbers[index])) < 0.01
			check(same, "%s nv %d: vida, recurso, armadura e poderes iguais ao terminal (%s)" % [class_id, level, got])
	check(CombatRules.kill_xp(1, 1) == 100 and CombatRules.kill_xp(5, 7) == 154, "XP por abate como no terminal")
	check(CombatRules.kill_xp(10, 3) == 0 and CombatRules.kill_xp(7, 7, true) == 320, "criaturas cinzentas e elites")
	check(CombatRules.armor_mitigation(0, 5) == 0.0 and CombatRules.armor_mitigation(1e9, 1) == 0.75, "armadura")
	check(CombatRules.element_multiplier("fogo", ["fogo"], []) == 1.5, "fraqueza")
	check(CombatRules.element_multiplier("fogo", [], ["fogo"]) == 0.5, "resistência")
	check(CombatRules.element_multiplier("fogo", ["fogo"], ["fogo"]) == 1.0, "fraqueza e resistência se cancelam")
	check(CombatRules.element_multiplier("fogo", [], [], ["fogo"]) == 0.0, "imunidade anula")
	check(CombatRules.monster_curve(2) == [53, 5.5, 59], "curva das criaturas")
	check(CombatRules.effect_seconds(2, "stun", false) == 4.0 and CombatRules.effect_seconds(3, "dot", false) == 9.0,
			"turnos viram segundos")
	var stab := HeroStats.ability("golpe_sinistro")
	check(CombatRules.ability_range(stab) == CombatRules.MELEE_RANGE, "golpe é corpo a corpo")
	Sim.prepare_hero("mago", 1)
	check(CombatRules.ability_range(HeroStats.ability("bola_de_fogo")) == CombatRules.SPELL_RANGE, "magia é à distância")
	check(CombatRules.cast_time("bola_de_fogo") > 0, "a Bola de Fogo leva tempo para conjurar")
	check(CombatRules.cast_time("armadura_de_gelo") == 0.0, "a Armadura de Gelo é instantânea")
	check(Game.action_bar[0] == "attack" and "ability:bola_de_fogo" in Game.action_bar, "barra de ações da classe")
	check(Game.action_bar[9] == "item:pocao_mana_menor", "poção de mana no último atalho de quem usa Mana")


func test_combat() -> void:
	seed(4242)
	Game.new_game({"name": "Teste"})
	var main: Node = MAIN_SCENE.instantiate()
	add_child(main)
	await frames(3)
	var world: Node = main.world
	var combat: Node = world.combat
	combat.rng.seed = 4242
	# criaturas no vale, longe da vila
	check(world.spawner.camps.size() >= 8, "o vale tem acampamentos de criaturas")
	var village: Array = world.map.regions[0].rects[0]
	for monster: Node in world.spawner.alive_monsters():
		check(world.passable(monster.cell), "%s nasceu num tile livre" % monster.unit_name())
		var inside: bool = monster.cell.x >= village[0] and monster.cell.x <= village[2] \
				and monster.cell.y >= village[1] and monster.cell.y <= village[3]
		check(not inside, "nada nasce dentro da vila")
	# clicar mira; Tab mira o mais perto
	var some: Node = world.spawner.alive_monsters()[0]
	check(world.monster_under(some.position - Vector2(0, 8)) == some, "clique acerta a criatura")
	# lutas simuladas (determinísticas): cada classe vence uma criatura do próprio nível
	world.overlay_open = true
	combat.hero_died.disconnect(world._on_hero_died)
	var spot := Sim.open_spot(world)
	for class_id: String in ["guerreiro", "mago", "sacerdote", "ladino"]:
		Sim.prepare_hero(class_id, 4)
		world.load_map("vale_primordia", spot, "down")
		var xp_before := Game.xp
		var result := Sim.fight(world, [["lobo_faminto", 4]], class_id)
		check(result.won, "%s nv 4 vence um lobo faminto nv 4" % class_id)
		check(result.seconds > 3.0 and result.seconds < 40.0,
				"%s: a luta dura alguns segundos (%.1fs)" % [class_id, result.seconds])
		check(Game.xp > xp_before and Game.kills.get("lobo_faminto", 0) == 1, "%s: XP e abate contados" % class_id)
	# selos: acertar os elementos certos enfraquece e depois cancela o golpe concentrado
	Sim.prepare_hero("mago", 5)
	world.load_map("vale_primordia", spot, "down")
	world.spawner.clear()
	var spider: Node = world.spawner.create("aranha_da_mata", 5, world.hero.cell + Vector2i(1, 0))
	spider.animate = false
	var web: Dictionary = Data.monster("aranha_da_mata").abilities[1]
	spider.charging = {"ability": web, "left": 3.0, "total": 3.0, "locks": ["fogo", "fisico"], "broken": [false, false]}
	spider.dodge = 0.0
	combat._break_lock(spider, "fogo")
	check(spider.charging.broken == [true, false], "um selo rompido")
	combat._break_lock(spider, "fisico")
	check(spider.charging.is_empty() and spider.incapacitated() == "stun", "todos os selos: golpe cancelado e atordoado")
	# interrupção (o Chute do ladino)
	spider.remove_effect("stun")
	spider.charging = {"ability": web, "left": 3.0, "total": 3.0, "locks": ["fogo"], "broken": [false]}
	combat._hits = {spider: true}
	combat._apply_spec({"type": "interrupt"}, {"id": "chute", "name": "Chute", "element": "fisico"}, [spider])
	check(spider.charging.is_empty(), "o Chute interrompe o golpe concentrado")
	# conjuração: andar cancela
	combat.set_target(spider)
	Game.resource = HeroStats.max_resource()
	combat.gcd_left = 0.0
	check(combat.use_ability("bola_de_fogo") and not combat.cast.is_empty(), "a Bola de Fogo começa a ser conjurada")
	combat.on_hero_moved()
	check(combat.cast.is_empty(), "andar interrompe a conjuração")
	# poção pela barra de ações
	Game.hp = 10
	Game.give_item("pocao_cura_menor", 1, false)
	combat.item_left = 0.0
	combat.use_slot(8)
	check(Game.hp > 10, "a poção da barra cura")
	# derrota: o herói cai e acorda na capela, sem 10% do cobre
	var fell := [false]
	var on_fall := func() -> void: fell[0] = true
	combat.hero_died.connect(on_fall)
	Game.copper = 1000
	Game.hp = 1
	combat.damage(world.hero, 50.0)
	check(fell[0] and not world.hero.alive(), "o herói cai")
	var lost: int = combat.revive()
	check(lost == 100 and Game.copper == 900, "perde 10% do cobre")
	check(Game.hp == world.hero.maximum_hp() / 2, "acorda com metade da vida")
	combat.hero_died.disconnect(on_fall)
	world.spawner.clear()
	# caçadas das missões
	Game.quests.clear()
	Story.start_quest("ratos")
	for kill in 6:
		Game.record_kill("rato_gigante")
	Story.update_quests()
	check(Game.quest_stage("ratos") == 1, "seis ratos derrotados avançam a missão")
	# encontro fixo: o Alfa Branco na Toca dos Lobos
	combat.hero_died.connect(world._on_hero_died)
	world.overlay_open = false
	Sim.prepare_hero("guerreiro", 7)
	var den: Array = Data.map_data("toca_dos_lobos").start
	world.load_map("toca_dos_lobos", Vector2i(int(den[0]), int(den[1])), "up")
	await frames(2)
	var alpha: Array = []
	for monster: Node in world.spawner.alive_monsters():
		if monster.template_id == "presa_de_gelo":
			alpha.append(monster)
	check(alpha.size() == 1, "o Alfa Branco espera no covil")
	if alpha.size() == 1:
		for member: Node in alpha[0].camp.members.duplicate():
			if member.state != "dead":
				member.hp = 0
				combat._on_monster_death(member)
		await drive_dialogue(main.dialogue)
		check(Game.has_flag("presa_de_gelo_derrotado"), "vencer o chefe marca a vitória")
		check(Game.has_journal("alfa_derrotado"), "e anota o diário")
	main.queue_free()
	await frames(2)
