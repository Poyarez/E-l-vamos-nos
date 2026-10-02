extends Node
## Põe as criaturas no mapa, como os "acampamentos" do WoW e do RuneScape:
##
## * cada região com tabela de encontros (rpg/data/maps: "encounters") ganha alguns pontos
##   fixos; em cada um nasce um grupo sorteado da tabela, respeitando dia e noite e as
##   condições ("if"). Grupo derrotado renasce depois de RESPAWN_SECONDS, com o herói longe;
## * os encontros fixos dos locais (chefes, emboscadas) aparecem no local enquanto a flag
##   de vitória não estiver ativa e as condições valerem. Vencê-los ativa a flag, entrega os
##   itens e anota o diário, como no terminal.

const MONSTER_SCENE := preload("res://scenes/world/monster.tscn")
const RESPAWN_SECONDS := 45.0
const CAMP_DENSITY := 4.0       # acampamentos por região = tiles × chance de encontro / CAMP_DENSITY
const MAX_CAMPS := 6
const CAMP_SPACING := 4
const SAFE_DISTANCE := 7        # nada nasce tão perto do herói
const MAX_SUMMONED := 4
const SAFE_TERRAINS := ["estrada", "ponte", "calcamento", "construcao"]

var world: Node
var combat: Node
var camps: Array = []           # {region, cell, members, respawn_left, encounters | fixed, encounter, landmark}
var monsters: Array = []


func setup(world_node: Node, combat_node: Node) -> void:
	world = world_node
	combat = combat_node


func _process(delta: float) -> void:
	if world == null or world.paused:
		return
	for camp: Dictionary in camps:
		if camp.get("fixed", false) or camp.respawn_left <= 0:
			continue
		camp.respawn_left -= delta
		if camp.respawn_left <= 0:
			if CombatRules.tile_distance(camp.cell, world.hero.cell) < SAFE_DISTANCE:
				camp.respawn_left = 3.0
			else:
				_spawn_camp(camp)


# --------------------------------------------------------------------------- mapa

## Monta os acampamentos do mapa atual (chamado a cada troca de mapa).
func populate() -> void:
	clear()
	var taken: Array = []
	for region: Dictionary in world.map.get("regions", []):
		if region.has("encounters"):
			_make_camps(region, taken)
	refresh_fixed()


func clear() -> void:
	for monster: Node in monsters:
		if is_instance_valid(monster):
			monster.queue_free()
	monsters.clear()
	camps.clear()


func _make_camps(region: Dictionary, taken: Array) -> void:
	var cells: Array = []
	for rect: Array in region.rects:
		for y in range(int(rect[1]), int(rect[3]) + 1):
			for x in range(int(rect[0]), int(rect[2]) + 1):
				var cell := Vector2i(x, y)
				if _good_spot(cell) and world.region_at(cell).get("id", "") == region.id:
					cells.append(cell)
	if cells.is_empty():
		return
	var encounters: Dictionary = region.encounters
	var count := clampi(roundi(cells.size() * float(encounters.get("chance", 0.05)) / CAMP_DENSITY), 1, MAX_CAMPS)
	var rng := RandomNumberGenerator.new()
	rng.seed = hash("%s:%s" % [world.map.id, region.id])
	for index in range(cells.size() - 1, 0, -1):   # embaralha de um jeito estável
		var other := rng.randi_range(0, index)
		var swap: Vector2i = cells[index]
		cells[index] = cells[other]
		cells[other] = swap
	for cell: Vector2i in cells:
		if count <= 0:
			break
		if taken.any(func(other: Vector2i) -> bool: return CombatRules.tile_distance(cell, other) < CAMP_SPACING):
			continue
		taken.append(cell)
		count -= 1
		var camp := {"region": region.id, "cell": cell, "members": [], "respawn_left": 0.0, "encounters": encounters}
		camps.append(camp)
		if CombatRules.tile_distance(cell, world.hero.cell) < SAFE_DISTANCE:
			camp.respawn_left = 2.0     # nasce quando o herói se afastar
		else:
			_spawn_camp(camp)


