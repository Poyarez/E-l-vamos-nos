"""Itens do jogo (fábrica em ``rpg.items``).

Campos: ``name``, ``type``, ``quality``, ``description`` (texto de ambientação),
``value`` (em moedas de cobre), ``stack`` (tamanho máximo da pilha) e, para
equipamentos, ``slot``, ``armor``, ``damage`` e ``stats``. ``dyeable`` indica peças
que recebem a cor de armadura escolhida na criação do personagem.
"""

QUALITIES = {
    "pobre": {"name": "Pobre", "color": "gray"},
    "comum": {"name": "Comum", "color": "white"},
    "incomum": {"name": "Incomum", "color": "bright_green"},
    "raro": {"name": "Raro", "color": "bright_blue"},
    "epico": {"name": "Épico", "color": "bright_magenta"},
    "lendario": {"name": "Lendário", "color": "yellow bold"},
}

SLOTS = {
    "cabeca": "Cabeça",
    "pescoco": "Pescoço",
    "ombros": "Ombros",
    "peito": "Peito",
    "maos": "Mãos",
    "cintura": "Cintura",
    "pernas": "Pernas",
    "pes": "Pés",
    "anel": "Anel",
    "arma": "Mão principal",
    "secundaria": "Mão secundária",
}

ITEM_TYPES = {
    "arma": "Arma",
    "escudo": "Escudo",
    "armadura": "Armadura",
    "joia": "Joia",
    "consumivel": "Consumível",
    "missao": "Item de missão",
    "diverso": "Diverso",
}

