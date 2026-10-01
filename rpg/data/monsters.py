"""Monstros (fábrica em ``rpg.monsters``).

Como no WoW, vida, dano e armadura seguem uma curva por nível; cada modelo só diz o
quanto se afasta dela (``hp``, ``damage``, ``armor`` — 1.0 é a média). ``levels`` é a
faixa de níveis em que a criatura aparece. ``elite`` dobra a experiência; ``boss``
impede a fuga.

Habilidades de monstro:

* ``chance`` e ``cooldown`` (em turnos) controlam a frequência;
* ``damage`` é um multiplicador do dano básico; ``element`` define a escola;
* ``charge`` (turnos) + ``locks`` criam os **selos** (estilo Sea of Stars): enquanto a
  criatura concentra o golpe, cada acerto do elemento certo rompe um selo. Romper todos
  cancela o golpe e atordoa a criatura; romper alguns enfraquece o golpe e anula os
  efeitos extras;
* ``effects`` no herói: ``dot`` (``power`` = fração do dano básico por turno), ``stun``,
  ``freeze``, ``debuff`` e ``drain_mana``; e na própria criatura: ``heal_self`` e ``buff_self``;
* ``summon``: lista de criaturas chamadas; ``hp_below`` + ``once`` disparam uma única vez
  quando a vida cai abaixo da fração indicada.

Saque: ``{"item", "chance" (%), "qty"}`` ou ``{"one_of": [...], "chance"}`` (um item ao acaso).
"""

FAMILIES = {
    "fera": "Fera",
    "aracnideo": "Aracnídeo",
    "espirito": "Espírito",
    "humanoide": "Humanoide",
}

