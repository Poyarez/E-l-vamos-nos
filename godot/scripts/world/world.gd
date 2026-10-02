extends Node2D
## O mundo jogável: o mapa atual em tiles, o herói, os NPCs e os marcadores dos locais.
## As regras são as mesmas do terminal (rpg/world.py e rpg/session.py): terreno, passagens,
## regiões e locais descobertos, exames, segredos, baús e a agenda dos NPCs.

signal location_changed                              # o herói chegou a um tile novo
signal area_discovered(title: String, text: String)  # primeira visita a uma região

const TILE := MapBuilder.TILE_SIZE
const STEP_TIME := 0.14
const ZOOM_LEVELS := [1.0, 1.5, 2.0, 3.0]
const EDGE_MARGIN := 2   # tiles de folga da câmera além da borda do mapa

## id -> deslocamento, como em rpg/world.py (rosa dos ventos em português).
const DIRECTIONS := {
	"n": Vector2i(0, -1), "ne": Vector2i(1, -1), "l": Vector2i(1, 0), "se": Vector2i(1, 1),
	"s": Vector2i(0, 1), "so": Vector2i(-1, 1), "o": Vector2i(-1, 0), "no": Vector2i(-1, -1),
}
const DIRECTION_NAMES := {
	"n": "norte", "ne": "nordeste", "l": "leste", "se": "sudeste",
	"s": "sul", "so": "sudoeste", "o": "oeste", "no": "noroeste",
}
const FACING_VECTORS := {
	"down": Vector2i(0, 1), "up": Vector2i(0, -1), "left": Vector2i(-1, 0), "right": Vector2i(1, 0),
}
const VERB_NAMES := {"entrar": "Entrar", "sair": "Sair", "navegar": "Navegar"}

const BLOCKED_TEXT := {
	"agua": "As águas são fundas e rápidas demais para atravessar aqui.",
	"montanha": "Paredões de rocha bloqueiam o caminho.",
	"cachoeira": "A cachoeira despenca sobre o penhasco; não há como seguir por aí.",
	"parede_gruta": "Rocha maciça bloqueia o caminho.",
	"lago_subterraneo": "A água negra do lago subterrâneo é funda e gelada demais.",
	"porta_selada": "A porta de pedra não se move nem um milímetro.",
	"fogo_violeta": "As chamas violetas não esquentam nada — e é justamente por isso que você não chega perto.",
}

## A cor do mundo em cada período do dia (o CanvasModulate tinge tudo, menos a interface).
const PERIOD_COLORS := {
	"madrugada": Color(0.30, 0.33, 0.58), "amanhecer": Color(0.88, 0.78, 0.82), "manha": Color(1, 1, 1),
	"tarde": Color(1, 0.98, 0.93), "entardecer": Color(0.97, 0.76, 0.62), "noite": Color(0.40, 0.43, 0.70),
}
const INDOOR_COLOR := Color(0.5, 0.48, 0.64)

const NPC_SCENE := preload("res://scenes/world/npc.tscn")
const ICONS := preload("res://art/icons.png")

var dialogue: Node                   # a caixa de diálogo (ligada pelo main.gd)
var map: Dictionary = {}             # dados do mapa atual (Data.map_data)
var ground: TileMapLayer
var busy := false                    # conversa, viagem ou menu em andamento
var region_id := ""

var _landmarks: Dictionary = {}      # Vector2i -> local
var _npc_nodes: Dictionary = {}      # npc_id -> nó do NPC
var _hinted: Dictionary = {}         # locais cuja pista já apareceu nesta sessão
var _last_bump := Vector2i(-9999, -9999)
var _zoom_index := 2
var _light_tween: Tween

@onready var map_holder: Node2D = $Map
@onready var markers: Node2D = $Markers
@onready var actors: Node2D = $Actors
@onready var hero: Node2D = $Actors/Hero
@onready var tint: CanvasModulate = $Tint
@onready var fade: ColorRect = $Fade/Black


func _ready() -> void:
	hero.step_finished.connect(arrive)
	Game.period_changed.connect(_on_period_changed)
	get_viewport().size_changed.connect(_update_camera_limits)


