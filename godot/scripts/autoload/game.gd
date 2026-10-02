extends Node
## Estado completo da partida: o herói, onde ele está, o relógio e a memória do mundo
## (flags, diário, locais descobertos, NPCs conhecidos, missões). É o que vai para o save.
## Equivale ao rpg/state.py e a parte do rpg/player.py da versão de terminal.

signal changed                          # algo mudou: a interface se redesenha
signal notified(text: String, kind: String)  # aviso na tela; kind escolhe a cor (veja hud.gd)
signal period_changed(period: String)   # amanheceu, anoiteceu...
signal leveled_up(level: int)

const SAVE_PATH := "user://save.json"
const SAVE_VERSION := 1
const DEFAULT_HERO := {
	"name": "Aventureiro", "gender": "nao_binario", "class_id": "guerreiro",
	"hair_style": "curto_desgrenhado", "hair_color": "castanho", "armor_color": "azul_real",
	"alignment": "neutro_bom",
}

var started := false
var hero: Dictionary = DEFAULT_HERO.duplicate()
var level := 1
var xp := 0
var copper := 0
var items: Dictionary = {}       # item -> quantidade
var equipment: Dictionary = {}   # espaço -> item (por enquanto, o equipamento inicial da classe)
var skills: Dictionary = {}      # perícia -> nível (as perícias chegam numa próxima etapa)
var talents: Dictionary = {}     # talento -> pontos
var hp := 1                      # vida atual (o máximo vem de HeroStats)
var resource := 0                # Mana, Raiva ou Energia atual
var action_bar: Array = []       # 10 atalhos: "attack", "ability:<id>", "item:<id>" ou ""
var kills: Dictionary = {}       # criatura -> quantas já foram derrotadas
var map_id := "vale_primordia"
var cell := Vector2i(30, 18)
var facing := "down"
var minutes := 0                 # minutos desde a meia-noite do Dia 1
var world_seed := 0
var flags: Dictionary = {}
var journal: Array = []          # {id, title, text, day, category}
var discovered: Dictionary = {}  # locais visitados
var regions: Dictionary = {}     # regiões visitadas
var met: Dictionary = {}         # NPCs com quem já conversou
var quests: Dictionary = {}      # missão -> {stage, kills, done, day}


func _ready() -> void:
	_setup_input()


# --------------------------------------------------------------------------- partida

func new_game(choices: Dictionary = {}) -> void:
	hero = DEFAULT_HERO.duplicate()
	hero.merge(choices, true)
	level = 1
	xp = 0
	copper = int(Data.items.get("starting_copper", 0))
	items.clear()
	for pair in Data.items.get("starting_items", []):
		give_item(pair[0], int(pair[1]), false)
	for pair in Data.class_data(hero.class_id).get("starting_items", []):
		give_item(pair[0], int(pair[1]), false)
	equipment = Data.class_data(hero.class_id).get("starting_equipment", {}).duplicate()
	skills.clear()
	talents.clear()
	kills.clear()
	HeroStats.invalidate()
	restore()
	action_bar.clear()
	refresh_action_bar()
	var start_map: Dictionary = Data.map_data("vale_primordia")
	map_id = "vale_primordia"
	cell = Vector2i(int(start_map.start[0]), int(start_map.start[1]))
	facing = "up"
	minutes = int(Data.rules.get("start_minutes", 480))
	world_seed = randi_range(1, 999999)
	flags.clear()
	journal.clear()
	discovered.clear()
	regions.clear()
	met.clear()
	quests.clear()
	add_journal("convocacao", "O cartaz de convocação",
			"O cartaz que trouxe você ao vale pede que os aventureiros procurem a Anciã Ysolde, na Vila de Primórdia.",
			"pista", false)
	started = true
	changed.emit()


# --------------------------------------------------------------------------- relógio

func day() -> int:
	return minutes / 1440 + 1


func hour() -> int:
	return (minutes % 1440) / 60


func time_text() -> String:
	return "%02d:%02d" % [hour(), minutes % 60]


func period() -> String:
	var current: String = Data.rules.periods[0].id
	for entry in Data.rules.periods:
		if hour() >= int(entry.hour):
			current = entry.id
	return current


func period_name() -> String:
	for entry in Data.rules.periods:
		if entry.id == period():
			return entry.name
	return ""