ITEMS = {
    # --- Armas iniciais
    "espada_curta_gasta": {
        "name": "Espada Curta Gasta", "type": "arma", "slot": "arma", "quality": "pobre",
        "damage": [3, 6], "value": 35, "stack": 1,
        "description": "O fio já viu dias melhores, mas o equilíbrio ainda é bom.",
    },
    "escudo_madeira_reforcada": {
        "name": "Escudo de Madeira Reforçada", "type": "escudo", "slot": "secundaria", "quality": "comum",
        "armor": 12, "value": 40, "stack": 1,
        "description": "Carvalho cintado com ferro. Aguenta mais do que aparenta.",
    },
    "cajado_aprendiz": {
        "name": "Cajado de Aprendiz", "type": "arma", "slot": "arma", "quality": "comum",
        "damage": [2, 5], "stats": {"intelecto": 1}, "value": 40, "stack": 1,
        "description": "Freixo entalhado com runas de iniciante. Ainda cheira a biblioteca.",
    },
    "maca_simples": {
        "name": "Maça Simples", "type": "arma", "slot": "arma", "quality": "comum",
        "damage": [3, 5], "stats": {"espirito": 1}, "value": 38, "stack": 1,
        "description": "Uma maça sem adornos, abençoada às pressas por um sacristão sonolento.",
    },
    "adaga_afiada": {
        "name": "Adaga Afiada", "type": "arma", "slot": "arma", "quality": "comum",
        "damage": [2, 4], "stats": {"agilidade": 1}, "value": 36, "stack": 1,
        "description": "Pequena, discreta e mortalmente afiada.",
    },
    "adaga_curva": {
        "name": "Adaga Curva", "type": "arma", "slot": "secundaria", "quality": "pobre",
        "damage": [1, 3], "value": 20, "stack": 1,
        "description": "A lâmina curva foi feita para ganchos e truques sujos.",
    },
    # --- Armaduras iniciais (recebem a cor escolhida)
    "cota_malha_recruta": {
        "name": "Cota de Malha de Recruta", "type": "armadura", "slot": "peito", "quality": "comum",
        "armor": 28, "value": 45, "stack": 1, "dyeable": True,
        "description": "Anéis de ferro trançados sobre um gibão acolchoado.",
    },
    "manto_aprendiz": {
        "name": "Manto de Aprendiz", "type": "armadura", "slot": "peito", "quality": "comum",
        "armor": 6, "stats": {"intelecto": 1}, "value": 30, "stack": 1, "dyeable": True,
        "description": "Bordado com estrelas de linha prateada — algumas já soltas.",
    },
    "vestes_novico": {
        "name": "Vestes de Noviço", "type": "armadura", "slot": "peito", "quality": "comum",
        "armor": 6, "stats": {"espirito": 1}, "value": 30, "stack": 1, "dyeable": True,
        "description": "Linho grosso com o sol nascente da Aurora costurado no peito.",
    },
    "gibao_couro_batido": {
        "name": "Gibão de Couro Batido", "type": "armadura", "slot": "peito", "quality": "comum",
        "armor": 14, "stats": {"agilidade": 1}, "value": 35, "stack": 1, "dyeable": True,
        "description": "Couro endurecido em óleo, silencioso como uma sombra.",
    },
    "calcas_couro_cru": {
        "name": "Calças de Couro Cru", "type": "armadura", "slot": "pernas", "quality": "pobre",
        "armor": 8, "value": 15, "stack": 1,
        "description": "Rangem um pouco a cada passo.",
    },
    "calcas_linho": {
        "name": "Calças de Linho", "type": "armadura", "slot": "pernas", "quality": "pobre",
        "armor": 3, "value": 10, "stack": 1,
        "description": "Leves e frescas. Nenhuma proteção digna de nota.",
    },
    "botas_gastas": {
        "name": "Botas Gastas", "type": "armadura", "slot": "pes", "quality": "pobre",
        "armor": 5, "value": 12, "stack": 1,
        "description": "Solas finas de tanta estrada. Ainda há chão pela frente.",
    },
    "sandalias_linho": {
        "name": "Sandálias de Linho", "type": "armadura", "slot": "pes", "quality": "pobre",
        "armor": 2, "value": 8, "stack": 1,
        "description": "Confortáveis — até a primeira poça de lama.",
    },
    # --- Consumíveis
    "pao_de_viagem": {
        "name": "Pão de Viagem", "type": "consumivel", "quality": "comum", "value": 5, "stack": 20,
        "description": "Duro como pedra, mas sustenta qualquer jornada.",
    },
    "cantil_agua": {
        "name": "Cantil de Água Fresca", "type": "consumivel", "quality": "comum", "value": 5, "stack": 20,
        "description": "Água do poço de Alvorada, ainda gelada.",
    },
    "pocao_cura_menor": {
        "name": "Poção de Cura Menor", "type": "consumivel", "quality": "comum", "value": 25, "stack": 5,
        "description": "Um líquido vermelho que formiga na língua e fecha pequenos cortes.",
    },
    "pocao_mana_menor": {
        "name": "Poção de Mana Menor", "type": "consumivel", "quality": "comum", "value": 25, "stack": 5,
        "description": "Azul cintilante, com gosto de trovão e hortelã.",
    },
    # --- Diversos e missão
    "tocha": {
        "name": "Tocha", "type": "diverso", "quality": "comum", "value": 2, "stack": 10,
        "description": "Breu e estopa num cabo de pinho. Ilumina — e esquenta as mãos.",
    },
    "cartaz_convocacao": {
        "name": "Cartaz de Convocação", "type": "missao", "quality": "comum", "value": 0, "stack": 1,
        "description": (
            "\"PROCURAM-SE AVENTUREIROS. O Vale de Primórdia pede ajuda. Recompensa em ouro. "
            "Procurar a Anciã Ysolde.\""
        ),
    },
    "pingente_pedra_da_lua": {
        "name": "Pingente de Pedra-da-Lua", "type": "joia", "slot": "pescoco", "quality": "raro",
        "stats": {"intelecto": 2, "espirito": 3}, "value": 1500, "stack": 1,
        "description": (
            "Uma pedra leitosa presa em prata antiga. Sob a luz da lua, um crescente brilha "
            "em seu interior — como se faltassem outras duas."
        ),
    },
}

#: Itens que todo herói carrega no início da jornada (além dos itens da classe).
STARTING_ITEMS = [["pao_de_viagem", 4], ["cantil_agua", 2], ["tocha", 2], ["cartaz_convocacao", 1]]
STARTING_COPPER = 250