## Começa (ou retoma) a partida no mapa e no tile salvos no Game.
func start() -> void:
	load_map(Game.map_id, Game.cell, Game.facing)
	arrive()


# --------------------------------------------------------------------------- mapa

func load_map(map_id: String, cell: Vector2i, facing: String = "") -> void:
	for child in map_holder.get_children():
		map_holder.remove_child(child)
		child.queue_free()
	for node: Node in _npc_nodes.values():
		node.queue_free()
	_npc_nodes.clear()
	map = Data.map_data(map_id)
	Game.map_id = map_id
	Game.cell = cell
	var instance := MapBuilder.instantiate_map(map_id)
	map_holder.add_child(instance)
	ground = instance.get_node_or_null("Ground")
	_landmarks.clear()
	for landmark: Dictionary in map.get("landmarks", []):
		_landmarks[Vector2i(int(landmark.x), int(landmark.y))] = landmark
	region_id = region_at(cell).get("id", "")
	hero.place(cell, facing)
	Game.facing = hero.facing
	_last_bump = Vector2i(-9999, -9999)
	_update_camera_limits()
	refresh_npcs()
	refresh_markers()
	update_lighting(false)


func outdoor() -> bool:
	return bool(map.get("outdoor", true))


## Id do terreno no tile (lido da camada pintada; "" fora do mapa).
func terrain_id_at(cell: Vector2i) -> String:
	if ground:
		var tile := ground.get_cell_tile_data(cell)
		return str(tile.get_custom_data("terrain")) if tile else ""
	var rows: Array = map.get("rows", [])
	if cell.y < 0 or cell.y >= rows.size() or cell.x < 0 or cell.x >= rows[cell.y].length():
		return ""
	return map.legend.get(rows[cell.y][cell.x], "")


func terrain_at(cell: Vector2i) -> Dictionary:
	return Data.terrain.get(terrain_id_at(cell), {})


func in_bounds(cell: Vector2i) -> bool:
	return terrain_id_at(cell) != ""


func passable(cell: Vector2i) -> bool:
	return bool(terrain_at(cell).get("passable", false))


## Pode andar de `cell` até `cell + delta`? Diagonais não cortam quinas bloqueadas.
func can_step(cell: Vector2i, delta: Vector2i) -> bool:
	if not passable(cell + delta):
		return false
	if delta.x and delta.y:
		return passable(cell + Vector2i(delta.x, 0)) and passable(cell + Vector2i(0, delta.y))
	return true


func region_at(cell: Vector2i) -> Dictionary:
	for region: Dictionary in map.get("regions", []):
		for rect: Array in region.rects:
			if rect[0] <= cell.x and cell.x <= rect[2] and rect[1] <= cell.y and cell.y <= rect[3]:
				return region
	return {}


func landmark_at(cell: Vector2i) -> Dictionary:
	return _landmarks.get(cell, {})


func portals_at(cell: Vector2i) -> Array:
	var found: Array = []
	for portal: Dictionary in map.get("portals", []):
		if int(portal.x) == cell.x and int(portal.y) == cell.y:
			found.append(portal)
	return found


func portal_known(portal: Dictionary) -> bool:
	return not portal.get("requires_flag") or Game.has_flag(portal.requires_flag)


func portal_locked(portal: Dictionary) -> bool:
	if portal.get("unlock_flag"):
		if not Game.has_flag(portal.unlock_flag):
			return true
	elif portal.get("locked", false):
		return true
	return Game.level < int(portal.get("min_level", 0))


static func direction_id(delta: Vector2i) -> String:
	for key: String in DIRECTIONS:
		if DIRECTIONS[key] == delta:
			return key
	return ""


## Direção aproximada (8 pontos) de `origin` para `target`, como em rpg/world.py.
static func direction_between(origin: Vector2i, target: Vector2i) -> String:
	var delta := target - origin
	if delta == Vector2i.ZERO:
		return ""
	if absi(delta.x) > 2 * absi(delta.y):
		delta.y = 0
	elif absi(delta.y) > 2 * absi(delta.x):
		delta.x = 0
	return direction_id(Vector2i(signi(delta.x), signi(delta.y)))