MONSTERS = {
    # ------------------------------------------------------------------ arredores da vila (nv 1-3)
    "corvo_ladrao": {
        "name": "Corvo Ladrão", "family": "fera", "levels": [1, 2],
        "hp": 0.65, "damage": 0.75, "armor": 0.4, "dodge": 0.12, "attack": "bica",
        "description": "Corvos enormes e espertos que roubam tudo o que brilha — inclusive de aventureiros distraídos.",
        "abilities": [
            {"id": "bicada_nos_olhos", "name": "Bicada nos Olhos", "chance": 0.2, "cooldown": 3, "damage": 1.1,
             "effects": [{"type": "debuff", "id": "cego", "name": "Visão turva", "stat": "hit", "value": -0.25,
                          "turns": 2}]},
        ],
        "loot": [{"item": "pena_corvo", "chance": 60, "qty": [1, 2]}, {"item": "bugiganga_brilhante", "chance": 25}],
        "copper": [2, 9],
    },
    "javali_jovem": {
        "name": "Javali Jovem", "family": "fera", "levels": [1, 3],
        "hp": 1.0, "damage": 0.9, "armor": 1.1, "attack": "chifra",
        "weaknesses": ["gelo"],
        "description": "Javalis novos, ainda sem as cerdas grossas dos adultos, mas já com muito mau humor.",
        "abilities": [
            {"id": "investida_selvagem", "name": "Investida Selvagem", "chance": 0.2, "cooldown": 3, "damage": 1.5},
        ],
        "loot": [{"item": "carne_javali", "chance": 55}, {"item": "couro_javali", "chance": 35},
                 {"item": "presa_javali", "chance": 15}],
    },
    "rato_gigante": {
        "name": "Rato Gigante", "family": "fera", "levels": [1, 3],
        "hp": 0.8, "damage": 0.9, "armor": 0.6, "attack": "morde",
        "weaknesses": ["fogo"],
        "description": "Ratos do tamanho de cães, surgidos de buracos no chão depois das tremuras. Só saem à noite.",
        "abilities": [
            {"id": "mordida_infecta", "name": "Mordida Infecta", "chance": 0.25, "cooldown": 2, "damage": 0.8,
             "effects": [{"type": "dot", "id": "infeccao", "name": "Infecção", "power": 0.3, "turns": 3,
                          "element": "natureza"}]},
        ],
        "loot": [{"item": "rabo_rato", "chance": 65}],
        "copper": [0, 3],
    },
    "lagarto_ribeirao": {
        "name": "Lagarto do Ribeirão", "family": "fera", "levels": [2, 3],
        "hp": 1.0, "damage": 0.9, "armor": 1.5, "attack": "morde",
        "weaknesses": ["gelo"], "resistances": ["natureza"],
        "description": "Lagartos de escamas verdes que tomam sol nas pedras do ribeirão e mordem quem chega perto.",
        "abilities": [
            {"id": "chicotada_cauda", "name": "Chicotada de Cauda", "chance": 0.25, "cooldown": 2, "damage": 1.4},
        ],
        "loot": [{"item": "escama_lagarto", "chance": 50, "qty": [1, 3]}],
    },
    # ------------------------------------------------------------------ Floresta Sussurrante (nv 2-6)
    "lobo_faminto": {
        "name": "Lobo Faminto", "family": "fera", "levels": [2, 3],
        "hp": 0.9, "damage": 1.0, "armor": 0.9, "attack": "morde",
        "weaknesses": ["fogo"],
        "description": "Lobos magros e desesperados, expulsos das matas profundas pela própria alcateia.",
        "loot": [{"item": "pele_lobo", "chance": 40}, {"item": "carne_lobo", "chance": 45},
                 {"item": "presa_lobo", "chance": 20}],
    },
    "lobo_cinzento": {
        "name": "Lobo Cinzento", "family": "fera", "levels": [3, 5],
        "hp": 1.0, "damage": 1.05, "armor": 1.0, "attack": "morde",
        "weaknesses": ["fogo"],
        "description": "O lobo comum da Floresta Sussurrante. Caça em dupla e nunca recua.",
        "abilities": [
            {"id": "mordida_dilacerante", "name": "Mordida Dilacerante", "chance": 0.25, "cooldown": 2,
             "damage": 1.0,
             "effects": [{"type": "dot", "id": "sangrando", "name": "Sangrando", "power": 0.3, "turns": 2}]},
        ],
        "loot": [{"item": "pele_lobo", "chance": 55}, {"item": "presa_lobo", "chance": 30},
                 {"item": "carne_lobo", "chance": 45}, {"item": "capuz_couro_lobo", "chance": 4},
                 {"item": "amuleto_dente_lobo", "chance": 3}],
    },
    "aranha_da_mata": {
        "name": "Aranha da Mata", "family": "aracnideo", "levels": [3, 5],
        "hp": 0.9, "damage": 1.0, "armor": 0.8, "attack": "pica",
        "weaknesses": ["fogo"], "resistances": ["natureza"],
        "description": ("Aranhas do tamanho de um escudo que tecem teias entre os troncos e injetam um veneno "
                        "dormente."),
        "abilities": [
            {"id": "picada_venenosa", "name": "Picada Venenosa", "chance": 0.3, "cooldown": 2, "damage": 0.7,
             "element": "natureza",
             "effects": [{"type": "dot", "id": "veneno", "name": "Veneno", "power": 0.35, "turns": 3,
                          "element": "natureza"}]},
            {"id": "teia_pegajosa", "name": "Teia Pegajosa", "chance": 0.3, "cooldown": 4, "charge": 1,
             "locks": ["fogo", "fisico"], "damage": 0.6, "element": "natureza",
             "announce": "A aranha começa a tecer uma teia enorme ao seu redor!",
             "effects": [{"type": "stun", "turns": 1, "name": "Teia"}]},
        ],
        "loot": [{"item": "teia_pegajosa", "chance": 55, "qty": [1, 2]}, {"item": "glandula_veneno", "chance": 30},
                 {"item": "luvas_seda_aranha", "chance": 4}],
    },
    "javali_espinhento": {
        "name": "Javali Espinhento", "family": "fera", "levels": [3, 5],
        "hp": 1.2, "damage": 1.05, "armor": 1.3, "attack": "chifra",
        "weaknesses": ["gelo"],
        "description": "Javalis adultos de dorso espinhento. Raspam o chão antes de investir — preste atenção.",
        "abilities": [
            {"id": "investida_furiosa", "name": "Investida Furiosa", "chance": 0.3, "cooldown": 3, "charge": 1,
             "locks": ["gelo", "fisico"], "damage": 2.2,
             "announce": "O javali raspa o chão e abaixa a cabeça, pronto para investir!"},
        ],
        "loot": [{"item": "carne_javali", "chance": 60}, {"item": "couro_javali", "chance": 50},
                 {"item": "presa_javali", "chance": 30}, {"item": "botas_couro_javali", "chance": 4}],
    },
    "espirito_sussurrante": {
        "name": "Espírito Sussurrante", "family": "espirito", "levels": [4, 6],
        "hp": 0.85, "damage": 0.9, "armor": 0.0, "attack": "toca com dedos gelados",
        "element": "sombra", "weaknesses": ["sagrado", "fogo"], "resistances": ["fisico", "sombra"],
        "description": ("Ecos de vozes antigas presos à floresta. Só aparecem à noite, e armas comuns mal "
                        "os tocam."),
        "abilities": [
            {"id": "sussurro_enlouquecedor", "name": "Sussurro Enlouquecedor", "chance": 0.35, "cooldown": 3,
             "charge": 2, "locks": ["sagrado", "fisico", "arcano"], "damage": 1.8, "element": "sombra",
             "announce": "O espírito começa a sussurrar o seu nome, cada vez mais alto...",
             "effects": [{"type": "drain_mana", "value": 0.2}, {"type": "stun", "turns": 1, "name": "Pavor"}]},
        ],
        "loot": [{"item": "ectoplasma", "chance": 45}, {"item": "essencia_sussurrante", "chance": 20},
                 {"item": "cajado_galho_sussurrante", "chance": 3}],
    },
    "lobo_gelido": {
        "name": "Lobo de Olhos Azuis", "family": "fera", "levels": [5, 6],
        "hp": 1.05, "damage": 1.1, "armor": 1.0, "attack": "morde",
        "weaknesses": ["fogo"], "resistances": ["gelo"],
        "description": ("Lobos de pelo eriçado e olhos de um azul gelado, corrompidos por algo. O uivo deles "
                        "congela o sangue — literalmente."),
        "abilities": [
            {"id": "uivo_gelido", "name": "Uivo Gélido", "chance": 0.3, "cooldown": 3, "charge": 1,
             "locks": ["fogo", "fisico"], "damage": 1.9, "element": "gelo",
             "announce": "O lobo ergue o focinho e o ar ao redor dele começa a congelar!",
             "effects": [{"type": "debuff", "id": "lento", "name": "Lentidão", "stat": "damage_dealt",
                          "value": -0.25, "turns": 2}]},
        ],
        "loot": [{"item": "pele_lobo", "chance": 50}, {"item": "presa_lobo", "chance": 35},
                 {"item": "fragmento_gelo_eterno", "chance": 25}, {"item": "manto_pele_lobo", "chance": 4}],
    },
    # ------------------------------------------------------------------ Toca dos Lobos (nv 4-7)
    "morcego_caverna": {
        "name": "Morcego das Cavernas", "family": "fera", "levels": [4, 5],
        "hp": 0.6, "damage": 0.85, "armor": 0.4, "dodge": 0.15, "attack": "morde",
        "weaknesses": ["arcano"],
        "description": "Morcegos de asas largas que vivem nas tocas e túneis. Rápidos e difíceis de acertar.",
        "abilities": [
            {"id": "guincho", "name": "Guincho Estridente", "chance": 0.25, "cooldown": 3, "damage": 0.5,
             "effects": [{"type": "debuff", "id": "tontura", "name": "Tontura", "stat": "hit", "value": -0.2,
                          "turns": 2}]},
        ],
        "loot": [{"item": "asa_morcego", "chance": 55, "qty": [1, 2]}],
    },
    "varek_domador": {
        "name": "Varek, o Domador", "family": "humanoide", "levels": [6, 6],
        "hp": 1.6, "damage": 0.95, "armor": 1.2, "attack": "chicoteia",
        "weaknesses": ["sagrado"], "resistances": ["sombra"],
        "description": "Um homem magro de capa negra, com um chicote de couro trançado e uma lua cortada no peito.",
        "abilities": [
            {"id": "assobio_ao_lobo", "name": "Assobio ao Lobo", "hp_below": 0.6, "once": True,
             "summon": ["lobo_faminto"], "text": "Varek leva os dedos à boca e assobia — um lobo responde!"},
            {"id": "flecha_sombria", "name": "Flecha Sombria", "chance": 0.3, "cooldown": 2, "damage": 1.3,
             "element": "sombra"},
            {"id": "rito_lua_cortada", "name": "Rito da Lua Cortada", "chance": 0.35, "cooldown": 4, "charge": 2,
             "locks": ["sagrado", "fisico", "fisico"],
             "announce": "Varek ergue um amuleto em forma de lua partida e começa a entoar uma prece rouca...",
             "effects": [{"type": "heal_self", "value": 0.2},
                         {"type": "buff_self", "id": "furia_lunar", "name": "Fúria Lunar", "stat": "damage_dealt",
                          "value": 0.2, "turns": 3}]},
        ],
        "loot": [{"one_of": ["machadinha_domador", "capuz_domador", "cinto_couro_trancado"], "chance": 100},
                 {"item": "coleira_lua_cortada", "chance": 100}],
        "copper": [80, 160],
    },
    "presa_de_gelo": {
        "name": "Presa-de-Gelo, o Alfa Branco", "family": "fera", "levels": [7, 7],
        "hp": 1.9, "damage": 1.0, "armor": 1.3, "attack": "morde", "elite": True, "boss": True,
        "weaknesses": ["fogo"], "resistances": ["gelo"],
        "description": ("O Alfa Branco da Floresta Sussurrante: um lobo do tamanho de um cavalo, de olhos azuis "
                        "como gelo. Os lobos o seguem — e ele segue alguém."),
        "abilities": [
            {"id": "chamado_alcateia", "name": "Chamado da Alcateia", "hp_below": 0.5, "once": True,
             "summon": ["lobo_cinzento"], "text": "Presa-de-Gelo uiva, e um lobo cinzento responde das sombras!"},
            {"id": "mordida_gelida", "name": "Mordida Gélida", "chance": 0.3, "cooldown": 2, "damage": 1.3,
             "element": "gelo",
             "effects": [{"type": "debuff", "id": "lento", "name": "Lentidão", "stat": "damage_dealt",
                          "value": -0.25, "turns": 2}]},
            {"id": "uivo_glacial", "name": "Uivo Glacial", "chance": 0.35, "cooldown": 4, "charge": 2,
             "locks": ["fogo", "fisico", "fisico"], "damage": 2.4, "element": "gelo",
             "announce": "Presa-de-Gelo ergue a cabeça e enche o peito de ar gelado...",
             "effects": [{"type": "freeze", "turns": 1, "name": "Congelamento"}]},
        ],
        "loot": [{"item": "pele_presa_de_gelo", "chance": 100},
                 {"one_of": ["presa_gelida", "manto_alfa_branco", "anel_uivo_gelido"], "chance": 100},
                 {"item": "fragmento_gelo_eterno", "chance": 100, "qty": [1, 2]}],
        "copper": [250, 500],
    },
}
