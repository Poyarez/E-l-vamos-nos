"""Receitas das perícias de produção (lógica em ``rpg.crafting``).

Como no OSRS, toda receita fica disponível ao atingir o nível — não é preciso aprender
com ninguém. Campos:

* ``skill``, ``level`` e ``xp`` (experiência por item, em unidades do OSRS);
* ``inputs`` — ``[[item, quantidade], ...]`` consumidos a cada item feito;
* ``output`` — ``[item, quantidade]``;
* ``station`` — onde é feita (ver ``STATIONS``; sem estação, faz-se em qualquer lugar)
  e ``tool`` — ferramenta exigida na mochila;
* ``minutes`` — tempo de jogo por item;
* ``burn`` — ``[chance, nível]``: chance de queimar no nível mínimo, caindo até zero no
  nível indicado (culinária). ``fail`` funciona igual, mas o material se perde (o ferro
  impuro da fundição).
"""

#: Estações de trabalho (com o comando que as usa). Os locais dos mapas as oferecem em
#: ``stations``: ``{"id", "name", "if", "closed", "burn", "fuel"}`` — ``burn`` multiplica a
#: chance de queimar (a cozinha da estalagem queima menos) e ``fuel`` é gasto a cada fornada.
STATIONS = {
    "fornalha": {"name": "Fornalha", "verb": "forjar"},
    "bigorna": {"name": "Bigorna", "verb": "forjar"},
    "fogo": {"name": "Fogo de cozinha", "verb": "cozinhar"},
    "roca": {"name": "Roca de fiar", "verb": "costurar"},
    "caldeirao": {"name": "Caldeirão", "verb": "preparar"},
}

#: Item que recebe a comida que queima.
BURNT_ITEM = "comida_queimada"