static func facing_for(delta: Vector2i) -> String:
	if delta.x:
		return "right" if delta.x > 0 else "left"
	return "down" if delta.y > 0 else "up"


## Escolhe sempre o mesmo texto para o mesmo lugar (como stable_choice no Python).
func stable_choice(options: Array, salt: String = "") -> String:
	if options.is_empty():
		return ""
	return options[posmod(hash("%s:%d:%d:%s" % [Game.map_id, hero.cell.x, hero.cell.y, salt]), options.size())]


# --------------------------------------------------------------------------- movimento

## Tenta andar um tile. Diagonais bloqueadas deslizam pelo lado livre.
func try_move(delta: Vector2i) -> bool:
	if busy or hero.moving or delta == Vector2i.ZERO:
		return false
	if delta.x and delta.y and not _move_possible(delta):
		for part: Vector2i in [Vector2i(delta.x, 0), Vector2i(0, delta.y)]:
			if _move_possible(part):
				return try_move(part)
	var cell: Vector2i = hero.cell
	hero.face(facing_for(delta))
	Game.facing = hero.facing
	var portal := _edge_portal(cell, delta)
	if not portal.is_empty():
		_travel(portal)
		return true
	var target := cell + delta
	if not in_bounds(target):
		_bump(target, "Não há caminho nessa direção.")
		return false
	if not can_step(cell, delta):
		if passable(target):
			_bump(target, "Não dá para cortar caminho nessa diagonal: siga pelos lados.")
		else:
			_bump(target, BLOCKED_TEXT.get(terrain_id_at(target), "Não é possível seguir nessa direção."))
		return false
	var cost := int(terrain_at(target).get("cost", 10))
	_last_bump = Vector2i(-9999, -9999)
	Game.cell = target
	hero.walk_to(target, STEP_TIME * clampf(cost / 10.0, 0.75, 1.8))
	Game.advance_time(cost)
	return true


func _move_possible(delta: Vector2i) -> bool:
	if not _edge_portal(hero.cell, delta).is_empty():
		return true
	return in_bounds(hero.cell + delta) and can_step(hero.cell, delta)


## Passagem pela borda do mapa (ex.: o Portão Sul) na direção do passo.
func _edge_portal(cell: Vector2i, delta: Vector2i) -> Dictionary:
	var direction := direction_id(delta)
	for portal: Dictionary in portals_at(cell):
		if portal.get("direction", "") == direction and portal_known(portal):
			return portal
	return {}


## Avisa por que não dá para seguir (uma vez por obstáculo, para não repetir a cada tecla).
func _bump(target: Vector2i, text: String) -> void:
	if target != _last_bump:
		_last_bump = target
		Game.notify(text)


## Chegou a um tile: regiões e locais novos rendem experiência, como no terminal.
func arrive() -> void:
	var cell: Vector2i = hero.cell
	var region := region_at(cell)
	if not region.is_empty() and not Game.regions.has(region.id):
		Game.regions[region.id] = true
		var xp := int(region.get("xp", 0))
		Game.notify("Nova área: %s%s" % [region.name, " (+%d XP)" % xp if xp else ""], "area")
		area_discovered.emit(region.name, region.get("intro", ""))
		Game.gain_xp(xp)
	region_id = region.get("id", "")
	var landmark := landmark_at(cell)
	if not landmark.is_empty() and not Game.discovered.has(landmark.id):
		Game.discovered[landmark.id] = true
		var xp := int(landmark.get("xp", 0))
		Game.notify("Local descoberto: %s%s" % [landmark.name, " (+%d XP)" % xp if xp else ""], "discovery")
		Game.gain_xp(xp)
		refresh_markers()
	_sense_landmarks(cell)
	Story.update_quests()
	location_changed.emit()


