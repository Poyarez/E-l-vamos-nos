class_name MapBuilder
extends RefCounted
## Monta os mapas em tiles a partir do desenho em texto dos dados (o mesmo do terminal).
##
## Cada tile do TileSet guarda o id do terreno no dado personalizado "terrain"; é isso que
## o jogo consulta para saber por onde se anda. Assim, quem pinta o mapa no editor do Godot
## (res://world/maps/<mapa>.tscn) muda de verdade o terreno do jogo.

const TILE_SIZE := 16
const TILES_TEXTURE := "res://art/tiles.png"
const TILESET_PATH := "res://world/tileset.tres"
const MAPS_DIR := "res://world/maps/"
const SOURCE_ID := 0

static var _tileset: TileSet


## Um TileSet novo, com todos os terrenos e suas variações (colunas do tiles.png).
static func make_tileset() -> TileSet:
	var tileset := TileSet.new()
	tileset.tile_size = Vector2i(TILE_SIZE, TILE_SIZE)
	tileset.add_custom_data_layer()
	tileset.set_custom_data_layer_name(0, "terrain")
	tileset.set_custom_data_layer_type(0, TYPE_STRING)
	var source := TileSetAtlasSource.new()
	source.texture = load(TILES_TEXTURE)
	source.texture_region_size = Vector2i(TILE_SIZE, TILE_SIZE)
	tileset.add_source(source, SOURCE_ID)
	for terrain_id: String in Data.art.tiles:
		var entry: Array = Data.art.tiles[terrain_id]
		for variant in int(entry[1]):
			var coords := Vector2i(variant, int(entry[0]))
			source.create_tile(coords)
			source.get_tile_data(coords, 0).set_custom_data("terrain", terrain_id)
	return tileset


## O TileSet do projeto (o salvo em res://world, se existir).
static func tileset() -> TileSet:
	if _tileset == null:
		_tileset = load(TILESET_PATH) if ResourceLoader.exists(TILESET_PATH) else make_tileset()
	return _tileset


## Coordenadas no atlas do terreno, com uma variação estável por posição.
static func atlas_coords(terrain_id: String, map_id: String, cell: Vector2i) -> Vector2i:
	var entry: Array = Data.art.tiles.get(terrain_id, Data.art.tiles.planicie)
	var variants := int(entry[1])
	var roll := posmod(hash("%s:%d:%d" % [map_id, cell.x, cell.y]), 8)
	var variant := 0 if roll < 4 else (1 if roll < 7 else 2)
	return Vector2i(mini(variant, variants - 1), int(entry[0]))


## A camada de chão de um mapa, desenhada a partir das linhas de texto dos dados.
static func build_layer(map_id: String) -> TileMapLayer:
	var data := Data.map_data(map_id)
	var layer := TileMapLayer.new()
	layer.name = "Ground"
	layer.tile_set = tileset()
	var rows: Array = data.rows
	for y in rows.size():
		var row: String = rows[y]
		for x in row.length():
			var cell := Vector2i(x, y)
			layer.set_cell(cell, SOURCE_ID, atlas_coords(data.legend[row[x]], map_id, cell))
	return layer


## Uma cena de mapa nova: um Node2D com a camada "Ground".
static func build_map(map_id: String) -> Node2D:
	var root := Node2D.new()
	root.name = map_id.to_pascal_case()
	var layer := build_layer(map_id)
	root.add_child(layer)
	layer.owner = root
	return root


## Posição no mundo dos pés de quem está no tile (centro da borda de baixo).
static func cell_position(cell: Vector2i) -> Vector2:
	return Vector2(cell.x * TILE_SIZE + TILE_SIZE / 2.0, (cell.y + 1) * TILE_SIZE)


static func scene_path(map_id: String) -> String:
	return MAPS_DIR + map_id + ".tscn"


## O mapa para jogar: a cena editada no Godot, se existir; senão, montada na hora.
static func instantiate_map(map_id: String) -> Node2D:
	var path := scene_path(map_id)
	if ResourceLoader.exists(path):
		var scene: PackedScene = load(path)
		return scene.instantiate()
	return build_map(map_id)
