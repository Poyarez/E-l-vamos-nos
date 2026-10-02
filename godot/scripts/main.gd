extends Node
## A partida em andamento: liga o mundo à interface, à caixa de diálogo, ao diário e ao menu,
## e transforma o teclado (ou o controle) em passos e ações.

@onready var world: Node2D = $World
@onready var hud: CanvasLayer = $Hud
@onready var dialogue: CanvasLayer = $DialogueBox
@onready var journal: CanvasLayer = $Journal
@onready var pause_menu: CanvasLayer = $PauseMenu


func _ready() -> void:
	if not Game.started:
		Game.new_game()   # cena aberta direto no editor (F6): começa com o herói padrão
	world.dialogue = dialogue
	hud.bind(world)
	pause_menu.wait_requested.connect(world.wait_hours.bind(1))
	pause_menu.journal_requested.connect(journal.open)
	world.start()


func _overlay_open() -> bool:
	return journal.is_open or pause_menu.is_open or dialogue.is_open


## Andar: segurar a direção faz o herói seguir de tile em tile (diagonais valem).
func _process(_delta: float) -> void:
	if _overlay_open() or world.busy or world.hero.moving:
		return
	var direction := Vector2i(_axis("move_left", "move_right"), _axis("move_up", "move_down"))
	if direction != Vector2i.ZERO:
		world.try_move(direction)


static func _axis(negative: String, positive: String) -> int:
	var value := Input.get_axis(negative, positive)
	return 0 if absf(value) < 0.5 else signi(roundi(value))


func _unhandled_input(event: InputEvent) -> void:
	if _overlay_open():
		return
	if event.is_action_pressed("menu"):
		get_viewport().set_input_as_handled()
		pause_menu.open()
	elif event.is_action_pressed("journal"):
		get_viewport().set_input_as_handled()
		journal.open()
	elif event.is_action_pressed("zoom_in"):
		world.zoom_step(1)
	elif event.is_action_pressed("zoom_out"):
		world.zoom_step(-1)
	elif world.busy or world.hero.moving:
		return
	elif event.is_action_pressed("interact"):
		get_viewport().set_input_as_handled()
		world.interact()
	elif event.is_action_pressed("wait"):
		get_viewport().set_input_as_handled()
		world.wait_hours(1)
