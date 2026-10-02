extends Node
## A partida em andamento: liga o mundo à interface, à caixa de diálogo, ao diário e ao menu,
## e transforma o teclado (ou o controle) em passos e ações: andar, interagir, mirar (Tab),
## atacar (F) e usar a barra de ações (1 a 0). O mouse fica com o mundo e com a barra.

@onready var world: Node2D = $World
@onready var hud: CanvasLayer = $Hud
@onready var dialogue: CanvasLayer = $DialogueBox
@onready var journal: CanvasLayer = $Journal
@onready var pause_menu: CanvasLayer = $PauseMenu
@onready var floating_text: CanvasLayer = $FloatingText


func _ready() -> void:
	if not Game.started:
		Game.new_game()   # cena aberta direto no editor (F6): começa com o herói padrão
	world.dialogue = dialogue
	floating_text.world = world
	world.combat.floating.connect(floating_text.show_text)
	hud.bind(world)
	pause_menu.wait_requested.connect(world.wait_hours.bind(1))
	pause_menu.journal_requested.connect(journal.open)
	world.start()


func _overlay_open() -> bool:
	return journal.is_open or pause_menu.is_open or dialogue.is_open


## Andar: segurar a direção faz o herói seguir de tile em tile (diagonais valem); sem tecla
## apertada, ele segue o caminho de um clique ou vai até o alvo.
func _process(_delta: float) -> void:
	world.overlay_open = journal.is_open or pause_menu.is_open
	if _overlay_open() or world.busy or world.hero.moving:
		return
	var direction := Vector2i(_axis("move_left", "move_right"), _axis("move_up", "move_down"))
	if direction != Vector2i.ZERO:
		world.stop_walking()
		world.try_move(direction)
	else:
		world.follow()


static func _axis(negative: String, positive: String) -> int:
	var value := Input.get_axis(negative, positive)
	return 0 if absf(value) < 0.5 else signi(roundi(value))


func _unhandled_input(event: InputEvent) -> void:
	if _overlay_open():
		return
	if event.is_action_pressed("menu"):
		get_viewport().set_input_as_handled()
		if world.combat.target != null:
			world.combat.set_target(null)   # Esc primeiro tira o alvo, como no WoW
		else:
			pause_menu.open()
	elif event.is_action_pressed("journal"):
		get_viewport().set_input_as_handled()
		journal.open()
	elif event.is_action_pressed("zoom_in"):
		world.zoom_step(1)
	elif event.is_action_pressed("zoom_out"):
		world.zoom_step(-1)
	elif world.busy:
		return
	elif event.is_action_pressed("target_next"):
		get_viewport().set_input_as_handled()
		world.combat.target_next()
	elif event.is_action_pressed("attack"):
		get_viewport().set_input_as_handled()
		world.combat.toggle_attack()
	elif _slot_pressed(event) >= 0:
		get_viewport().set_input_as_handled()
		world.combat.use_slot(_slot_pressed(event))
	elif world.hero.moving:
		return
	elif event.is_action_pressed("interact"):
		get_viewport().set_input_as_handled()
		world.interact()
	elif event.is_action_pressed("wait"):
		get_viewport().set_input_as_handled()
		if world.combat.in_combat():
			world.combat.error.emit("Você está em combate!")
		else:
			world.wait_hours(1)


func _slot_pressed(event: InputEvent) -> int:
	for index in 10:
		if event.is_action_pressed("slot_%d" % (index + 1)):
			return index
	return -1