func _good_spot(cell: Vector2i) -> bool:
	if not world.passable(cell) or world.terrain_id_at(cell) in SAFE_TERRAINS:
		return false
	if not world.landmark_at(cell).is_empty() or not world.portals_at(cell).is_empty():
		return false
	for npc_id: String in world.npc_cells():
		if CombatRules.tile_distance(cell, world.npc_cells()[npc_id]) <= 2:
			return false
	return true


## Sorteia um grupo da tabela da região (como rpg/monsters.py): [[criatura, nível], ...].
func pick_group(encounters: Dictionary, rng: RandomNumberGenerator) -> Array:
	var groups: Array = []
	var total := 0.0
	for group: Dictionary in encounters.get("groups", []):
		var time: String = group.get("time", "")
		if world.outdoor() and time == "noite" and not Game.is_night():
			continue
		if world.outdoor() and time == "dia" and Game.is_night():
			continue
		if not Conditions.met(group.get("if")):
			continue
		groups.append(group)
		total += float(group.get("weight", 1))
	if groups.is_empty():
		return []
	var roll := rng.randf() * total
	var chosen: Dictionary = groups[-1]
	for group: Dictionary in groups:
		roll -= float(group.get("weight", 1))
		if roll < 0:
			chosen = group
			break
	var picked: Array = []
	for template_id: String in chosen.monsters:
		var levels: Array = chosen.get("levels", Data.monster(template_id).get("levels", [1, 1]))
		picked.append([template_id, rng.randi_range(int(levels[0]), int(levels[1]))])
	return picked


func _spawn_camp(camp: Dictionary) -> void:
	camp.members = camp.members.filter(func(member: Variant) -> bool: return is_instance_valid(member))
	var rng := RandomNumberGenerator.new()
	rng.randomize()
	var group := pick_group(camp.encounters, rng)
	if group.is_empty():
		camp.respawn_left = 20.0       # nada aparece a esta hora; tenta de novo mais tarde
		return
	for pair: Array in group:
		var cell := _free_cell_near(camp.cell)
		if cell == Vector2i(-1, -1):
			continue
		var monster := create(pair[0], int(pair[1]), cell)
		monster.camp = camp
		camp.members.append(monster)


func create(template_id: String, level: int, cell: Vector2i, summoned: bool = false) -> Node:
	var monster: Node = MONSTER_SCENE.instantiate()
	world.actors.add_child(monster)
	monster.setup(template_id, level, cell, world, combat, summoned)
	monsters.append(monster)
	monster.tree_exited.connect(_forget.bind(monster))
	return monster


func _forget(monster: Node) -> void:
	monsters.erase(monster)
	if combat.target == monster:
		combat.set_target(null)


func _free_cell_near(center: Vector2i) -> Vector2i:
	for radius in 3:
		for y in range(center.y - radius, center.y + radius + 1):
			for x in range(center.x - radius, center.x + radius + 1):
				var cell := Vector2i(x, y)
				if CombatRules.tile_distance(cell, center) == radius and world.passable(cell) \
						and monster_at(cell) == null and cell != world.hero.cell:
					return cell
	return Vector2i(-1, -1)


# --------------------------------------------------------------------------- encontros fixos

## Os chefes e emboscadas dos locais: aparecem quando as condições valem (e somem quando
## deixam de valer, se ninguém estiver lutando).
func refresh_fixed() -> void:
	for landmark: Dictionary in world.map.get("landmarks", []):
		var encounter: Dictionary = landmark.get("encounter", {})
		if encounter.is_empty():
			continue
		var camp := _fixed_camp(landmark.id)
		var wanted := not Game.has_flag(encounter.flag) and Conditions.met(encounter.get("if"))
		if wanted and camp.is_empty():
			_spawn_fixed(landmark, encounter)
		elif not wanted and not camp.is_empty() and _all_in_state(_members(camp), "idle"):
			for member: Node in _members(camp):
				member.queue_free()
			camps.erase(camp)


func _fixed_camp(landmark_id: String) -> Dictionary:
	for camp: Dictionary in camps:
		if camp.get("landmark", {}).get("id", "") == landmark_id:
			return camp
	return {}


