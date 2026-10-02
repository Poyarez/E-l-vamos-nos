extends Unit
## Uma criatura no mapa: o modelo de rpg/data/monsters.py, com vida, dano e armadura da
## curva do nível, e uma IA no estilo do WoW: passeia perto de onde nasceu, ataca quem chega
## perto (chamando o bando junto), persegue, desiste e volta para casa se for longe demais
## ("evadir", recuperando a vida) e concentra golpes especiais protegidos por selos, que o
## herói pode romper acertando o elemento certo ou interromper.

const CHASE_STEP := 0.2        # segundos por tile perseguindo (o herói é um pouco mais rápido)
const WANDER_STEP := 0.5
const EVADE_STEP := 0.12
const LEASH := 12              # tiles de casa antes de desistir da perseguição
const WANDER_RADIUS := 2
const AGGRO_RADIUS := 3

var template_id := ""
var data: Dictionary = {}
var level := 1
var hp := 1
var max_hp := 1
var damage := Vector2(1, 2)
var base_armor := 0.0
var dodge := 0.05
var element := "fisico"
var weaknesses: Array = []
var resistances: Array = []
var immunities: Array = []
var abilities: Array = []
var elite := false
var boss := false
var cooldowns: Dictionary = {}     # habilidade -> segundos até poder repetir
var used_once: Dictionary = {}
var charging: Dictionary = {}      # golpe sendo concentrado: {ability, left, total, locks, broken}
var home := Vector2i.ZERO
var camp: Dictionary = {}          # o acampamento a que pertence (spawner.gd)
var aggro_center := Vector2i.ZERO  # encontros fixos atacam quem chega perto do local
var aggro_radius := AGGRO_RADIUS
var state := "idle"                # idle, combat, evade ou dead
var targeted := false
var moving := false
var swing_left := 0.0
var world: Node
var combat: Node
var animate := true                # false nas simulações: os passos acontecem na hora

var _think_left := 0.0
var _tween: Tween
var _size := 1.0
var _steps := 0

@onready var sprite: Sprite2D = $Sprite


## Cria a criatura no tile; chamado depois de entrar na árvore.
func setup(id: String, at_level: int, at: Vector2i, world_node: Node, combat_node: Node,
		summoned: bool = false) -> void:
	template_id = id
	data = Data.monster(id)
	world = world_node
	combat = combat_node
	level = at_level
	var curve := CombatRules.monster_curve(level)
	var hp_scale := CombatRules.MONSTER_HP_SCALE
	var damage_scale := CombatRules.MONSTER_DAMAGE_SCALE
	if data.get("elite", false) or data.get("boss", false):
		hp_scale = CombatRules.ELITE_HP_SCALE
		damage_scale = CombatRules.ELITE_DAMAGE_SCALE
	if summoned:
		hp_scale = CombatRules.SUMMON_SCALE
		damage_scale = CombatRules.SUMMON_SCALE
	max_hp = roundi(curve[0] * float(data.get("hp", 1.0)) * hp_scale)
	hp = max_hp
	var average: float = curve[1] * float(data.get("damage", 1.0)) * damage_scale
	damage = Vector2(average * 0.8, average * 1.2)
	base_armor = roundf(curve[2] * float(data.get("armor", 1.0)))
	dodge = float(data.get("dodge", 0.05))
	element = data.get("element", "fisico")
	weaknesses = data.get("weaknesses", [])
	resistances = data.get("resistances", [])
	immunities = data.get("immunities", [])
	abilities = data.get("abilities", [])
	elite = bool(data.get("elite", false))
	boss = bool(data.get("boss", false))
	name = "%s_%d" % [id.to_pascal_case(), get_instance_id()]
	home = at
	aggro_center = at
	if elite or boss:
		aggro_radius = AGGRO_RADIUS + 1
	var art: Dictionary = Data.art.monsters
	_size = float(art.scale.get(id, 1.0))
	sprite.vframes = art.rows.size()
	sprite.frame_coords = Vector2i(0, int(art.rows[id]))
	sprite.scale = Vector2(_size, _size)
	if id in art.ghosts:
		sprite.modulate = Color(1, 1, 1, 0.75)
	_think_left = randf_range(1.0, 4.0)
	place(at)


