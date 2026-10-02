extends Node
## O "banco de dados" do jogo: os JSON de res://data, exportados do Python por
## tools/export_godot_data.py. Mapas, NPCs, itens e regras nascem no Python e chegam
## aqui sem redigitar nada.

const DATA_DIR := "res://data/"

var terrain: Dictionary = {}
var npcs: Dictionary = {}
var items: Dictionary = {}          # items, qualities, slots, types, starting_items...
var classes: Dictionary = {}        # classes, resources, stats, talent_start_level
var appearance: Dictionary = {}     # genders, hair_styles, hair_colors, armor_colors, alignments
var quests: Dictionary = {}
var crafting: Dictionary = {}       # perícias, pontos de coleta, receitas
var rules: Dictionary = {}          # relógio, períodos, fases da lua, curva de XP...
var art: Dictionary = {}            # onde está cada coisa nas imagens de res://art
var map_ids: Array = []

var _maps: Dictionary = {}


func _ready() -> void:
	load_all()


func load_all() -> void:
	terrain = _read("terrain.json")
	npcs = _read("npcs.json")
	items = _read("items.json")
	classes = _read("classes.json")
	appearance = _read("appearance.json")
	quests = _read("quests.json")
	crafting = _read("crafting.json")
	rules = _read("rules.json")
	art = _read("art.json")
	map_ids = _read("maps/index.json")
	_maps.clear()


func map_data(map_id: String) -> Dictionary:
	if not _maps.has(map_id):
		_maps[map_id] = _read("maps/%s.json" % map_id)
	return _maps[map_id]


func item(item_id: String) -> Dictionary:
	return items.get("items", {}).get(item_id, {})


func item_name(item_id: String) -> String:
	return item(item_id).get("name", item_id)


func class_data(class_id: String) -> Dictionary:
	return classes.get("classes", {}).get(class_id, {})


func _read(file_name: String) -> Variant:
	var path := DATA_DIR + file_name
	if not FileAccess.file_exists(path):
		push_error("Arquivo de dados não encontrado: %s" % path)
		return {}
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if parsed == null:
		push_error("JSON inválido: %s" % path)
		return {}
	return parsed
