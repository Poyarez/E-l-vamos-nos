extends CanvasLayer
## O menu da tecla Esc: continuar, salvar, deixar o tempo passar, abrir o diário, voltar ao
## título ou sair.

signal closed
signal wait_requested
signal journal_requested

var is_open := false

@onready var root: Control = $Root
@onready var info: Label = %Info
@onready var status: Label = %Status


func _ready() -> void:
	%Resume.pressed.connect(close)
	%Save.pressed.connect(_save)
	%Wait.pressed.connect(_close_and_emit.bind(wait_requested))
	%Journal.pressed.connect(_close_and_emit.bind(journal_requested))
	%ToTitle.pressed.connect(get_tree().change_scene_to_file.bind("res://scenes/title.tscn"))
	%Quit.pressed.connect(get_tree().quit)


func open() -> void:
	is_open = true
	root.visible = true
	status.text = ""
	info.text = "%s · %s nível %d\nDia %d, %s (%s) · %s" % [Game.hero.name, Game.class_name_text(), Game.level,
			Game.day(), Game.time_text(), Game.period_name(), Game.moon_phase()]
	%Resume.grab_focus()


func close() -> void:
	is_open = false
	root.visible = false
	closed.emit()


func _close_and_emit(request: Signal) -> void:
	close()
	request.emit()


func _save() -> void:
	status.text = "Jogo salvo." if Game.save_game() else "Não foi possível salvar."


func _unhandled_input(event: InputEvent) -> void:
	if is_open and event.is_action_pressed("menu"):
		get_viewport().set_input_as_handled()
		close()