## Pistas de locais ainda não descobertos por perto ("Você ouve água caindo a leste...").
func _sense_landmarks(cell: Vector2i) -> void:
	for landmark: Dictionary in _landmarks.values():
		if not landmark.get("hint") or landmark.get("hidden", false) or Game.discovered.has(landmark.id):
			continue
		if _hinted.has(landmark.id):
			continue
		var at := Vector2i(int(landmark.x), int(landmark.y))
		if maxi(absi(at.x - cell.x), absi(at.y - cell.y)) > 6:
			continue
		var direction := direction_between(cell, at)
		if direction:
			_hinted[landmark.id] = true
			Game.notify(GameText.plain(landmark.hint.format({"direcao": DIRECTION_NAMES[direction]})), "lore")


# --------------------------------------------------------------------------- passagens

func _travel(portal: Dictionary) -> void:
	busy = true
	await use_portal(portal)
	busy = false


func use_portal(portal: Dictionary) -> void:
	if portal_locked(portal):
		await say(portal.get("label", "Passagem"), [portal.get("locked_text", "A passagem está bloqueada.")])
		return
	var target: Variant = portal.get("target")
	if not target is Array:
		Game.notify("Esse caminho ainda não leva a lugar nenhum.")
		return
	if portal.get("travel_text"):
		await say(portal.get("label", "Passagem"), [portal.travel_text])
	await _fade_to(1.0)
	load_map(str(target[0]), Vector2i(int(target[1]), int(target[2])), hero.facing)
	Game.advance_time(10)
	arrive()
	await _fade_to(0.0)


func _fade_to(alpha: float) -> void:
	var tween := create_tween()
	tween.tween_property(fade, "color:a", alpha, 0.25)
	await tween.finished


# --------------------------------------------------------------------------- interação

## E / Enter / Espaço: conversar, atravessar uma passagem, examinar o local ou olhar em volta.
func interact() -> void:
	if busy or hero.moving:
		return
	busy = true
	var npc_id := npc_to_talk()
	var verb_portal := _verb_portal(hero.cell)
	var landmark := landmark_at(hero.cell)
	if npc_id:
		await talk(npc_id)
	elif not verb_portal.is_empty():
		await use_portal(verb_portal)
	elif not landmark.is_empty():
		await examine(landmark)
	else:
		await look_around()
	busy = false
	location_changed.emit()


## O que o botão de interagir faria agora (para a dica na tela).
func interaction_hint() -> String:
	var npc_id := npc_to_talk()
	if npc_id:
		return "E: conversar com %s" % Data.npcs[npc_id].short
	var portal := _verb_portal(hero.cell)
	if not portal.is_empty():
		return "E: %s — %s" % [VERB_NAMES.get(portal.verb, portal.verb.capitalize()), portal.label]
	var landmark := landmark_at(hero.cell)
	if not landmark.is_empty():
		return "E: examinar" + (" · dormir" if landmark.get("rest", false) else "")
	for edge: Dictionary in portals_at(hero.cell):
		if edge.get("direction") and portal_known(edge):
			return "Siga para o %s: %s" % [DIRECTION_NAMES.get(edge.direction, ""), edge.label]
	return ""


func _verb_portal(cell: Vector2i) -> Dictionary:
	for portal: Dictionary in portals_at(cell):
		if portal.get("verb") and portal_known(portal):
			return portal
	return {}


func npc_at(cell: Vector2i) -> String:
	for npc_id: String in _npc_nodes:
		if _npc_nodes[npc_id].cell == cell:
			return npc_id
	return ""


## Com quem falar: quem está à frente, no mesmo tile ou em volta do herói.
func npc_to_talk() -> String:
	var ahead: Vector2i = hero.cell + FACING_VECTORS[hero.facing]
	for cell: Vector2i in [ahead, hero.cell]:
		var found := npc_at(cell)
		if found:
			return found
	for delta: Vector2i in DIRECTIONS.values():
		var found := npc_at(hero.cell + delta)
		if found:
			return found
	return ""


func talk(npc_id: String) -> void:
	var node: Node2D = _npc_nodes[npc_id]
	node.face_towards(hero.cell)
	if node.cell != hero.cell:
		hero.face(facing_for(node.cell - hero.cell))
	await dialogue.run_npc(npc_id)
	Story.update_quests()
	refresh_npcs()
	refresh_markers()