func place(at: Vector2i) -> void:
	cell = at
	position = MapBuilder.cell_position(at)


# --------------------------------------------------------------------------- Unit

func unit_name() -> String:
	return data.get("name", template_id)


func current_hp() -> int:
	return hp


func set_current_hp(value: int) -> void:
	hp = clampi(value, 0, max_hp)
	queue_redraw()


func maximum_hp() -> int:
	return max_hp


func unit_level() -> int:
	return level


func unit_armor() -> float:
	return base_armor + modifier("armor")


func head_position() -> Vector2:
	return global_position - Vector2(0, 16 * _size + 4)


# --------------------------------------------------------------------------- IA

func _process(delta: float) -> void:
	if state == "dead" or world == null or world.paused:
		return
	think(delta)
	queue_redraw()


func think(delta: float) -> void:
	for key: String in cooldowns.keys():
		cooldowns[key] -= delta
		if cooldowns[key] <= 0:
			cooldowns.erase(key)
	swing_left = maxf(0.0, swing_left - delta)
	match state:
		"idle":
			_idle(delta)
		"combat":
			_fight(delta)
		"evade":
			_evade()


func _idle(delta: float) -> void:
	if combat.can_aggro(self):
		engage()
		return
	_think_left -= delta
	if _think_left > 0 or moving:
		return
	_think_left = randf_range(3.0, 7.0)
	var options: Array = []
	for delta_cell: Vector2i in world.DIRECTIONS.values():
		var next: Vector2i = cell + delta_cell
		if CombatRules.tile_distance(next, home) <= WANDER_RADIUS and _free(next):
			options.append(next)
	if not options.is_empty():
		step_to(options[randi() % options.size()], WANDER_STEP)


## Entra em combate (e chama o resto do bando, como no WoW).
func engage() -> void:
	if state == "dead" or state == "combat":
		return
	state = "combat"
	swing_left = 0.8
	combat.on_monster_engaged(self)
	for member: Variant in camp.get("members", []):
		if is_instance_valid(member) and member != self and member.state == "idle":
			member.engage()


func _fight(delta: float) -> void:
	var hero: Unit = world.hero
	if not hero.alive() or combat.hero_hidden():
		evade()
		return
	if CombatRules.tile_distance(cell, home) > LEASH:
		evade()
		return
	var control := incapacitated()
	if control == "stun" or control == "freeze":
		return
	if control == "fear":
		if not moving:
			_flee_from(hero.cell)
		return
	if not charging.is_empty():
		charging.left -= delta
		if charging.left <= 0:
			combat.finish_charge(self)
		return
	var distance := CombatRules.tile_distance(cell, hero.cell)
	if distance == 0:
		if not moving:
			_step_aside()
		return
	if distance == 1:
		_face(hero.cell)
		if swing_left <= 0 and not moving:
			swing_left = CombatRules.MONSTER_SWING
			combat.monster_act(self)
	elif not moving:
		_chase(hero.cell)


## Desiste da luta: volta correndo para casa, com a vida cheia de novo.
func evade() -> void:
	if state == "dead":
		return
	state = "evade"
	charging = {}
	effects.clear()
	combat.on_monster_evaded(self)


func _evade() -> void:
	if moving:
		return
	if cell == home:
		state = "idle"
		hp = max_hp
		_think_left = randf_range(2.0, 5.0)
		return
	var path: Array = world.find_path(cell, home)
	if path.size() >= 2:
		step_to(path[1], EVADE_STEP)
	else:
		place(home)


func _chase(target: Vector2i) -> void:
	var path: Array = world.find_path(cell, target, true)
	var next := cell
	if path.size() >= 2 and _free(path[1]) and path[1] != target:
		next = path[1]
	else:
		var best := CombatRules.tile_distance(cell, target)
		for delta_cell: Vector2i in world.DIRECTIONS.values():
			var option: Vector2i = cell + delta_cell
			var distance := CombatRules.tile_distance(option, target)
			if option != target and distance < best and world.can_step(cell, delta_cell) and _free(option):
				best = distance
				next = option
	if next != cell:
		step_to(next, CHASE_STEP * _terrain_factor(next))


