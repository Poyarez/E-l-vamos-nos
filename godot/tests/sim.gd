extends RefCounted
## Lutas simuladas para testar e balancear o combate em tempo real: o herói (classe e nível)
## contra criaturas coladas nele, num passo fixo de tempo, jogando como uma pessoa jogaria
## (a mesma "rotação" da simulação do terminal: rompe selos, interrompe, bebe poções).
## Do nível 8 em diante o herói usa o equipamento e os talentos da fase, como no terminal.

const STEP := 0.05

## Equipamento da fase da mina e das ruínas (o mesmo da simulação do terminal).
const GEAR := {
	"guerreiro": ["espada_ferro", "escudo_ferro", "cota_ferro", "elmo_ferro", "perneiras_ferro", "botas_ferro",
			"manto_pele_lobo", "amuleto_dente_lobo", "anel_granada"],
	"mago": ["cajado_galho_sussurrante", "vestes_seda", "capuz_domador", "luvas_seda_aranha", "calcas_la",
			"manto_la", "pingente_pedra_da_lua", "anel_prata", "sandalias_linho"],
	"sacerdote": ["maca_ferro", "vestes_seda", "capuz_la", "luvas_seda_aranha", "calcas_la", "manto_la",
			"pingente_pedra_da_lua", "anel_prata", "sandalias_linho"],
	"ladino": ["presa_gelida", "gibao_couro_javali", "capuz_couro_lobo", "botas_couro_javali",
			"cinto_couro_trancado", "manto_pele_lobo", "amuleto_dente_lobo", "anel_granada", "calcas_couro_cru"],
}
const TALENT := {"guerreiro": "armas_mestria", "mago": "fogo_intenso", "sacerdote": "sombra_profunda",
		"ladino": "assassinato_malignos"}
const GEARED_LEVEL := 8


## Um lugar aberto (3x3 de campina, sem locais) no mapa atual.
static func open_spot(world: Node) -> Vector2i:
	var rows: Array = world.map.rows
	for y in range(2, rows.size() - 2):
		for x in range(2, rows[y].length() - 2):
			var cell := Vector2i(x, y)
			var ok: bool = world.terrain_id_at(cell) == "planicie" and world.landmark_at(cell).is_empty()
			for delta: Vector2i in world.DIRECTIONS.values():
				ok = ok and world.terrain_id_at(cell + delta) == "planicie" and world.landmark_at(cell + delta).is_empty()
			if ok:
				return cell
	return Vector2i(30, 18)


## Prepara o herói: classe, nível (com o equipamento e os talentos da fase), vida e recurso
## cheios e as poções da luta.
static func prepare_hero(class_id: String, level: int, potions: Array = []) -> void:
	Game.new_game({"class_id": class_id, "name": "Teste"})
	Game.level = level
	if level >= GEARED_LEVEL:
		for item_id: String in GEAR[class_id]:
			var slot: String = Data.item(item_id).get("slot", "")
			if slot:
				Game.equipment[slot] = item_id
		Game.talents[TALENT[class_id]] = mini(level - 9, 5) if level >= 10 else 0
	HeroStats.invalidate()
	Game.restore()
	Game.action_bar.clear()
	Game.refresh_action_bar()
	for item_id: String in ["pocao_cura_menor", "pocao_cura", "pocao_mana_menor"]:
		Game.items.erase(item_id)
	if not potions.is_empty():
		Game.give_item(potions[0], int(potions[1]), false)


## Uma luta: devolve {won, seconds, hp (fração que sobrou), potions (gastas)}.
static func fight(world: Node, group: Array, class_id: String, max_seconds: float = 180.0) -> Dictionary:
	var combat: Node = world.combat
	var hero: Unit = world.hero
	world.spawner.clear()
	combat.reset()
	combat.cooldowns.clear()
	combat.gcd_left = 0.0
	combat.item_left = 0.0
	combat.combo = 0
	hero.effects.clear()
	var offsets := [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]
	for index in group.size():
		var monster: Node = world.spawner.create(group[index][0], int(group[index][1]), hero.cell + offsets[index])
		monster.animate = false
		monster.camp = {"members": []}
	combat.attack(world.spawner.alive_monsters()[0])
	var potions_before := _potions()
	var seconds := 0.0
	while seconds < max_seconds and hero.alive() and not world.spawner.alive_monsters().is_empty():
		_act(world, class_id)
		combat.step(STEP)
		for monster: Node in world.spawner.alive_monsters():
			monster.think(STEP)
		seconds += STEP
	var result := {"won": hero.alive() and world.spawner.alive_monsters().is_empty(), "seconds": seconds,
			"hp": float(Game.hp) / hero.maximum_hp(), "potions": potions_before - _potions()}
	world.spawner.clear()
	return result