func is_night() -> bool:
	return period() in Data.rules.night_periods


func is_twilight() -> bool:
	return period() in Data.rules.twilight_periods


func moon_phase() -> String:
	var phases: Array = Data.rules.moon_phases
	return phases[posmod(day() - 1 + world_seed, phases.size())]


func advance_time(amount: int) -> void:
	var before := period()
	var before_day := day()
	minutes += max(0, amount)
	if day() != before_day:
		notify("Amanhece o Dia %d." % day(), "time")
	if period() != before:
		period_changed.emit(period())
	changed.emit()


# --------------------------------------------------------------------------- herói

func class_name_text() -> String:
	return Data.class_data(hero.class_id).get("names", {}).get(hero.gender, hero.class_id)


## Palavras usadas nos diálogos: {nome}, {tratamento}, {Bem_vindo}, {classe}...
func forms() -> Dictionary:
	var base: Dictionary = Data.appearance.genders.get(hero.gender, {}).get("forms", {}).duplicate()
	base["classe"] = class_name_text().to_lower()
	for key in base.keys():
		base[_capitalize_first(key)] = _capitalize_first(base[key])
	base["nome"] = hero.name
	return base


func xp_needed() -> int:
	var table: Array = Data.rules.get("xp_to_next", [])
	if level >= int(Data.rules.get("max_level", 60)) or level - 1 >= table.size():
		return 0
	return int(table[level - 1])


func gain_xp(amount: int) -> void:
	if amount <= 0 or xp_needed() == 0:
		return
	xp += amount
	while xp_needed() > 0 and xp >= xp_needed():
		xp -= xp_needed()
		level += 1
		HeroStats.invalidate()
		notify("NÍVEL %d! Você se sente mais forte." % level, "level")
		for ability: Dictionary in HeroStats.class_data().get("abilities", []):
			if int(ability.level) == level and not ability.get("talent"):
				notify("Nova habilidade: %s" % ability.name, "level")
		restore()
		refresh_action_bar()
		leveled_up.emit(level)
	changed.emit()


## Vida cheia; recurso no estado de descanso (a Raiva zera, Mana e Energia enchem).
func restore() -> void:
	hp = HeroStats.max_hp()
	resource = HeroStats.max_resource() if HeroStats.starts_full() else 0


## Põe na barra de ações as habilidades novas e, no fim, poções (como um jogador faria no WoW).
func refresh_action_bar() -> void:
	while action_bar.size() < 10:
		action_bar.append("")
	if action_bar[0].is_empty():
		action_bar[0] = "attack"
	for ability: Dictionary in HeroStats.abilities():
		var entry := "ability:%s" % ability.id
		if entry in action_bar:
			continue
		for index in range(1, 8):
			if action_bar[index].is_empty():
				action_bar[index] = entry
				break
	if action_bar[8].is_empty():
		action_bar[8] = "item:pocao_cura_menor"
	if action_bar[9].is_empty():
		action_bar[9] = "item:pocao_mana_menor" if HeroStats.resource_id() == "mana" else "item:pao_de_viagem"


## Conta uma criatura derrotada (para as missões de caçada).
func record_kill(template_id: String) -> void:
	kills[template_id] = int(kills.get(template_id, 0)) + 1
	for quest_id: String in quests:
		var entry: Dictionary = quests[quest_id]
		if entry.get("done", false):
			continue
		var hunt: Variant = Story.current_stage(quest_id).get("goal", {}).get("kill")
		if hunt is Dictionary and template_id in hunt.get("monsters", []):
			entry["kills"] = int(entry.get("kills", 0)) + 1


func skill_level(skill_id: String) -> int:
	return int(skills.get(skill_id, 1))


func talent_points_spent() -> int:
	var total := 0
	for talent_id in talents:
		total += int(talents[talent_id])
	return total


# --------------------------------------------------------------------------- itens e dinheiro

func count_item(item_id: String) -> int:
	return int(items.get(item_id, 0))


func give_item(item_id: String, quantity: int = 1, announce: bool = true) -> void:
	if quantity <= 0:
		return
	items[item_id] = count_item(item_id) + quantity
	if announce:
		notify("Recebido: %s x%d" % [Data.item_name(item_id), quantity], "item")
	changed.emit()


## Possui o item, na mochila ou equipado.
func owns(item_id: String) -> bool:
	return count_item(item_id) > 0 or item_id in equipment.values()


