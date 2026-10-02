extends Node
## Tela de título: o vale ao fundo, ao entardecer, e o menu. "Novo jogo" abre a criação de
## personagem (nome, gênero, classe, cabelo, armadura e alinhamento) com uma prévia do herói.

const HERO_SCRIPT := preload("res://scripts/world/hero.gd")
const FACINGS := ["down", "left", "up", "right"]

var _facing := 0

@onready var camera: Camera2D = $Backdrop/Camera
@onready var menu: Control = %Menu
@onready var creation: Control = %Creation
@onready var hero_name: LineEdit = %HeroName
@onready var gender: OptionButton = %Gender
@onready var hero_class: OptionButton = %HeroClass
@onready var hair_style: OptionButton = %HairStyle
@onready var hair_color: OptionButton = %HairColor
@onready var armor_color: OptionButton = %ArmorColor
@onready var alignment: OptionButton = %Alignment
@onready var look: Node2D = %Look
@onready var class_info: Label = %ClassInfo


func _ready() -> void:
	%GameTitle.text = Data.rules.get("title", "Crônicas de Primórdia")
	%Subtitle.text = "O Vale de Primórdia — versão Godot"
	%Version.text = "v%s · dados do RPG de terminal" % Data.rules.get("version", "")
	_build_backdrop()
	_fill(gender, Data.appearance.genders, "nao_binario")
	_fill(hero_class, Data.classes.classes, "guerreiro")
	_fill(hair_style, Data.appearance.hair_styles, "curto_desgrenhado")
	_fill(hair_color, Data.appearance.hair_colors, "castanho")
	_fill(armor_color, Data.appearance.armor_colors, "azul_real")
	_fill(alignment, Data.appearance.alignments, "neutro_bom")
	for option: OptionButton in [gender, hero_class, hair_style, hair_color, armor_color, alignment]:
		option.item_selected.connect(_on_choice_changed.unbind(1))
	%NewGame.pressed.connect(_show_creation)
	%Continue.pressed.connect(_continue)
	%Continue.disabled = not Game.has_save()
	%Quit.pressed.connect(get_tree().quit)
	%Back.pressed.connect(_show_menu)
	%Start.pressed.connect(_start)
	hero_name.text_submitted.connect(_start.unbind(1))
	var turn := Timer.new()
	turn.wait_time = 1.2
	turn.autostart = true
	turn.timeout.connect(_turn_preview)
	add_child(turn)
	_on_choice_changed()
	_show_menu()


## O Vale de Primórdia em tiles, com a câmera passeando devagar.
func _build_backdrop() -> void:
	var valley := MapBuilder.instantiate_map("vale_primordia")
	$Backdrop.add_child(valley)
	$Backdrop.move_child(valley, 0)
	var pan := create_tween().set_loops()
	pan.tween_property(camera, "position", Vector2(700, 300), 30.0).set_trans(Tween.TRANS_SINE)
	pan.tween_property(camera, "position", Vector2(300, 180), 30.0).set_trans(Tween.TRANS_SINE)


func _fill(option: OptionButton, entries: Dictionary, default_id: String) -> void:
	option.clear()
	for entry_id: String in entries:
		option.add_item(_label_for(option, entry_id, entries[entry_id]))
		option.set_item_metadata(option.item_count - 1, entry_id)
		if entry_id == default_id:
			option.select(option.item_count - 1)


func _label_for(option: OptionButton, entry_id: String, entry: Dictionary) -> String:
	if option == hero_class:
		return entry.get("names", {}).get(_selected(gender), entry_id)
	return entry.get("name", entry_id)


static func _selected(option: OptionButton) -> String:
	return str(option.get_item_metadata(option.selected)) if option.selected >= 0 else ""


func choices() -> Dictionary:
	var typed := hero_name.text.strip_edges()
	return {
		"name": typed if typed else "Aventureiro", "gender": _selected(gender), "class_id": _selected(hero_class),
		"hair_style": _selected(hair_style), "hair_color": _selected(hair_color),
		"armor_color": _selected(armor_color), "alignment": _selected(alignment),
	}


func _on_choice_changed() -> void:
	# o nome da classe muda com o gênero (Guerreiro/Guerreira)
	for index in hero_class.item_count:
		var class_id := str(hero_class.get_item_metadata(index))
		hero_class.set_item_text(index, _label_for(hero_class, class_id, Data.class_data(class_id)))
	HERO_SCRIPT.apply_look(look, choices())
	var data := Data.class_data(_selected(hero_class))
	var align: Dictionary = Data.appearance.alignments.get(_selected(alignment), {})
	class_info.text = "%s\n%s\n\n%s" % [data.get("tagline", ""), data.get("role", ""), align.get("description", "")]


## A prévia gira devagar para mostrar o herói de todos os lados.
func _turn_preview() -> void:
	_facing = (_facing + 1) % FACINGS.size()
	var column: int = HERO_SCRIPT.COLUMNS[FACINGS[_facing]]
	for sprite: Sprite2D in look.get_children():
		sprite.frame_coords = Vector2i(column, sprite.frame_coords.y)


func _show_menu() -> void:
	creation.visible = false
	menu.visible = true
	%NewGame.grab_focus()


func _show_creation() -> void:
	menu.visible = false
	creation.visible = true
	hero_name.grab_focus()


func _start() -> void:
	Game.new_game(choices())
	get_tree().change_scene_to_file("res://scenes/main.tscn")


func _continue() -> void:
	if Game.load_game():
		get_tree().change_scene_to_file("res://scenes/main.tscn")


func _unhandled_input(event: InputEvent) -> void:
	if creation.visible and event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		_show_menu()