static func _potions() -> int:
	return Game.count_item("pocao_cura_menor") + Game.count_item("pocao_cura") + Game.count_item("pocao_mana_menor")


static func _ready_to(combat: Node, ability_id: String) -> bool:
	if not HeroStats.knows(ability_id) or combat.cooldowns.has(ability_id):
		return false
	var ability := HeroStats.ability(ability_id)
	if Game.resource < HeroStats.ability_cost(ability):
		return false
	return combat._requirements_problem(ability, combat.target).is_empty()


static func _try(combat: Node, ability_id: String) -> bool:
	return _ready_to(combat, ability_id) and combat.use_ability(ability_id)


## O que um jogador faria agora (espelha a simulação do terminal, em rpg/ ... sim4.py).
static func _act(world: Node, class_id: String) -> void:
	var combat: Node = world.combat
	var hero: Unit = world.hero
	if not combat.cast.is_empty() or combat.gcd_left > 0:
		return
	var life := float(Game.hp) / hero.maximum_hp()
	if life < 0.35 and combat.item_left <= 0:
		for potion: String in ["pocao_cura", "pocao_cura_menor"]:
			if Game.count_item(potion) and combat.use_item(potion):
				return
	if HeroStats.resource_id() == "mana" and float(Game.resource) / HeroStats.max_resource() < 0.15 \
			and Game.count_item("pocao_mana_menor") and combat.item_left <= 0:
		combat.use_item("pocao_mana_menor")
		return
	var living: Array = world.spawner.alive_monsters()
	var charging: Array = living.filter(func(monster: Node) -> bool: return not monster.charging.is_empty())
	if not charging.is_empty() and combat.target != charging[0]:
		combat.set_target(charging[0])
		combat.auto_attack = combat.is_melee_class()
	if combat.target == null or not is_instance_valid(combat.target):
		combat.target_next()
	var target: Node = combat.target
	if target == null:
		return
	if not target.charging.is_empty():
		var locks: Array = []
		for index in target.charging.locks.size():
			if not target.charging.broken[index]:
				locks.append(target.charging.locks[index])
		if class_id == "ladino" and _try(combat, "chute"):
			return
		for ability: Dictionary in HeroStats.abilities():
			if ability.get("kind") == "dano" and ability.element in locks and _try(combat, ability.id):
				return
	var several := living.size() > 1
	match class_id:
		"guerreiro":
			if life < 0.4 and _try(combat, "muralha_de_escudo"):
				return
			if _try(combat, "executar"):
				return
			if several and _try(combat, "trovoada"):
				return
			if hero.find_effect("brado").is_empty() and Game.resource >= 25 and _try(combat, "brado_de_batalha"):
				return
			if target.find_effect("dilacerar").is_empty() and target.hp > 40 and _try(combat, "dilacerar"):
				return
			if not _try(combat, "golpe_mortal"):
				_try(combat, "golpe_heroico")
		"mago":
			if hero.find_effect("armadura_gelo").is_empty() and _try(combat, "armadura_de_gelo"):
				return
			if several and _try(combat, "nova_congelante"):
				return
			if not "fogo" in target.resistances and (_try(combat, "pirolancamento") or _try(combat, "impacto_de_fogo")):
				return
			if "arcano" in target.weaknesses and _try(combat, "misseis_arcanos"):
				return
			if "fogo" in target.weaknesses and _try(combat, "bola_de_fogo"):
				return
			if not "gelo" in target.resistances and _try(combat, "seta_de_gelo"):
				return
			if not "fogo" in target.resistances and _try(combat, "bola_de_fogo"):
				return
			_try(combat, "misseis_arcanos")
		"sacerdote":
			if hero.find_effect("fortitude").is_empty() and _try(combat, "palavra_de_poder_fortitude"):
				return
			if life < 0.45 and _try(combat, "cura_menor"):
				return
			if life < 0.75 and hero.find_effect("escudo_luz").is_empty() and _try(combat, "palavra_de_poder_escudo"):
				return
			if life < 0.7 and hero.find_effect("renovar").is_empty() and _try(combat, "renovar"):
				return
			if several and _try(combat, "grito_psiquico"):
				return
			if target.find_effect("dor").is_empty() and target.hp > 40 and not "sombra" in target.resistances \
					and _try(combat, "palavra_sombria_dor"):
				return
			_try(combat, "punicao")
		"ladino":
			if life < 0.4 and _try(combat, "evasao"):
				return
			if combat.combo >= 4 and _try(combat, "eviscerar"):
				return
			if _try(combat, "apunhalar") or _try(combat, "golpe_sinistro"):
				return
			if combat.combo >= 1 and target.hp < 25:
				_try(combat, "eviscerar")
