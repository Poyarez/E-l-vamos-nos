extends Unit
## O herói no mapa: três camadas de sprite (corpo, roupa e cabelo) tingidas com as cores
## escolhidas na criação, andando de tile em tile. Também é quem luta: a vida e o recurso
## ficam no Game (vão para o save) e os números vêm de HeroStats.

signal step_finished

## Primeira coluna de cada direção em hero.png (a seguinte é o passo).
const COLUMNS := {"down": 0, "up": 2, "left": 4, "right": 6}

var facing := "down"
var moving := false

var _steps := 0
var _tween: Tween

@onready var body: Sprite2D = $Body
@onready var clothes: Sprite2D = $Clothes
@onready var hair: Sprite2D = $Hair
@onready var camera: Camera2D = $Camera
@onready var light: PointLight2D = $Light


func _ready() -> void:
	refresh_look()


# --------------------------------------------------------------------------- Unit

func unit_name() -> String:
	return Game.hero.name


func is_hero() -> bool:
	return true


func current_hp() -> int:
	return Game.hp


func set_current_hp(value: int) -> void:
	Game.hp = clampi(value, 0, maximum_hp())


func maximum_hp() -> int:
	return HeroStats.max_hp() + int(modifier("max_hp"))


func unit_level() -> int:
	return Game.level


func unit_armor() -> float:
	return HeroStats.armor() + modifier("armor")


func head_position() -> Vector2:
	return global_position - Vector2(0, 22)


# --------------------------------------------------------------------------- aparência e passos


## Aplica a aparência do herói atual (roupa e cabelo).
func refresh_look() -> void:
	apply_look(self, Game.hero)


## Usado também pela prévia da tela de criação: qualquer nó com Body, Clothes e Hair.
static func apply_look(node: Node, look: Dictionary) -> void:
	var art: Dictionary = Data.art.hero
	var clothes_sprite: Sprite2D = node.get_node("Clothes")
	var hair_sprite: Sprite2D = node.get_node("Hair")
	clothes_sprite.modulate = Color(Data.art.armor_colors.get(look.get("armor_color", ""), "#2f4fa3"))
	var shape: String = art.hair_shapes.get(look.get("hair_style", ""), "curto")
	hair_sprite.visible = shape != "careca"
	if hair_sprite.visible:
		hair_sprite.frame_coords = Vector2i(hair_sprite.frame_coords.x, int(art.hair_rows[shape]))
		hair_sprite.modulate = Color(Data.art.hair_colors.get(look.get("hair_color", ""), "#6b4226"))


func place(target: Vector2i, direction: String = "") -> void:
	if _tween:
		_tween.kill()
	moving = false
	cell = target
	position = MapBuilder.cell_position(cell)
	face(direction if direction else facing)
	camera.reset_smoothing()


func face(direction: String) -> void:
	facing = direction
	_set_pose(false)


## Anda até o tile vizinho em `duration` segundos.
func walk_to(target: Vector2i, duration: float) -> void:
	cell = target
	moving = true
	_steps += 1
	_set_pose(true)
	_tween = create_tween()
	_tween.tween_property(self, "position", MapBuilder.cell_position(target), duration)
	_tween.parallel().tween_callback(_set_pose.bind(false)).set_delay(duration * 0.5)
	_tween.tween_callback(_finish_step)


## Avanço rápido até um tile (a Investida do guerreiro).
func dash_to(target: Vector2i) -> void:
	walk_to(target, 0.12)


func _finish_step() -> void:
	moving = false
	step_finished.emit()


## Quadro parado ou de passo; andando para cima ou para baixo, o passo alterna a perna.
func _set_pose(stepping: bool) -> void:
	var column: int = COLUMNS[facing] + (1 if stepping else 0)
	var mirrored := stepping and facing in ["down", "up"] and _steps % 2 == 0
	for sprite: Sprite2D in [body, clothes, hair]:
		sprite.frame_coords = Vector2i(column, sprite.frame_coords.y)
		sprite.flip_h = mirrored
