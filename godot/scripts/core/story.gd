class_name Story
extends RefCounted
## Efeitos dos diálogos e o andamento das missões: o mesmo motor dirigido por dados de
## rpg/npcs.py (apply_effects) e rpg/quests.py (start, update), agora sobre o estado do Game.

const EFFECT_KEYS := ["set_flag", "journal", "xp", "give_item", "take_item", "give_copper", "take_copper",
		"restore", "open_shop", "start_quest", "reset_talents"]


static func apply_effects(effects: Variant) -> void:
	if not effects is Dictionary or effects.is_empty():
		return
	for key: String in effects:
		if not key in EFFECT_KEYS:
			push_error("Efeito de diálogo desconhecido: %s" % key)
	for flag: String in Conditions.as_list(effects.get("set_flag", [])):
		Game.set_flag(flag)
	for entry: Dictionary in Conditions.as_list(effects.get("journal", [])):
		Game.add_journal(entry.id, entry.title, entry.text, entry.get("category", "pista"))
	for pair: Array in Conditions.item_pairs(effects.get("give_item")):
		Game.give_item(pair[0], pair[1])
	for pair: Array in Conditions.item_pairs(effects.get("take_item")):
		Game.take_item(pair[0], mini(pair[1], Game.count_item(pair[0])))
	if effects.has("give_copper"):
		Game.give_copper(int(effects.give_copper))
	if effects.has("take_copper"):
		var amount := mini(Game.copper, int(effects.take_copper))
		Game.copper -= amount
		Game.notify("Você paga %s." % Game.money_text(amount), "item")
	if effects.get("reset_talents", false):
		var refunded := Game.talent_points_spent()
		Game.talents.clear()
		HeroStats.invalidate()
		Game.notify("Seus talentos foram esquecidos: %s para você gastar de novo."
				% ("1 ponto volta" if refunded == 1 else "%d pontos voltam" % refunded), "level")
	if effects.has("start_quest"):
		start_quest(effects.start_quest)
	if effects.has("xp"):
		Game.notify("Conhecimento adquirido! (+%d XP)" % int(effects.xp), "xp")
		Game.gain_xp(int(effects.xp))
	if effects.get("restore", false):
		Game.notify("Sua vida e seu vigor foram restaurados.", "level")
	if effects.get("open_shop", false):
		Game.notify("(As lojas chegam numa próxima etapa da versão Godot.)", "time")
	Game.changed.emit()


# --------------------------------------------------------------------------- missões

static func quest(quest_id: String) -> Dictionary:
	return Data.quests.get("quests", {}).get(quest_id, {})


## Começa a missão (se ainda não começou). Devolve true se começou agora.
static func start_quest(quest_id: String) -> bool:
	if Game.quests.has(quest_id) or quest(quest_id).is_empty():
		return false
	Game.quests[quest_id] = {"stage": 0, "kills": 0, "done": false, "day": Game.day()}
	var data := quest(quest_id)
	Game.notify("Nova missão: %s" % data.name, "quest")
	Game.notify(GameText.plain(data.stages[0].text), "lore")
	Game.changed.emit()
	return true


static func current_stage(quest_id: String) -> Dictionary:
	var stages: Array = quest(quest_id).get("stages", [])
	var index := Game.quest_stage(quest_id)
	return stages[index] if index >= 0 and index < stages.size() else {}


## Itens da recompensa: os de todos mais os da classe do herói.
static func reward_items(quest_id: String) -> Array:
	var rewards: Dictionary = quest(quest_id).get("rewards", {})
	var pairs := Conditions.item_pairs(rewards.get("items"))
	pairs.append_array(Conditions.item_pairs(rewards.get("class_items", {}).get(Game.hero.class_id)))
	return pairs


static func _goal_met(goal: Dictionary, kills: int) -> bool:
	var conditions := goal.duplicate()
	conditions.erase("kill")
	if not Conditions.met(conditions):
		return false
	return not goal.has("kill") or kills >= int(goal.kill.count)


## Começa as missões automáticas e avança as etapas cumpridas (com recompensas no fim).
## Chamado depois de cada ação que muda o mundo (conversas, exames, passos).
static func update_quests() -> void:
	for quest_id: String in Data.quests.get("quests", {}):
		var start: Variant = quest(quest_id).get("start")
		if not Game.quests.has(quest_id) and start is Dictionary and Conditions.met(start):
			start_quest(quest_id)
	for quest_id: String in Game.quests.keys():
		var entry: Dictionary = Game.quests[quest_id]
		var data := quest(quest_id)
		if data.is_empty():
			continue
		while not entry.get("done", false):
			var stage := current_stage(quest_id)
			if stage.is_empty() or not _goal_met(stage.goal, int(entry.get("kills", 0))):
				break
			for pair: Array in Conditions.item_pairs(stage.get("take_item")):
				Game.take_item(pair[0], mini(pair[1], Game.count_item(pair[0])))
			entry.stage = int(entry.stage) + 1
			entry.kills = 0
			if int(entry.stage) >= data.stages.size():
				entry.done = true
				_complete(quest_id)
			else:
				Game.notify("Missão atualizada — %s: %s" % [data.name, GameText.plain(data.stages[entry.stage].text)], "quest")
	Game.changed.emit()


static func _complete(quest_id: String) -> void:
	var data := quest(quest_id)
	var rewards: Dictionary = data.get("rewards", {})
	Game.notify("Missão concluída: %s!" % data.name, "quest")
	if data.has("ending"):
		Game.notify(GameText.plain(data.ending), "lore")
	for flag: String in Conditions.as_list(rewards.get("set_flag", [])):
		Game.set_flag(flag)
	for pair: Array in reward_items(quest_id):
		Game.give_item(pair[0], pair[1])
	if rewards.get("copper", 0):
		Game.give_copper(int(rewards.copper))
	if rewards.get("xp", 0):
		Game.notify("+%d XP" % int(rewards.xp), "xp")
		Game.gain_xp(int(rewards.xp))
	var journal: Variant = rewards.get("journal")
	if journal is Dictionary:
		Game.add_journal(journal.id, journal.title, journal.text, "missão")