RECIPES = {
    # ------------------------------------------------------------------ metalurgia: fornalha
    "barra_bronze": {
        "skill": "metalurgia", "level": 1, "xp": 6.2, "station": "fornalha", "minutes": 2,
        "inputs": [["minerio_cobre", 1], ["minerio_estanho", 1]], "output": ["barra_bronze", 1],
    },
    "barra_ferro": {
        "skill": "metalurgia", "level": 15, "xp": 12.5, "station": "fornalha", "minutes": 3,
        "inputs": [["minerio_ferro", 1]], "output": ["barra_ferro", 1], "fail": [0.5, 45],
    },
    "barra_prata": {
        "skill": "metalurgia", "level": 20, "xp": 13.7, "station": "fornalha", "minutes": 3,
        "inputs": [["minerio_prata", 1]], "output": ["barra_prata", 1],
    },
    # ------------------------------------------------------------------ metalurgia: bigorna (bronze)
    "adaga_bronze": {
        "skill": "metalurgia", "level": 1, "xp": 12.5, "station": "bigorna", "tool": "martelo", "minutes": 4,
        "inputs": [["barra_bronze", 1]], "output": ["adaga_bronze", 1],
    },
    "machadinha_bronze": {
        "skill": "metalurgia", "level": 2, "xp": 12.5, "station": "bigorna", "tool": "martelo", "minutes": 4,
        "inputs": [["barra_bronze", 1]], "output": ["machadinha_bronze", 1],
    },
    "maca_bronze": {
        "skill": "metalurgia", "level": 3, "xp": 12.5, "station": "bigorna", "tool": "martelo", "minutes": 4,
        "inputs": [["barra_bronze", 1]], "output": ["maca_bronze", 1],
    },
    "elmo_bronze": {
        "skill": "metalurgia", "level": 4, "xp": 12.5, "station": "bigorna", "tool": "martelo", "minutes": 4,
        "inputs": [["barra_bronze", 1]], "output": ["elmo_bronze", 1],
    },
    "espada_bronze": {
        "skill": "metalurgia", "level": 5, "xp": 12.5, "station": "bigorna", "tool": "martelo", "minutes": 4,
        "inputs": [["barra_bronze", 1]], "output": ["espada_bronze", 1],
    },
    "picareta_bronze": {
        "skill": "metalurgia", "level": 6, "xp": 25, "station": "bigorna", "tool": "martelo", "minutes": 6,
        "inputs": [["barra_bronze", 2]], "output": ["picareta_bronze", 1],
    },
    "botas_bronze": {
        "skill": "metalurgia", "level": 7, "xp": 12.5, "station": "bigorna", "tool": "martelo", "minutes": 4,
        "inputs": [["barra_bronze", 1]], "output": ["botas_bronze", 1],
    },
    "escudo_bronze": {
        "skill": "metalurgia", "level": 9, "xp": 25, "station": "bigorna", "tool": "martelo", "minutes": 6,
        "inputs": [["barra_bronze", 2]], "output": ["escudo_bronze", 1],
    },
    "cota_bronze": {
        "skill": "metalurgia", "level": 12, "xp": 37.5, "station": "bigorna", "tool": "martelo", "minutes": 10,
        "inputs": [["barra_bronze", 3]], "output": ["cota_bronze", 1],
    },
    "perneiras_bronze": {
        "skill": "metalurgia", "level": 16, "xp": 37.5, "station": "bigorna", "tool": "martelo", "minutes": 8,
        "inputs": [["barra_bronze", 3]], "output": ["perneiras_bronze", 1],
    },
    # ------------------------------------------------------------------ metalurgia: bigorna (ferro)
    "adaga_ferro": {
        "skill": "metalurgia", "level": 15, "xp": 25, "station": "bigorna", "tool": "martelo", "minutes": 4,
        "inputs": [["barra_ferro", 1]], "output": ["adaga_ferro", 1],
    },
    "maca_ferro": {
        "skill": "metalurgia", "level": 17, "xp": 25, "station": "bigorna", "tool": "martelo", "minutes": 4,
        "inputs": [["barra_ferro", 1]], "output": ["maca_ferro", 1],
    },
    "machado_ferro": {
        "skill": "metalurgia", "level": 17, "xp": 25, "station": "bigorna", "tool": "martelo", "minutes": 4,
        "inputs": [["barra_ferro", 1]], "output": ["machado_ferro", 1],
    },
    "elmo_ferro": {
        "skill": "metalurgia", "level": 18, "xp": 25, "station": "bigorna", "tool": "martelo", "minutes": 4,
        "inputs": [["barra_ferro", 1]], "output": ["elmo_ferro", 1],
    },
    "espada_ferro": {
        "skill": "metalurgia", "level": 19, "xp": 25, "station": "bigorna", "tool": "martelo", "minutes": 4,
        "inputs": [["barra_ferro", 1]], "output": ["espada_ferro", 1],
    },
    "picareta_ferro": {
        "skill": "metalurgia", "level": 20, "xp": 50, "station": "bigorna", "tool": "martelo", "minutes": 6,
        "inputs": [["barra_ferro", 2]], "output": ["picareta_ferro", 1],
    },
    "botas_ferro": {
        "skill": "metalurgia", "level": 21, "xp": 25, "station": "bigorna", "tool": "martelo", "minutes": 4,
        "inputs": [["barra_ferro", 1]], "output": ["botas_ferro", 1],
    },
    "escudo_ferro": {
        "skill": "metalurgia", "level": 24, "xp": 50, "station": "bigorna", "tool": "martelo", "minutes": 6,
        "inputs": [["barra_ferro", 2]], "output": ["escudo_ferro", 1],
    },
    "cota_ferro": {
        "skill": "metalurgia", "level": 27, "xp": 75, "station": "bigorna", "tool": "martelo", "minutes": 10,
        "inputs": [["barra_ferro", 3]], "output": ["cota_ferro", 1],
    },
    "perneiras_ferro": {
        "skill": "metalurgia", "level": 31, "xp": 75, "station": "bigorna", "tool": "martelo", "minutes": 8,
        "inputs": [["barra_ferro", 3]], "output": ["perneiras_ferro", 1],
    },
    # ------------------------------------------------------------------ metalurgia: joias de prata
    "anel_prata": {
        "skill": "metalurgia", "level": 20, "xp": 25, "station": "bigorna", "tool": "martelo", "minutes": 6,
        "inputs": [["barra_prata", 1]], "output": ["anel_prata", 1],
    },
    "anel_granada": {
        "skill": "metalurgia", "level": 27, "xp": 45, "station": "bigorna", "tool": "martelo", "minutes": 8,
        "inputs": [["barra_prata", 1], ["granada_bruta", 1]], "output": ["anel_granada", 1],
    },
    "amuleto_eco": {
        "skill": "metalurgia", "level": 45, "xp": 100, "station": "bigorna", "tool": "martelo", "minutes": 12,
        "inputs": [["barra_prata", 1], ["cristal_eco", 1]], "output": ["amuleto_eco", 1],
    },
    # ------------------------------------------------------------------ culinária
    "pao_de_viagem": {
        "skill": "culinaria", "level": 1, "xp": 25, "station": "fogo", "minutes": 3, "burn": [0.4, 15],
        "inputs": [["farinha", 1]], "output": ["pao_de_viagem", 1],
    },
    "camarao_assado": {
        "skill": "culinaria", "level": 1, "xp": 30, "station": "fogo", "minutes": 2, "burn": [0.5, 18],
        "inputs": [["camarao_cru", 1]], "output": ["camarao_assado", 1],
    },
    "sardinha_assada": {
        "skill": "culinaria", "level": 3, "xp": 40, "station": "fogo", "minutes": 2, "burn": [0.5, 22],
        "inputs": [["sardinha_crua", 1]], "output": ["sardinha_assada", 1],
    },
    "bisteca_javali": {
        "skill": "culinaria", "level": 5, "xp": 45, "station": "fogo", "minutes": 3, "burn": [0.5, 25],
        "inputs": [["carne_javali", 1]], "output": ["bisteca_javali", 1],
    },
    "truta_assada": {
        "skill": "culinaria", "level": 12, "xp": 70, "station": "fogo", "minutes": 3, "burn": [0.55, 35],
        "inputs": [["truta_crua", 1]], "output": ["truta_assada", 1],
    },
    "espetinho_lobo": {
        "skill": "culinaria", "level": 15, "xp": 75, "station": "fogo", "minutes": 4, "burn": [0.5, 35],
        "inputs": [["carne_lobo", 1], ["especiarias", 1]], "output": ["espetinho_lobo", 1],
    },
    "ensopado_javali": {
        "skill": "culinaria", "level": 18, "xp": 90, "station": "fogo", "minutes": 6, "burn": [0.5, 40],
        "inputs": [["carne_javali", 2], ["cogumelo_lume", 1]], "output": ["ensopado_javali", 1],
    },
    "torta_truta": {
        "skill": "culinaria", "level": 22, "xp": 100, "station": "fogo", "minutes": 6, "burn": [0.5, 45],
        "inputs": [["truta_crua", 1], ["farinha", 2]], "output": ["torta_truta", 1],
    },
    "salmao_assado": {
        "skill": "culinaria", "level": 25, "xp": 90, "station": "fogo", "minutes": 3, "burn": [0.55, 50],
        "inputs": [["salmao_cru", 1]], "output": ["salmao_assado", 1],
    },
    "peixe_cego_assado": {
        "skill": "culinaria", "level": 32, "xp": 120, "station": "fogo", "minutes": 4, "burn": [0.6, 60],
        "inputs": [["peixe_cego_cru", 1]], "output": ["peixe_cego_assado", 1],
    },
    # ------------------------------------------------------------------ alfaiataria: roca
    "fio_linho": {
        "skill": "alfaiataria", "level": 1, "xp": 10, "station": "roca", "minutes": 1,
        "inputs": [["linho", 1]], "output": ["fio_linho", 1],
    },
    "novelo_la": {
        "skill": "alfaiataria", "level": 8, "xp": 20, "station": "roca", "minutes": 2,
        "inputs": [["la_crua", 1]], "output": ["novelo_la", 1],
    },
    "fio_seda": {
        "skill": "alfaiataria", "level": 20, "xp": 35, "station": "roca", "minutes": 2,
        "inputs": [["teia_pegajosa", 2]], "output": ["fio_seda", 1],
    },
    # ------------------------------------------------------------------ alfaiataria: costura (agulha)
    "luvas_linho": {
        "skill": "alfaiataria", "level": 2, "xp": 25, "tool": "agulha", "minutes": 8,
        "inputs": [["fio_linho", 2]], "output": ["luvas_linho", 1],
    },
    "tunica_linho": {
        "skill": "alfaiataria", "level": 4, "xp": 40, "tool": "agulha", "minutes": 12,
        "inputs": [["fio_linho", 3]], "output": ["tunica_linho", 1],
    },
    "bolsa_linho": {
        "skill": "alfaiataria", "level": 6, "xp": 55, "tool": "agulha", "minutes": 15,
        "inputs": [["fio_linho", 4]], "output": ["bolsa_linho", 1],
    },
    "colar_presas": {
        "skill": "alfaiataria", "level": 9, "xp": 50, "tool": "agulha", "minutes": 8,
        "inputs": [["presa_lobo", 3], ["fio_linho", 1]], "output": ["colar_presas", 1],
    },
    "capuz_la": {
        "skill": "alfaiataria", "level": 10, "xp": 60, "tool": "agulha", "minutes": 10,
        "inputs": [["novelo_la", 2]], "output": ["capuz_la", 1],
    },
    "gibao_couro_javali": {
        "skill": "alfaiataria", "level": 12, "xp": 80, "tool": "agulha", "minutes": 15,
        "inputs": [["couro_javali", 3], ["fio_linho", 2]], "output": ["gibao_couro_javali", 1],
    },
    "calcas_la": {
        "skill": "alfaiataria", "level": 14, "xp": 75, "tool": "agulha", "minutes": 12,
        "inputs": [["novelo_la", 3]], "output": ["calcas_la", 1],
    },
    "botas_couro_javali": {
        "skill": "alfaiataria", "level": 16, "xp": 85, "tool": "agulha", "minutes": 12,
        "inputs": [["couro_javali", 2], ["fio_linho", 1]], "output": ["botas_couro_javali", 1],
    },
    "manto_la": {
        "skill": "alfaiataria", "level": 17, "xp": 80, "tool": "agulha", "minutes": 12,
        "inputs": [["novelo_la", 3]], "output": ["manto_la", 1],
    },
    "capuz_couro_lobo": {
        "skill": "alfaiataria", "level": 19, "xp": 100, "tool": "agulha", "minutes": 12,
        "inputs": [["pele_lobo", 3], ["fio_linho", 1]], "output": ["capuz_couro_lobo", 1],
    },
    "bolsa_la": {
        "skill": "alfaiataria", "level": 21, "xp": 110, "tool": "agulha", "minutes": 15,
        "inputs": [["novelo_la", 4], ["couro_javali", 1]], "output": ["bolsa_la", 1],
    },
    "manto_pele_lobo": {
        "skill": "alfaiataria", "level": 23, "xp": 120, "tool": "agulha", "minutes": 15,
        "inputs": [["pele_lobo", 4], ["novelo_la", 1]], "output": ["manto_pele_lobo", 1],
    },
    "luvas_seda_aranha": {
        "skill": "alfaiataria", "level": 25, "xp": 120, "tool": "agulha", "minutes": 12,
        "inputs": [["fio_seda", 2]], "output": ["luvas_seda_aranha", 1],
    },
    "vestes_seda": {
        "skill": "alfaiataria", "level": 30, "xp": 160, "tool": "agulha", "minutes": 20,
        "inputs": [["fio_seda", 4]], "output": ["vestes_seda", 1],
    },
    "bolsa_seda": {
        "skill": "alfaiataria", "level": 35, "xp": 190, "tool": "agulha", "minutes": 20,
        "inputs": [["fio_seda", 4], ["novelo_la", 2]], "output": ["bolsa_seda", 1],
    },
    # ------------------------------------------------------------------ alquimia
    "pocao_cura_menor": {
        "skill": "alquimia", "level": 1, "xp": 25, "tool": "almofariz", "minutes": 4,
        "inputs": [["folha_charco", 2], ["frasco_vazio", 1]], "output": ["pocao_cura_menor", 1],
    },
    "pocao_mana_menor": {
        "skill": "alquimia", "level": 10, "xp": 35, "tool": "almofariz", "minutes": 4,
        "inputs": [["cogumelo_lume", 1], ["folha_charco", 1], ["frasco_vazio", 1]],
        "output": ["pocao_mana_menor", 1],
    },
    "elixir_javali": {
        "skill": "alquimia", "level": 12, "xp": 40, "station": "caldeirao", "tool": "almofariz", "minutes": 5,
        "inputs": [["presa_javali", 1], ["folha_charco", 1], ["frasco_vazio", 1]], "output": ["elixir_javali", 1],
    },
    "oleo_inflamavel": {
        "skill": "alquimia", "level": 15, "xp": 45, "station": "caldeirao", "tool": "almofariz", "minutes": 5,
        "inputs": [["flor_breu", 2], ["frasco_vazio", 1]], "output": ["oleo_inflamavel", 1],
    },
    "veneno_aranha": {
        "skill": "alquimia", "level": 18, "xp": 50, "station": "caldeirao", "tool": "almofariz", "minutes": 5,
        "inputs": [["glandula_veneno", 1], ["folha_charco", 1], ["frasco_vazio", 1]], "output": ["veneno_aranha", 1],
    },
    "elixir_morcego": {
        "skill": "alquimia", "level": 20, "xp": 55, "station": "caldeirao", "tool": "almofariz", "minutes": 5,
        "inputs": [["asa_morcego", 2], ["cogumelo_lume", 1], ["frasco_vazio", 1]], "output": ["elixir_morcego", 1],
    },
    "frasco_gelo": {
        "skill": "alquimia", "level": 22, "xp": 60, "station": "caldeirao", "tool": "almofariz", "minutes": 5,
        "inputs": [["fragmento_gelo_eterno", 1], ["orquidea_termal", 1], ["frasco_vazio", 1]],
        "output": ["frasco_gelo", 1],
    },
    "pocao_cura": {
        "skill": "alquimia", "level": 25, "xp": 70, "tool": "almofariz", "minutes": 5,
        "inputs": [["musgo_prata", 2], ["folha_charco", 1], ["frasco_vazio", 1]], "output": ["pocao_cura", 1],
    },
    "elixir_lobo": {
        "skill": "alquimia", "level": 27, "xp": 75, "station": "caldeirao", "tool": "almofariz", "minutes": 5,
        "inputs": [["presa_lobo", 2], ["orquidea_termal", 1], ["frasco_vazio", 1]], "output": ["elixir_lobo", 1],
    },
    "frasco_luz": {
        "skill": "alquimia", "level": 31, "xp": 90, "station": "caldeirao", "tool": "almofariz", "minutes": 6,
        "inputs": [["lirio_lua", 1], ["ectoplasma", 1], ["frasco_vazio", 1]], "output": ["frasco_luz", 1],
    },
    "elixir_sussurrante": {
        "skill": "alquimia", "level": 33, "xp": 95, "station": "caldeirao", "tool": "almofariz", "minutes": 6,
        "inputs": [["essencia_sussurrante", 1], ["lirio_lua", 1], ["frasco_vazio", 1]],
        "output": ["elixir_sussurrante", 1],
    },
    "pocao_mana": {
        "skill": "alquimia", "level": 36, "xp": 100, "tool": "almofariz", "minutes": 5,
        "inputs": [["cogumelo_lume", 2], ["orquidea_termal", 1], ["frasco_vazio", 1]], "output": ["pocao_mana", 1],
    },
    "frasco_eco": {
        "skill": "alquimia", "level": 42, "xp": 125, "station": "caldeirao", "tool": "almofariz", "minutes": 8,
        "inputs": [["cristal_eco", 1], ["lirio_lua", 1], ["frasco_vazio", 1]], "output": ["frasco_eco", 1],
    },
}
