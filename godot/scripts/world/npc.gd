extends Node2D
## Um NPC no mapa (uma linha de npcs.png). Fantasmas flutuam, translúcidos; quem o herói
## ainda não conhece mostra um "!" sobre a cabeça.

const COLUMNS := {"down": 0, "up": 2, "left": 4, "right": 6}

var npc_id := ""
var cell := Vector2i.ZERO

@onready var sprite: Sprite2D = $Sprite
@onready var mark: Sprite2D = $Mark


## Chamado depois de entrar na árvore (os nós filhos já existem).
func setup(id: String, at: Vector2i) -> void:
	npc_id = id
	name = id.to_pascal_case()
	var art: Dictionary = Data.art.npcs
	var size := float(art.scale.get(id, 1.0))
	sprite.frame_coords = Vector2i(COLUMNS.down, int(art.rows[id]))
	sprite.scale = Vector2(size, size)
	mark.position = Vector2(0, -16 * size - 7)
	var bob := create_tween().set_loops()
	bob.tween_property(mark, "position:y", mark.position.y - 2, 0.5).set_trans(Tween.TRANS_SINE)
	bob.tween_property(mark, "position:y", mark.position.y, 0.5).set_trans(Tween.TRANS_SINE)
	if id in art.ghosts:
		sprite.modulate = Color(0.75, 0.95, 1.0, 0.62)
		var float_tween := create_tween().set_loops()
		float_tween.tween_property(sprite, "position:y", -3.0, 1.3).set_trans(Tween.TRANS_SINE)
		float_tween.tween_property(sprite, "position:y", 0.0, 1.3).set_trans(Tween.TRANS_SINE)
	move_to(at)
	refresh()


func move_to(at: Vector2i) -> void:
	cell = at
	position = MapBuilder.cell_position(at)


func refresh() -> void:
	mark.visible = not Game.met.has(npc_id)


func face(direction: String) -> void:
	sprite.frame_coords = Vector2i(COLUMNS[direction], sprite.frame_coords.y)


## Vira-se para quem puxou conversa.
func face_towards(target: Vector2i) -> void:
	var delta := target - cell
	if delta == Vector2i.ZERO:
		face("down")
	elif absi(delta.x) > absi(delta.y):
		face("right" if delta.x > 0 else "left")
	else:
		face("down" if delta.y > 0 else "up")
