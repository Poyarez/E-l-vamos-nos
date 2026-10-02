class_name HeroStats
extends RefCounted
## Os números do herói, calculados dos dados da classe, do equipamento e dos talentos, com as
## mesmas fórmulas de rpg/player.py e rpg/talents.py: atributos, vida, Mana/Raiva/Energia,
## armadura, poder de ataque e mágico, críticos, esquiva e as habilidades conhecidas.
##
## Atributos e talentos ficam guardados num cache, que vale por um quadro (ou até invalidate(),
## chamado quando o nível, o equipamento ou os talentos mudam).

static var _cache: Dictionary = {}
static var _frame := -1


## Esquece os números guardados (nível, equipamento ou talentos mudaram).
static func invalidate() -> void:
	_cache.clear()


static func _cached(key: String) -> Variant:
	var frame := Engine.get_process_frames()
	if frame != _frame:
		_frame = frame
		_cache.clear()
	return _cache.get(key)


static func class_data() -> Dictionary:
	return Data.class_data(Game.hero.class_id)


static func resource_id() -> String:
	return class_data().get("resource", "mana")


static func resource_info() -> Dictionary:
	return Data.classes.get("resources", {}).get(resource_id(), {})


static func resource_name() -> String:
	return resource_info().get("name", "Mana")


## Começa cheia (Mana e Energia) ou vazia (Raiva).
static func starts_full() -> bool:
	return bool(resource_info().get("starts_full", true))


# --------------------------------------------------------------------------- talentos

## Soma dos efeitos de talento de um tipo para uma chave (elemento, habilidade ou atributo).
static func talent_bonus(kind: String, key: String = "") -> float:
	var cache_key := "talent:%s:%s" % [kind, key]
	var known: Variant = _cached(cache_key)
	if known != null:
		return known
	var total := 0.0
	for tree: Dictionary in class_data().get("talent_trees", []):
		for talent: Dictionary in tree.talents:
			var ranks := int(Game.talents.get(talent.id, 0))
			if ranks <= 0:
				continue
			for effect: Dictionary in talent.effects:
				if effect.kind != kind:
					continue
				var effect_key: Variant = effect.get("key")
				if effect_key == null or effect_key == "all" or effect_key == key:
					total += float(effect.get("value", 0)) * ranks
	_cache[cache_key] = total
	return total


static func granted_abilities() -> Array:
	var granted: Array = []
	for tree: Dictionary in class_data().get("talent_trees", []):
		for talent: Dictionary in tree.talents:
			if int(Game.talents.get(talent.id, 0)) > 0:
				for effect: Dictionary in talent.effects:
					if effect.kind == "ability":
						granted.append(effect.key)
	return granted


# --------------------------------------------------------------------------- atributos

static func base_stat(stat_id: String) -> int:
	var data := class_data()
	return int(data.base_stats[stat_id] + data.growth[stat_id] * (Game.level - 1))


static func gear_bonus(stat_id: String) -> int:
	var total := 0
	for item_id: String in Game.equipment.values():
		total += int(Data.item(item_id).get("stats", {}).get(stat_id, 0))
	return total


static func stat(stat_id: String) -> int:
	var cache_key := "stat:" + stat_id
	var known: Variant = _cached(cache_key)
	if known != null:
		return known
	var value := base_stat(stat_id) + gear_bonus(stat_id) + int(talent_bonus("stat", stat_id))
	_cache[cache_key] = value
	return value


static func max_hp() -> int:
	var data := class_data()
	var base: float = data.base_hp + data.hp_per_level * (Game.level - 1) + stat("vigor") * 2
	return roundi(base * (1 + talent_bonus("max_hp_pct")))


static func max_resource() -> int:
	var fixed: Variant = resource_info().get("max")
	if fixed != null:
		return int(fixed)
	var data := class_data()
	var base: float = data.get("base_mana", 0) + data.get("mana_per_level", 0) * (Game.level - 1) \
			+ stat("intelecto") * 3
	return roundi(base * (1 + talent_bonus("max_resource_pct")))


static func armor() -> int:
	var base := stat("agilidade") * 2.0
	for item_id: String in Game.equipment.values():
		base += float(Data.item(item_id).get("armor", 0))
	return roundi(base * (1 + talent_bonus("armor_pct")))


static func attack_power() -> float:
	var total := 0.0
	var factors: Dictionary = class_data().get("attack_power", {})
	for stat_id: String in factors:
		total += stat(stat_id) * float(factors[stat_id])
	return total


static func spell_power() -> float:
	var factors: Dictionary = class_data().get("spell_power", {})
	if factors.is_empty():
		return 0.0
	var total := Game.level * 1.5
	for stat_id: String in factors:
		total += stat(stat_id) * float(factors[stat_id])
	return total


static func crit_chance() -> float:
	return 0.05 + stat("agilidade") / 2000.0 + talent_bonus("crit")


static func spell_crit_chance() -> float:
	return 0.05 + stat("intelecto") / 3000.0 + talent_bonus("spell_crit")


static func dodge() -> float:
	return 0.05 + stat("agilidade") / 2000.0 + talent_bonus("dodge")


## Mana por segundo em combate (o Espírito guia a recuperação, como no terminal).
static func mana_regen() -> float:
	if resource_id() != "mana":
		return 0.0
	return (stat("espirito") * 0.2 + 2) * (1 + talent_bonus("mana_regen_pct")) / CombatRules.TURN


# --------------------------------------------------------------------------- equipamento

## A arma do espaço (arma ou secundária), ou {} se não houver.
static func weapon(slot: String = "arma") -> Dictionary:
	var data := Data.item(Game.equipment.get(slot, ""))
	return data if data.has("damage") else {}


static func has_shield() -> bool:
	return Data.item(Game.equipment.get("secundaria", "")).get("subtype", "") == "escudo"


static func has_dagger() -> bool:
	return weapon("arma").get("subtype", "") == "adaga"


# --------------------------------------------------------------------------- habilidades

## Habilidades conhecidas (as de talento só depois de aprender o talento), por nível.
static func abilities() -> Array:
	var granted := granted_abilities()
	var known: Array = []
	for ability: Dictionary in class_data().get("abilities", []):
		if ability.get("talent"):
			if ability.id in granted:
				known.append(ability)
		elif int(ability.level) <= Game.level:
			known.append(ability)
	return known


static func ability(ability_id: String) -> Dictionary:
	for entry: Dictionary in class_data().get("abilities", []):
		if entry.id == ability_id:
			return entry
	return {}


static func knows(ability_id: String) -> bool:
	for entry: Dictionary in abilities():
		if entry.id == ability_id:
			return true
	return false


static func ability_cost(entry: Dictionary) -> int:
	return maxi(0, int(entry.get("cost", 0) - talent_bonus("cost", entry.id)))


## Recarga em segundos (turnos dos dados × TURN, menos os talentos).
static func ability_cooldown(entry: Dictionary) -> float:
	return maxf(0.0, entry.get("cooldown", 0) - talent_bonus("cooldown", entry.id)) * CombatRules.TURN


static func damage_bonus(element: String, ability_id: String = "") -> float:
	var bonus := talent_bonus("damage_pct", element)
	if ability_id:
		bonus += talent_bonus("ability_pct", ability_id)
	return 1 + bonus