## Uma caixa de narração com o texto e, se houver, opções. Devolve a opção escolhida.
func say(title: String, paragraphs: Array, options: Array = []) -> int:
	return await dialogue.show_message(title, paragraphs, options)


## Examina o local: pode revelar segredos, abrir baús ou achar tesouros (rpg/session.py).
func examine(landmark: Dictionary) -> void:
	Game.advance_time(5)
	var title: String = landmark.name
	var secret: Dictionary = landmark.get("secret", {})
	var hidden := not secret.is_empty() and not Game.has_flag(secret.flag)
	var needs := _missing_skills(secret.get("skill", {})) if hidden else []
	if hidden and needs.is_empty() and Conditions.met(secret.get("if")):
		var xp := int(secret.get("xp", 0))
		Game.set_flag(secret.flag)
		Game.notify("Segredo descoberto! (+%d XP)" % xp, "secret")
		Game.gain_xp(xp)
		var journal: Variant = secret.get("journal")
		if journal is Dictionary:
			Game.add_journal(secret.flag, journal.title, journal.text, "segredo")
		await say(title, [secret.text])
		return
	var chest: Dictionary = landmark.get("chest", {})
	if not chest.is_empty() and not Game.has_flag(chest.flag):
		await say(title, _open_chest(landmark, chest))
		return
	var loot: Dictionary = landmark.get("loot", {})
	if not loot.is_empty() and not Game.has_flag(loot.flag):
		var xp := int(loot.get("xp", 0))
		Game.set_flag(loot.flag)
		Game.notify("Tesouro encontrado! (+%d XP)" % xp, "treasure")
		for pair: Array in loot.get("items", []):
			Game.give_item(pair[0], int(pair[1]))
		if loot.get("copper", 0):
			Game.give_copper(int(loot.copper))
		Game.gain_xp(xp)
		await say(title, [loot.text])
		return
	var texts: Array = [landmark.get("examine", "") if landmark.get("examine", "") else landmark.description]
	if hidden and secret.get("hint"):
		var extra := " (%s)" % ", ".join(PackedStringArray(needs)) if needs else ""
		texts.append("*%s%s*" % [secret.hint, extra])
	if not landmark.get("rest", false):
		await say(title, texts)
		return
	var sleep_label := "Tirar um cochilo (2 horas)" if _is_daytime() else "Dormir até o amanhecer"
	var choice := await say(title, texts, [sleep_label, "Esperar 1 hora", "Seguir viagem"])
	if choice == 0:
		await say(title, [rest()])
	elif choice == 1:
		wait_hours(1)


## Perícias que faltam para o segredo, já com nome e nível ("Mineração 15").
func _missing_skills(required: Dictionary) -> Array:
	var missing: Array = []
	for skill_id: String in required:
		if Game.skill_level(skill_id) < int(required[skill_id]):
			var skill_name: String = Data.crafting.get("skills", {}).get(skill_id, {}).get("name", skill_id)
			missing.append("%s %d" % [skill_name, int(required[skill_id])])
	return missing


## Baú trancado: abre com a chave certa, quando a condição bate ou com um ladino experiente.
func _open_chest(landmark: Dictionary, chest: Dictionary) -> Array:
	var key: String = chest.get("key", "")
	var how := ""
	if chest.has("if") and Conditions.met(chest["if"]):
		how = chest.get("opens", "O fecho cede sozinho, como se reconhecesse você.")
	elif key and Game.count_item(key):
		if chest.get("consume_key", true):
			Game.take_item(key)
		how = "Você usa %s na fechadura. Clique." % Data.item_name(key)
	elif chest.get("pick") and Game.hero.class_id == "ladino" and Game.level >= int(chest.pick):
		Game.advance_time(10)
		how = "Você trabalha a fechadura com uma gazua improvisada e, depois de alguns minutos, ela cede."
	if how.is_empty():
		var hints: Array = []
		if key:
			hints.append("falta %s" % Data.item_name(key))
		if chest.get("pick"):
			hints.append("um ladino de nível %d conseguiria arrombar" % int(chest.pick))
		var locked: String = chest.get("locked", "Está trancado.")
		var detail := " (%s)" % "; ".join(PackedStringArray(hints)) if hints else ""
		return [landmark.get("examine", landmark.description), "*%s%s*" % [locked, detail]]
	var xp := int(chest.get("xp", 0))
	Game.set_flag(chest.flag)
	Game.notify("Baú aberto! (+%d XP)" % xp, "treasure")
	for pair: Array in chest.get("items", []):
		Game.give_item(pair[0], int(pair[1]))
	if chest.get("copper", 0):
		Game.give_copper(int(chest.copper))
	Game.gain_xp(xp)
	return [how, chest.text]