func take_item(item_id: String, quantity: int = 1) -> bool:
	if count_item(item_id) < quantity:
		return false
	items[item_id] = count_item(item_id) - quantity
	if items[item_id] <= 0:
		items.erase(item_id)
	changed.emit()
	return true


func give_copper(amount: int) -> void:
	copper += amount
	notify("Recebido: %s" % money_text(amount), "item")
	changed.emit()


## 12345 de cobre -> "1o 23p 45c" (ouro, prata e cobre, como no WoW)
static func money_text(amount: int) -> String:
	var gold := amount / 10000
	var silver := (amount / 100) % 100
	var bronze := amount % 100
	if gold:
		return "%do %dp %dc" % [gold, silver, bronze]
	if silver:
		return "%dp %dc" % [silver, bronze]
	return "%dc" % bronze


# --------------------------------------------------------------------------- memória do mundo

func has_flag(flag: String) -> bool:
	return bool(flags.get(flag, false))


func set_flag(flag: String, value: bool = true) -> void:
	flags[flag] = value
	changed.emit()


func has_journal(entry_id: String) -> bool:
	for entry in journal:
		if entry.id == entry_id:
			return true
	return false


## Anota no diário. Devolve false se a anotação já existia.
func add_journal(entry_id: String, title: String, text: String, category: String = "pista",
		announce: bool = true) -> bool:
	if has_journal(entry_id):
		return false
	journal.append({"id": entry_id, "title": title, "text": text, "day": day(), "category": category})
	if announce:
		notify("Diário atualizado: %s" % title, "journal")
	changed.emit()
	return true


func notify(text: String, kind: String = "") -> void:
	notified.emit(text, kind)


func quest_active(quest_id: String) -> bool:
	return quests.has(quest_id) and not quests[quest_id].get("done", false)


func quest_done(quest_id: String) -> bool:
	return quests.has(quest_id) and quests[quest_id].get("done", false)


## Etapa atual da missão (0 = a primeira), ou -1 se ela não começou.
func quest_stage(quest_id: String) -> int:
	return int(quests[quest_id].get("stage", 0)) if quests.has(quest_id) else -1


# --------------------------------------------------------------------------- save

func to_dict() -> Dictionary:
	return {
		"version": SAVE_VERSION, "hero": hero, "level": level, "xp": xp, "copper": copper, "items": items,
		"equipment": equipment, "hp": hp, "resource": resource, "action_bar": action_bar, "kills": kills,
		"skills": skills, "talents": talents, "map": map_id, "x": cell.x, "y": cell.y, "facing": facing,
		"minutes": minutes, "seed": world_seed, "flags": flags, "journal": journal,
		"discovered": discovered.keys(), "regions": regions.keys(), "met": met.keys(), "quests": quests,
	}


func from_dict(data: Dictionary) -> void:
	hero = DEFAULT_HERO.duplicate()
	hero.merge(data.get("hero", {}), true)
	level = int(data.get("level", 1))
	xp = int(data.get("xp", 0))
	copper = int(data.get("copper", 0))
	items = {}
	for item_id in data.get("items", {}):
		items[item_id] = int(data.items[item_id])
	equipment = data.get("equipment", {})
	kills = data.get("kills", {})
	skills = data.get("skills", {})
	talents = data.get("talents", {})
	map_id = data.get("map", "vale_primordia")
	if not map_id in Data.map_ids:
		map_id = "vale_primordia"
	cell = Vector2i(int(data.get("x", 30)), int(data.get("y", 18)))
	facing = data.get("facing", "down")
	minutes = int(data.get("minutes", 480))
	world_seed = int(data.get("seed", 1))
	flags = data.get("flags", {})
	journal = data.get("journal", [])
	discovered = _as_set(data.get("discovered", []))
	regions = _as_set(data.get("regions", []))
	met = _as_set(data.get("met", []))
	quests = data.get("quests", {})
	HeroStats.invalidate()
	hp = clampi(int(data.get("hp", HeroStats.max_hp())), 1, HeroStats.max_hp())
	resource = clampi(int(data.get("resource", 0)), 0, HeroStats.max_resource())
	action_bar = data.get("action_bar", [])
	refresh_action_bar()
	started = true
	changed.emit()


func has_save() -> bool:
	return FileAccess.file_exists(SAVE_PATH)