## O herói pisou no mesmo tile: a criatura recua para um vizinho livre e continua a luta.
func _step_aside() -> void:
	for delta_cell: Vector2i in world.DIRECTIONS.values():
		if world.can_step(cell, delta_cell) and _free(cell + delta_cell):
			step_to(cell + delta_cell, CHASE_STEP)
			return


func _flee_from(danger: Vector2i) -> void:
	var best := cell
	var far := CombatRules.tile_distance(cell, danger)
	for delta_cell: Vector2i in world.DIRECTIONS.values():
		var option: Vector2i = cell + delta_cell
		if CombatRules.tile_distance(option, danger) > far and world.can_step(cell, delta_cell) and _free(option):
			far = CombatRules.tile_distance(option, danger)
			best = option
	if best != cell:
		step_to(best, CHASE_STEP * 1.4)


func _free(target: Vector2i) -> bool:
	return world.passable(target) and world.monster_at(target, self) == null and target != world.hero.cell


func _terrain_factor(target: Vector2i) -> float:
	return clampf(float(world.terrain_at(target).get("cost", 10)) / 10.0, 0.75, 1.8)


func step_to(target: Vector2i, duration: float) -> void:
	_face(target)
	if not animate:
		place(target)
		return
	cell = target
	moving = true
	_steps += 1
	sprite.frame_coords = Vector2i(1, sprite.frame_coords.y)
	_tween = create_tween()
	_tween.tween_property(self, "position", MapBuilder.cell_position(target), duration)
	_tween.tween_callback(_finish_step)


func _finish_step() -> void:
	moving = false
	sprite.frame_coords = Vector2i(0, sprite.frame_coords.y)


func _face(target: Vector2i) -> void:
	if target.x != cell.x:
		sprite.flip_h = target.x > cell.x


# --------------------------------------------------------------------------- morte

func die() -> void:
	state = "dead"
	targeted = false
	charging = {}
	effects.clear()
	if _tween:
		_tween.kill()
	moving = false
	queue_redraw()
	sprite.rotation_degrees = -90 if sprite.flip_h else 90
	sprite.position = Vector2(0, -3)
	sprite.modulate = Color(0.55, 0.5, 0.5, sprite.modulate.a)
	var fade := create_tween()
	fade.tween_interval(6.0)
	fade.tween_property(self, "modulate:a", 0.0, 1.5)
	fade.tween_callback(queue_free)


# --------------------------------------------------------------------------- desenho

## Anel de seleção, barra de vida e a barra do golpe concentrado (com os selos).
func _draw() -> void:
	if state == "dead":
		return
	if targeted:
		draw_set_transform(Vector2(0, -1), 0.0, Vector2(1.0, 0.45))
		draw_arc(Vector2.ZERO, 7.0 * maxf(1.0, _size), 0.0, TAU, 24, Color(1.0, 0.85, 0.3, 0.95), 1.2)
		draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	if state == "idle" and hp >= max_hp and not targeted:
		return
	var top := -16.0 * _size - 5.0
	var width := 14.0
	draw_rect(Rect2(-width / 2 - 1, top - 1, width + 2, 4), Color(0.05, 0.04, 0.08, 0.85))
	var ratio := float(hp) / max_hp
	var color := Color(0.85, 0.2, 0.18) if state == "combat" or targeted else Color(0.6, 0.6, 0.6)
	draw_rect(Rect2(-width / 2, top, width * ratio, 2), color)
	if not charging.is_empty():
		var progress: float = 1.0 - charging.left / charging.total
		draw_rect(Rect2(-width / 2 - 1, top - 5, width + 2, 3), Color(0.05, 0.04, 0.08, 0.85))
		draw_rect(Rect2(-width / 2, top - 4, width * progress, 1), Color(0.88, 0.56, 1.0))
		var locks: Array = charging.locks
		for index in locks.size():
			var x := -float(locks.size() * 4) / 2 + index * 4
			var seal := CombatRules.element_color(locks[index])
			if charging.broken[index]:
				seal = Color(0.3, 0.3, 0.3)
			draw_rect(Rect2(x, top - 9, 3, 3), seal)
