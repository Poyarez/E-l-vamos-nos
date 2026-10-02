extends Node
## Gera os recursos do projeto a partir dos dados: o TileSet (res://world/tileset.tres), uma
## cena por mapa (res://world/maps/<mapa>.tscn, pronta para pintar no editor) e o tema da
## interface (res://ui/theme.tres).
##
## O que já existe NÃO é sobrescrito, porque pode ter sido editado no Godot. Para refazer tudo
## a partir dos dados do Python (depois de mudar um mapa em rpg/data/maps, por exemplo):
##     godot --headless --path godot res://tools/build_project.tscn -- --overwrite
## No editor: abra tools/build_project.tscn e aperte F6 (sem sobrescrever nada).


func _ready() -> void:
	var overwrite := "--overwrite" in OS.get_cmdline_user_args()
	var report := PackedStringArray()
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(MapBuilder.MAPS_DIR))
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(UiTheme.THEME_PATH.get_base_dir()))
	if overwrite or not ResourceLoader.exists(MapBuilder.TILESET_PATH):
		_save(MapBuilder.make_tileset(), MapBuilder.TILESET_PATH, report)
	MapBuilder._tileset = null   # as cenas passam a apontar para o arquivo salvo
	for map_id: String in Data.map_ids:
		var path := MapBuilder.scene_path(map_id)
		if ResourceLoader.exists(path) and not overwrite:
			report.append("mantido: %s" % path)
			continue
		var root := MapBuilder.build_map(map_id)
		var scene := PackedScene.new()
		scene.pack(root)
		_save(scene, path, report)
		root.free()
	if overwrite or not ResourceLoader.exists(UiTheme.THEME_PATH):
		_save(UiTheme.make(), UiTheme.THEME_PATH, report)
	print("\n".join(report))
	get_tree().quit()


func _save(resource: Resource, path: String, report: PackedStringArray) -> void:
	var error := ResourceSaver.save(resource, path)
	if error == OK:
		report.append("gerado: %s" % path)
	else:
		report.append("ERRO %d ao salvar %s" % [error, path])
		push_error("Não foi possível salvar %s (erro %d)" % [path, error])