func save_game() -> bool:
	var file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if file == null:
		notify("Não foi possível salvar o jogo.", "warn")
		return false
	file.store_string(JSON.stringify(to_dict(), "\t"))
	file.close()
	return true


func load_game() -> bool:
	if not has_save():
		return false
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(SAVE_PATH))
	if not parsed is Dictionary:
		return false
	from_dict(parsed)
	return true


# --------------------------------------------------------------------------- utilidades

static func _capitalize_first(text: String) -> String:
	return text.substr(0, 1).to_upper() + text.substr(1)


static func _as_set(values: Array) -> Dictionary:
	var result := {}
	for value in values:
		result[value] = true
	return result


## Controles: setas ou WASD para andar, E/Enter/Espaço para interagir, Tab para mirar, F para
## atacar, 1 a 0 para a barra de ações, T para esperar uma hora, J para o diário, Esc para o
## menu e +/- (ou a roda do mouse) para o zoom. Também funciona com controle (direcional ou
## analógico, A, X, B, Y, LB, RB e Start). Ficam aqui, e não no project.godot, para ser fácil
## de ler e mudar.
func _setup_input() -> void:
	var keys := {
		"move_up": [KEY_W, KEY_UP], "move_down": [KEY_S, KEY_DOWN],
		"move_left": [KEY_A, KEY_LEFT], "move_right": [KEY_D, KEY_RIGHT],
		"interact": [KEY_E, KEY_ENTER, KEY_KP_ENTER, KEY_SPACE],
		"wait": [KEY_T], "journal": [KEY_J], "menu": [KEY_ESCAPE],
		"zoom_in": [KEY_EQUAL, KEY_KP_ADD], "zoom_out": [KEY_MINUS, KEY_KP_SUBTRACT],
		"target_next": [KEY_TAB], "attack": [KEY_F],
		"slot_1": [KEY_1, KEY_KP_1], "slot_2": [KEY_2, KEY_KP_2], "slot_3": [KEY_3, KEY_KP_3],
		"slot_4": [KEY_4, KEY_KP_4], "slot_5": [KEY_5, KEY_KP_5], "slot_6": [KEY_6, KEY_KP_6],
		"slot_7": [KEY_7, KEY_KP_7], "slot_8": [KEY_8, KEY_KP_8], "slot_9": [KEY_9, KEY_KP_9],
		"slot_10": [KEY_0, KEY_KP_0],
	}
	var buttons := {
		"move_up": JOY_BUTTON_DPAD_UP, "move_down": JOY_BUTTON_DPAD_DOWN,
		"move_left": JOY_BUTTON_DPAD_LEFT, "move_right": JOY_BUTTON_DPAD_RIGHT,
		"interact": JOY_BUTTON_A, "journal": JOY_BUTTON_Y, "menu": JOY_BUTTON_START,
		"target_next": JOY_BUTTON_RIGHT_SHOULDER, "attack": JOY_BUTTON_X,
		"slot_2": JOY_BUTTON_B, "slot_3": JOY_BUTTON_LEFT_SHOULDER,
	}
	var sticks := {
		"move_up": [JOY_AXIS_LEFT_Y, -1.0], "move_down": [JOY_AXIS_LEFT_Y, 1.0],
		"move_left": [JOY_AXIS_LEFT_X, -1.0], "move_right": [JOY_AXIS_LEFT_X, 1.0],
	}
	var wheel := {"zoom_in": MOUSE_BUTTON_WHEEL_UP, "zoom_out": MOUSE_BUTTON_WHEEL_DOWN}
	for action: String in keys:
		if InputMap.has_action(action):
			continue
		InputMap.add_action(action)
		for keycode: Key in keys[action]:
			var key := InputEventKey.new()
			key.physical_keycode = keycode
			InputMap.action_add_event(action, key)
		if buttons.has(action):
			var button := InputEventJoypadButton.new()
			button.button_index = buttons[action]
			InputMap.action_add_event(action, button)
		if sticks.has(action):
			var motion := InputEventJoypadMotion.new()
			motion.axis = sticks[action][0]
			motion.axis_value = sticks[action][1]
			InputMap.action_add_event(action, motion)
		if wheel.has(action):
			var scroll := InputEventMouseButton.new()
			scroll.button_index = wheel[action]
			InputMap.action_add_event(action, scroll)