## Olhar em volta: o texto do terreno (e, às vezes, da região), de dia ou de noite.
func look_around() -> void:
	var terrain := terrain_at(hero.cell)
	var region := region_at(hero.cell)
	var night := outdoor() and Game.is_night()
	var paragraphs: Array = [stable_choice(terrain.get("night" if night else "day", []))]
	var ambient: Array = region.get("night" if night else "day", [])
	if not ambient.is_empty():
		paragraphs.append("*%s*" % stable_choice(ambient, str(Game.day())))
	var title: String = region.get("name", map.name)
	await say("%s · %s" % [title, terrain.get("name", "")], paragraphs)


# --------------------------------------------------------------------------- tempo

func _is_daytime() -> bool:
	return Game.hour() >= 7 and Game.hour() < 17


## Dormir na estalagem: de dia, um cochilo; à noite, até as 7h (e o jogo é salvo).
func rest() -> String:
	if _is_daytime():
		Game.advance_time(120)
		return "Ainda é dia claro. Você tira um cochilo de duas horas num quarto da estalagem."
	Game.advance_time(posmod(7 * 60 - Game.minutes % 1440, 1440))
	var saved := " (Jogo salvo.)" if Game.save_game() else ""
	return "Você dorme profundamente num quarto quente da estalagem e acorda com energia renovada às %s do Dia %d.%s" \
			% [Game.time_text(), Game.day(), saved]


func wait_hours(hours: int) -> void:
	Game.advance_time(hours * 60)
	Game.notify("Você espera %d %s. Agora são %s (%s)." % [hours, "hora" if hours == 1 else "horas",
			Game.time_text(), Game.period_name()], "time")


func _on_period_changed(_period: String) -> void:
	update_lighting(true)
	refresh_npcs()


func update_lighting(animate: bool = true) -> void:
	var color: Color = PERIOD_COLORS.get(Game.period(), Color.WHITE) if outdoor() else INDOOR_COLOR
	hero.light.enabled = not outdoor() or Game.is_night() or Game.is_twilight()
	hero.light.texture_scale = 1.0 if outdoor() else clampf(float(map.get("light", 3)) / 3.0, 0.7, 1.6)
	if _light_tween:
		_light_tween.kill()
	if animate:
		_light_tween = create_tween()
		_light_tween.tween_property(tint, "color", color, 1.5)
	else:
		tint.color = color


# --------------------------------------------------------------------------- NPCs e marcadores

## Onde o NPC está agora: [mapa, tile], ou [] se está fora de cena (agenda com "if" e "map").
func npc_location(npc_id: String) -> Array:
	var npc: Dictionary = Data.npcs[npc_id]
	for rule: Dictionary in npc.get("schedule", []):
		if rule.has("periods") and not Game.period() in rule.periods:
			continue
		if rule.has("if") and not Conditions.met(rule["if"]):
			continue
		return [rule.get("map", npc.map), Vector2i(int(rule.x), int(rule.y))]
	return []


## Põe cada NPC no tile da agenda dele. NPCs no mesmo tile se espalham pelos vizinhos.
func refresh_npcs() -> void:
	var wanted := {}
	var taken := {}
	for npc_id: String in Data.npcs:
		var location := npc_location(npc_id)
		if location.is_empty() or location[0] != Game.map_id:
			continue
		var cell: Vector2i = location[1]
		if taken.has(cell):
			cell = _free_cell_near(cell, taken)
		taken[cell] = true
		wanted[npc_id] = cell
	for npc_id: String in _npc_nodes.keys():
		if not wanted.has(npc_id):
			_npc_nodes[npc_id].queue_free()
			_npc_nodes.erase(npc_id)
	for npc_id: String in wanted:
		if _npc_nodes.has(npc_id):
			_npc_nodes[npc_id].move_to(wanted[npc_id])
			_npc_nodes[npc_id].refresh()
		else:
			var node := NPC_SCENE.instantiate()
			actors.add_child(node)
			node.setup(npc_id, wanted[npc_id])
			_npc_nodes[npc_id] = node