func _spawn_fixed(landmark: Dictionary, encounter: Dictionary) -> void:
	var center := Vector2i(int(landmark.x), int(landmark.y))
	var camp := {"cell": center, "members": [], "respawn_left": 0.0, "fixed": true, "encounter": encounter,
			"landmark": landmark, "announced": false}
	camps.append(camp)
	for pair: Array in encounter.monsters:
		var cell := _free_cell_near(center)
		if cell == Vector2i(-1, -1):
			continue
		var monster := create(pair[0], int(pair[1]), cell)
		monster.camp = camp
		monster.aggro_center = center
		monster.aggro_radius = int(encounter.get("radius", 1)) + 1
		camp.members.append(monster)


func _all_in_state(members: Array, wanted: String) -> bool:
	for member: Node in members:
		if member.state != wanted:
			return false
	return true


func _members(camp: Dictionary) -> Array:
	return camp.get("members", []).filter(func(member: Variant) -> bool: return is_instance_valid(member))


## Primeira vez que um encontro fixo entra em combate: o texto de abertura, como no terminal.
func announce(monster: Node) -> void:
	var camp: Dictionary = monster.camp
	if not camp.get("fixed", false) or camp.get("announced", false):
		return
	camp.announced = true
	var intro: String = camp.encounter.get("intro", "")
	if intro:
		world.announce(camp.landmark.name, [intro])


# --------------------------------------------------------------------------- mortes e reforços

func on_monster_died(monster: Node) -> void:
	var camp: Dictionary = monster.camp
	if camp.is_empty():
		return
	if not _all_in_state(_members(camp), "dead"):
		return
	if camp.get("fixed", false):
		_complete(camp)
	else:
		camp.respawn_left = RESPAWN_SECONDS


## Vitória num encontro fixo: flag, itens, diário e o texto de vitória.
func _complete(camp: Dictionary) -> void:
	var encounter: Dictionary = camp.encounter
	Game.set_flag(encounter.flag)
	for pair: Array in encounter.get("items", []):
		Game.give_item(pair[0], int(pair[1]))
	var journal: Variant = encounter.get("journal")
	if journal is Dictionary:
		Game.add_journal(journal.id, journal.title, journal.text, "segredo")
	camps.erase(camp)
	Story.update_quests()
	world.refresh_npcs()
	var victory: String = encounter.get("victory", "")
	if victory:
		world.announce(camp.landmark.name, [victory])


## Reforços chamados por uma criatura (o assobio do domador, o chamado da alcateia...).
func summon(caller: Node, template_ids: Array) -> void:
	var camp: Dictionary = caller.camp
	if not camp.has("members"):
		camp["members"] = [caller]
	for template_id: String in template_ids:
		if _members(camp).filter(func(member: Node) -> bool: return member.alive()).size() >= MAX_SUMMONED:
			return
		var cell := _free_cell_near(caller.cell)
		if cell == Vector2i(-1, -1):
			return
		var minion := create(template_id, maxi(1, caller.level - 1), cell, true)
		minion.camp = camp
		minion.home = caller.home
		minion.aggro_center = caller.aggro_center
		camp.members.append(minion)
		minion.engage()


# --------------------------------------------------------------------------- dia e noite

## Ao virar o período, acampamentos parados longe do herói trocam de criaturas (as da noite
## aparecem à noite) e os encontros fixos conferem as condições de novo.
func on_period_changed() -> void:
	for camp: Dictionary in camps:
		if camp.get("fixed", false) or camp.respawn_left > 0:
			continue
		var members := _members(camp)
		if not _all_in_state(members, "idle"):
			continue
		if CombatRules.tile_distance(camp.cell, world.hero.cell) < SAFE_DISTANCE + 2:
			continue
		for member: Node in members:
			member.queue_free()
		camp.members = []
		_spawn_camp(camp)
	refresh_fixed()


# --------------------------------------------------------------------------- consultas

func alive_monsters() -> Array:
	var alive: Array = []
	for monster: Node in monsters:
		if is_instance_valid(monster) and monster.state != "dead":
			alive.append(monster)
	return alive


func monster_at(cell: Vector2i, except: Node = null) -> Node:
	for monster: Node in monsters:
		if is_instance_valid(monster) and monster != except and monster.state != "dead" and monster.cell == cell:
			return monster
	return null
