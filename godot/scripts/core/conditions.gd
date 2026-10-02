class_name Conditions
extends RefCounted
## Condições declarativas dos dados (diálogos, agendas de NPCs, passagens, missões).
## Mesmo formato e mesmas regras de rpg/conditions.py: todas as chaves do bloco precisam
## ser verdadeiras.
##
## flag / not_flag, journal, discovered, class, moral, law, period, night, met, min_level,
## item ("pao", ["pao", 3] ou lista de pares), owns, skill, copper, moon, quest_active,
## quest_done, quest_stage (["missao", n]), talents e any (lista de blocos: basta um).


const KEYS := ["flag", "not_flag", "journal", "discovered", "class", "moral", "law", "period", "night", "met",
		"min_level", "item", "owns", "skill", "copper", "moon", "quest_active", "quest_done", "quest_stage",
		"talents", "any"]


static func as_list(value: Variant) -> Array:
	return value if value is Array else [value]


## "pao" ou ["pao", 3] -> ["pao", 3]
static func item_requirement(value: Variant) -> Array:
	if value is Array:
		return [str(value[0]), int(value[1])]
	return [str(value), 1]


## ["pao", 2] ou [["pao", 2], ["agua", 1]] -> lista de pares (vazia sem valor)
static func item_pairs(value: Variant) -> Array:
	if value == null or (value is Array and value.is_empty()) or (value is String and value.is_empty()):
		return []
	if value is Array and value[0] is Array:
		return value.map(func(entry: Variant) -> Array: return item_requirement(entry))
	return [item_requirement(value)]


## Avalia um bloco "if". met_npc diz se o herói já conhecia o NPC antes da conversa.
static func met(conditions: Variant, met_npc: bool = false) -> bool:
	if conditions == null or not conditions is Dictionary or conditions.is_empty():
		return true
	var alignment: Dictionary = Data.appearance.get("alignments", {}).get(Game.hero.alignment, {})
	for key: String in conditions:
		var value: Variant = conditions[key]
		var ok := true
		match key:
			"flag":
				ok = as_list(value).all(func(flag: String) -> bool: return Game.has_flag(flag))
			"not_flag":
				ok = not as_list(value).any(func(flag: String) -> bool: return Game.has_flag(flag))
			"journal":
				ok = as_list(value).all(func(entry_id: String) -> bool: return Game.has_journal(entry_id))
			"discovered":
				ok = as_list(value).all(func(landmark: String) -> bool: return Game.discovered.has(landmark))
			"class":
				ok = Game.hero.class_id in as_list(value)
			"moral":
				ok = alignment.get("moral", "") in as_list(value)
			"law":
				ok = alignment.get("law", "") in as_list(value)
			"period":
				ok = Game.period() in as_list(value)
			"night":
				ok = Game.is_night() == bool(value)
			"met":
				ok = met_npc == bool(value)
			"min_level":
				ok = Game.level >= int(value)
			"item":
				ok = item_pairs(value).all(func(pair: Array) -> bool: return Game.count_item(pair[0]) >= pair[1])
			"owns":
				ok = as_list(value).all(func(item_id: String) -> bool: return Game.owns(item_id))
			"skill":
				ok = value.keys().all(func(skill: String) -> bool: return Game.skill_level(skill) >= int(value[skill]))
			"copper":
				ok = Game.copper >= int(value)
			"moon":
				ok = Game.moon_phase() in as_list(value)
			"quest_active":
				ok = as_list(value).all(func(quest_id: String) -> bool: return Game.quest_active(quest_id))
			"quest_done":
				ok = as_list(value).all(func(quest_id: String) -> bool: return Game.quest_done(quest_id))
			"quest_stage":
				ok = Game.quest_active(str(value[0])) and Game.quest_stage(str(value[0])) == int(value[1])
			"talents":
				ok = (Game.talent_points_spent() > 0) == bool(value)
			"any":
				ok = value.any(func(block: Variant) -> bool: return met(block, met_npc))
			_:
				push_error("Condição desconhecida: %s" % key)
				ok = false
		if not ok:
			return false
	return true