func _free_cell_near(cell: Vector2i, taken: Dictionary) -> Vector2i:
	for radius in [1, 2]:
		for delta: Vector2i in [Vector2i(0, 1), Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, -1),
				Vector2i(1, 1), Vector2i(-1, 1), Vector2i(1, -1), Vector2i(-1, -1)]:
			var candidate: Vector2i = cell + delta * radius
			if passable(candidate) and not taken.has(candidate):
				return candidate
	return cell


## "?" sobre locais ainda não descobertos, estrela nos conhecidos e porta nas passagens.
func refresh_markers() -> void:
	for child in markers.get_children():
		child.queue_free()
	var passages := {}
	for portal: Dictionary in map.get("portals", []):
		if portal_known(portal):
			passages[Vector2i(int(portal.x), int(portal.y))] = true
	for cell: Vector2i in passages:
		_add_marker(cell, int(Data.art.icons.passage), 0.75, false)
	for cell: Vector2i in _landmarks:
		var landmark: Dictionary = _landmarks[cell]
		var discovered := Game.discovered.has(landmark.id)
		if not discovered and not landmark.get("hidden", false):
			_add_marker(cell, int(Data.art.icons.new), 1.0, true)
		elif discovered and not passages.has(cell):
			_add_marker(cell, int(Data.art.icons.known), 0.55, false)


func _add_marker(cell: Vector2i, frame: int, alpha: float, bobbing: bool) -> void:
	var sprite := Sprite2D.new()
	sprite.texture = ICONS
	sprite.hframes = 4
	sprite.frame = frame
	sprite.modulate.a = alpha
	sprite.position = MapBuilder.cell_position(cell) - Vector2(0, TILE * (1.4 if bobbing else 0.5))
	if not bobbing:
		sprite.scale = Vector2(0.6, 0.6)
	markers.add_child(sprite)
	if bobbing:
		var tween := sprite.create_tween().set_loops()
		tween.tween_property(sprite, "position:y", sprite.position.y - 3, 0.6).set_trans(Tween.TRANS_SINE)
		tween.tween_property(sprite, "position:y", sprite.position.y, 0.6).set_trans(Tween.TRANS_SINE)


# --------------------------------------------------------------------------- câmera

func zoom_step(direction: int) -> void:
	_zoom_index = clampi(_zoom_index + direction, 0, ZOOM_LEVELS.size() - 1)
	var level: float = ZOOM_LEVELS[_zoom_index]
	hero.camera.zoom = Vector2(level, level)
	_update_camera_limits()


## A câmera não mostra o vazio além do mapa; mapas pequenos ficam centralizados.
func _update_camera_limits() -> void:
	if map.is_empty():
		return
	var rect := Rect2i(0, 0, map.rows[0].length(), map.rows.size())
	if ground:
		rect = ground.get_used_rect()
	var camera: Camera2D = hero.camera
	var view := get_viewport_rect().size / camera.zoom
	var area := Rect2(Vector2(rect.position * TILE), Vector2(rect.size * TILE))
	# uma margem além da borda, para o herói não ficar colado no canto da tela
	area = area.grow(TILE * EDGE_MARGIN)
	var grow := Vector2(maxf(0, view.x - area.size.x) / 2, maxf(0, view.y - area.size.y) / 2)
	area = area.grow_individual(grow.x, grow.y, grow.x, grow.y)
	camera.limit_left = int(area.position.x)
	camera.limit_top = int(area.position.y)
	camera.limit_right = int(area.end.x)
	camera.limit_bottom = int(area.end.y)
	camera.reset_smoothing()
