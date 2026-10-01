"""Missões e tarefas do quadro de avisos (lógica em ``rpg.quests``).

Missão:
  ``name``, ``category`` (``principal`` ou ``secundaria``), ``giver`` (quem pede — só para
  exibir), ``summary`` (o resumo no diário de missões), ``start`` (condições que começam a
  missão sozinha; sem ``start``, ela começa pelo efeito de diálogo ``start_quest``),
  ``stages`` e ``rewards``.

Etapa: ``text`` (o que fazer agora) e ``goal`` — um bloco de condições de
``rpg.conditions`` mais, opcionalmente, ``kill: {"monsters": [...], "count": n}`` (abates
feitos depois que a etapa começou). ``take_item`` recolhe itens quando a etapa termina.
Entregas usam ``any`` com a flag da entrega como plano B: se o herói entregar os itens na
mesma conversa em que recebeu a missão, a etapa não fica presa esperando itens que já se
foram.

Recompensa: ``xp``, ``copper``, ``items``, ``class_items`` (por classe), ``set_flag`` e
``journal``; ``ending`` é o texto exibido ao concluir.

Tarefa do quadro (``BOUNTIES``): ``name``, ``description``, ``goal`` (``kill`` e/ou
``deliver``: itens entregues ao quadro), ``reward``, ``min_level``/``max_level`` e ``if``.
"""

QUESTS = {
    # ================================================================== principal
    "tres_luas": {
        "name": "As Três Luas",
        "category": "principal",
        "giver": "Anciã Ysolde",
        "summary": ("Os Vigias da Lua usavam três luas — crescente, cheia e minguante — para cantar o sono do "
                    "Primordial, o gigante que dorme sob o vale. O culto da Lua Cortada quer acordá-lo. Reúna as "
                    "luas antes deles."),
        "start": {"flag": "ysolde_tres_luas"},
        "stages": [
            {"text": "Encontre a primeira lua: \"onde a água cai em véu de prata, a lua dorme em sua casa\".",
             "goal": {"flag": "bau_gruta_aberto"}},
            {"text": "Os Vigias estão enterrados no Cemitério da Colina. Visite o túmulo de Kael — à noite.",
             "goal": {"flag": "kael_conversou"}},
            {"text": ("Aprenda a canção das três notas nas Pedras que Cantam, na Ilhota da Garça, à noite. Será "
                      "preciso um barco: talvez o de Anselmo, no píer."),
             "goal": {"flag": "cancao_tres_notas"}},
            {"text": "Cante para o Carvalho Ancião, na mata antiga, numa noite, e receba a lua cheia.",
             "goal": {"owns": "lua_cheia"}},
            {"text": ("Morwen, a Senhora da Lua Cortada, tem a lua minguante. Encontre o santuário sob o Círculo de "
                      "Pedras Rúnicas e derrote-a."),
             "goal": {"flag": "morwen_derrotada"}},
            {"text": "A lua minguante foi partida ao meio. Leve as metades e uma barra de prata a Brom, o ferreiro.",
             "goal": {"owns": "lua_minguante"}},
            {"text": "Leve as três luas à Porta Selada, na gruta atrás da cachoeira.",
             "goal": {"flag": "porta_aberta"}},
            {"text": "Atrás da porta, o Vigia sonha um pesadelo. Desperte-o.",
             "goal": {"flag": "vigia_desperto"}},
            {"text": "Conte tudo à Anciã Ysolde.",
             "goal": {"flag": "ysolde_final"}},
        ],
        "rewards": {
            "xp": 5000, "copper": 2500, "items": [["manto_vigias", 1]], "set_flag": ["vale_salvo"],
            "journal": {
                "id": "fim_tres_luas", "title": "O sono do Primordial",
                "text": ("Com as três luas e a canção, o Vigia despertou em paz e cantou o Primordial de volta ao "
                         "sono. O culto da Lua Cortada caiu, os tremores pararam e o Vale de Primórdia respira de "
                         "novo. Mas o Passo do Norte segue fechado, a ponte do Rio Largo caiu — e há outros "
                         "gigantes adormecidos pelo mundo."),
            },
        },
        "ending": ("Naquela noite, a vila inteira se reúne na praça. Lírio canta, Marta serve ensopado de graça, "
                   "Tobias dança com quem deixar, e até a Capitã Renna sorri. Lá embaixo, muito fundo, um gigante "
                   "dorme em paz. E, no cemitério da colina, há flores frescas no túmulo de Kael."),
    },
    # ================================================================== secundárias
    "aprendiz": {
        "name": "O Aprendiz Desaparecido",
        "category": "secundaria",
        "giver": "Brom Martelo-Rubro",
        "summary": ("Davi, aprendiz de Brom, sumiu na Mina de Ferro-Velho na grande tremura. Brom ainda espera "
                    "notícias."),
        "start": {"any": [{"journal": "pista_davi"}, {"flag": "davi_resgatado"}]},
        "stages": [
            {"text": "Entre na Mina de Ferro-Velho, nas Colinas de Cobre (nível 8 ou mais).",
             "goal": {"discovered": "boca_mina"}},
            {"text": "Encontre Davi nas profundezas da mina.",
             "goal": {"flag": "davi_resgatado"}},
            {"text": "Volte à forja e conte a Brom.",
             "goal": {"flag": "brom_davi_voltou"}},
        ],
        "rewards": {
            "xp": 2500, "copper": 600, "set_flag": ["mina_livre"],
            "class_items": {"guerreiro": [["escudo_davi", 1]], "mago": [["cajado_aco", 1]],
                            "sacerdote": [["maca_davi", 1]], "ladino": [["adaga_davi", 1]]},
        },
        "ending": "Davi forjou uma peça especial para você. Com a mina livre, a forja de Brom volta a vender ferro e aço.",
    },
    "corvo": {
        "name": "As Asas do Corvo",
        "category": "secundaria",
        "giver": "Capitã Renna",
        "summary": ("Uma carta no cofre do capataz revela que o culto paga o Bando do Corvo para manter o vale "
                    "isolado. Sem as flechas da mina, o Bando está vulnerável."),
        "start": {"any": [{"item": "carta_capataz"}, {"flag": "renna_carta"}]},
        "stages": [
            {"text": "Mostre a carta do capataz à Capitã Renna, no Portão Norte.",
             "goal": {"flag": "renna_carta"}},
            {"text": ("O Portão Sul está aberto. Encontre o acampamento de Ulric Corvo-Negro na Rota dos Mercadores "
                      "e acabe com o Bando."),
             "goal": {"flag": "ulric_derrotado"}},
            {"text": "Volte à Capitã Renna com a notícia.",
             "goal": {"flag": "rota_liberada"}},
        ],
        "rewards": {"xp": 3000, "copper": 1500, "items": [["anel_guarda", 1]]},
        "ending": "A Rota dos Mercadores está livre. As caravanas vão voltar — e Zahir vai montar banca no mercado.",
    },
    "sobrinho": {
        "name": "O Olho que se Abre",
        "category": "secundaria",
        "giver": "Capitã Renna",
        "summary": ("Tomé, o sobrinho da Capitã Renna, foi às ruínas ver \"o olho se abrir\" e não voltou."),
        "stages": [
            {"text": "Procure Tomé na Torre Tombada, nas Ruínas de Vel'Tharas — à noite.",
             "goal": {"flag": "tome_cultistas"}},
            {"text": "Fale com Tomé.",
             "goal": {"flag": "tome_salvo"}},
            {"text": "Conte à Capitã Renna que o sobrinho está a salvo.",
             "goal": {"flag": "renna_tome"}},
        ],
        "rewards": {"xp": 1800, "copper": 400, "items": [["capa_guarda", 1]]},
    },
    "barco": {
        "name": "Um Barco para a Ilhota",
        "category": "secundaria",
        "giver": "Velho Anselmo",
        "summary": "O barco de Anselmo está furado. Com ele consertado, dá para chegar à Ilhota da Garça.",
        "stages": [
            {"text": ("Junte 10 pregos de bronze (forja), 2 potes de piche (alquimia) e 1 remendo de lona "
                      "(alfaiataria) — ou compre com Brom, Brígida e Graça."),
             "goal": {"any": [{"item": [["pregos_bronze", 10], ["piche", 2], ["remendo_lona", 1]]},
                              {"flag": "barco_consertado"}]}},
            {"text": "Leve os materiais a Anselmo, no píer do Lago Espelhado.",
             "goal": {"flag": "barco_consertado"}},
        ],
        "rewards": {"xp": 1200, "items": [["isca_minhoca", 20]]},
        "ending": "O barco de Anselmo está pronto. Use 'navegar' no píer para ir à Ilhota da Garça.",
    },
    "rei_do_lago": {
        "name": "O Rei do Lago",
        "category": "secundaria",
        "giver": "Velho Anselmo",
        "summary": ("Anselmo jura que o Rei do Lago existe: um peixe do tamanho de um bezerro, com uma barbatana "
                    "em forma de coroa. Ele mora no Poço do Rei, na ilhota."),
        "stages": [
            {"text": ("Fisgue um Rei do Lago no Poço do Rei, na Ilhota da Garça. Só um pescador de mão firme "
                      "(Pesca 35) consegue segurá-lo."),
             "goal": {"any": [{"item": "rei_do_lago"}, {"flag": "anselmo_rei"}]}},
            {"text": "Mostre o peixe a Anselmo.",
             "goal": {"flag": "anselmo_rei"}},
        ],
        "rewards": {"xp": 2500, "items": [["vara_anselmo", 1]]},
    },
    "ratos": {
        "name": "Ratos no Celeiro",
        "category": "secundaria",
        "giver": "Tobias",
        "summary": "Ratos do tamanho de cães saem dos buracos dos campos à noite e atacam o celeiro de Tobias.",
        "stages": [
            {"text": "Derrote 6 ratos gigantes nos campos ao redor da vila (eles saem à noite).",
             "goal": {"kill": {"monsters": ["rato_gigante"], "count": 6}}},
            {"text": "Volte ao moinho de Tobias.",
             "goal": {"flag": "tobias_ratos"}},
        ],
        "rewards": {"xp": 450, "copper": 150, "items": [["pao_de_viagem", 5]]},
    },
    "peles": {
        "name": "Casacos para o Inverno",
        "category": "secundaria",
        "giver": "Dona Graça",
        "summary": "Os netos de Dona Graça precisam de casacos para o inverno — de pele de lobo.",
        "stages": [
            {"text": "Junte 5 peles de lobo.",
             "goal": {"any": [{"item": ["pele_lobo", 5]}, {"flag": "graca_peles"}]}},
            {"text": "Entregue as peles a Dona Graça, no mercado.",
             "goal": {"flag": "graca_peles"}},
        ],
        "rewards": {"xp": 600, "copper": 250, "items": [["bolsa_la", 1]]},
    },
    "remedios": {
        "name": "Remédios para a Capela",
        "category": "secundaria",
        "giver": "Irmã Celeste",
        "summary": "A Capela da Aurora vive cheia de feridos desde as tremuras, e as poções nunca bastam.",
        "stages": [
            {"text": "Consiga 3 poções de cura menor (Mãe Brígida ensina a prepará-las; Dona Graça vende).",
             "goal": {"any": [{"item": ["pocao_cura_menor", 3]}, {"flag": "celeste_remedios"}]}},
            {"text": "Entregue as poções à Irmã Celeste, na capela.",
             "goal": {"flag": "celeste_remedios"}},
        ],
        "rewards": {"xp": 600, "copper": 200, "items": [["simbolo_aurora", 1]]},
    },
}

BOUNTIES = {
    # ------------------------------------------------------------------ caçadas
    "caca_ratos": {
        "name": "Ratos nos campos",
        "description": "\"Os ratos voltaram! Pago por cada cinco. — Tobias\"",
        "goal": {"kill": {"monsters": ["rato_gigante"], "count": 5}},
        "reward": {"xp": 150, "copper": 60}, "max_level": 6,
    },
    "caca_javalis": {
        "name": "Javalis no trigal",
        "description": "\"Javalis pisotearam meio trigal. Quem der um jeito neles leva uma recompensa. — Família Moreira\"",
        "goal": {"kill": {"monsters": ["javali_jovem", "javali_espinhento"], "count": 4}},
        "reward": {"xp": 250, "copper": 100}, "min_level": 2, "max_level": 8,
    },
    "caca_lobos": {
        "name": "Lobos na orla",
        "description": "\"Lobos rondam a orla da floresta. A guarda paga por cada alcateia dispersada. — R. V.\"",
        "goal": {"kill": {"monsters": ["lobo_faminto", "lobo_cinzento", "lobo_gelido"], "count": 5}},
        "reward": {"xp": 300, "copper": 120}, "min_level": 3, "max_level": 9,
    },
    "caca_aranhas": {
        "name": "Teias na trilha",
        "description": "\"Aranhas do tamanho de escudos na trilha dos caçadores. Recompensa pelas cabeças.\"",
        "goal": {"kill": {"monsters": ["aranha_da_mata"], "count": 4}},
        "reward": {"xp": 300, "copper": 120, "items": [["pocao_cura_menor", 2]]}, "min_level": 3, "max_level": 9,
    },
    "caca_espiritos": {
        "name": "Vozes na floresta",
        "description": "\"Os sussurros da floresta estão dizendo nomes. Que alguém os cale. — Irmã Celeste\"",
        "goal": {"kill": {"monsters": ["espirito_sussurrante"], "count": 3}},
        "reward": {"xp": 400, "copper": 160}, "min_level": 5, "max_level": 11,
    },
    "caca_kobolds": {
        "name": "Cântico na mina",
        "description": "\"Os kobolds da mina atacam quem chega perto. A guarda paga por seis deles. — R. V.\"",
        "goal": {"kill": {"monsters": ["kobold_escavador", "kobold_vela", "kobold_geomante"], "count": 6}},
        "reward": {"xp": 600, "copper": 250}, "min_level": 8, "if": {"not_flag": "gorran_derrotado"},
    },
    "caca_toupeiras": {
        "name": "Toupeiras-de-ferro",
        "description": "\"Toupeiras comem o minério antes de nós! Quatro couraças, um bom pagamento. — Brom\"",
        "goal": {"kill": {"monsters": ["toupeira_ferro"], "count": 4}},
        "reward": {"xp": 550, "copper": 220}, "min_level": 8,
    },
    "caca_sentinelas": {
        "name": "Pedras que andam",
        "description": "\"Estátuas andam pelas ruínas de dia. Alguém precisa parar essas pedras. — Ysolde\"",
        "goal": {"kill": {"monsters": ["sentinela_ruinas"], "count": 3}},
        "reward": {"xp": 550, "copper": 200}, "min_level": 8,
    },
    "caca_cultistas": {
        "name": "Capas negras",
        "description": "\"Capas negras nas ruínas, à noite. A guarda paga por cada um que não voltar. — R. V.\"",
        "goal": {"kill": {"monsters": ["acolito_lua", "guarda_capa_negra", "cao_sombrio"], "count": 4}},
        "reward": {"xp": 700, "copper": 300}, "min_level": 9, "if": {"not_flag": "morwen_derrotada"},
    },
    "caca_bandidos": {
        "name": "Penas negras",
        "description": "\"Bandidos do Corvo na Rota dos Mercadores. Recompensa por cinco deles. — R. V.\"",
        "goal": {"kill": {"monsters": ["batedor_corvo", "arqueiro_corvo", "brutamontes_corvo"], "count": 5}},
        "reward": {"xp": 700, "copper": 300}, "min_level": 9,
        "if": {"flag": "rota_aberta", "not_flag": "ulric_derrotado"},
    },
    "caca_ecos": {
        "name": "Ecos sem descanso",
        "description": "\"Os ecos das ruínas não descansam. Que a Aurora os guie — e que alguém os ajude. — Celeste\"",
        "goal": {"kill": {"monsters": ["eco_veltharas"], "count": 3}},
        "reward": {"xp": 650, "copper": 260, "items": [["pocao_cura", 1]]}, "min_level": 10,
    },
    # ------------------------------------------------------------------ encomendas (perícias)
    "entrega_bronze": {
        "name": "Barras de bronze",
        "description": "\"Preciso de cinco barras de bronze para ferraduras. Pago bem. — Brom\"",
        "goal": {"deliver": [["barra_bronze", 5]]},
        "reward": {"xp": 200, "copper": 150}, "max_level": 14,
    },
    "entrega_ferro": {
        "name": "Barras de ferro",
        "description": "\"Ferro para as dobradiças do portão: quatro barras. — Guarda do Vale\"",
        "goal": {"deliver": [["barra_ferro", 4]]},
        "reward": {"xp": 300, "copper": 250}, "min_level": 4,
    },
    "entrega_aco": {
        "name": "Aço para a guarda",
        "description": "\"Com a mina livre, a guarda quer lanças novas: quatro barras de aço. — R. V.\"",
        "goal": {"deliver": [["barra_aco", 4]]},
        "reward": {"xp": 450, "copper": 400}, "min_level": 8, "if": {"flag": "mina_livre"},
    },
    "entrega_trutas": {
        "name": "Trutas para a estalagem",
        "description": "\"Cinco trutas assadas para o jantar dos viajantes. — Marta\"",
        "goal": {"deliver": [["truta_assada", 5]]},
        "reward": {"xp": 250, "copper": 180},
    },
    "entrega_salmao": {
        "name": "Banquete de salmão",
        "description": "\"Três salmões assados para um casamento no sítio. Bem assados, hein! — Família Moreira\"",
        "goal": {"deliver": [["salmao_assado", 3]]},
        "reward": {"xp": 300, "copper": 220},
    },
    "entrega_pocoes": {
        "name": "Poções para a capela",
        "description": "\"Quatro poções de cura menor para os feridos. — Irmã Celeste\"",
        "goal": {"deliver": [["pocao_cura_menor", 4]]},
        "reward": {"xp": 250, "copper": 160},
    },
    "entrega_fios": {
        "name": "Fio de linho",
        "description": "\"Dez meadas de fio de linho para as velas dos barcos. — Anselmo\"",
        "goal": {"deliver": [["fio_linho", 10]]},
        "reward": {"xp": 150, "copper": 100}, "max_level": 14,
    },
    "entrega_ervas": {
        "name": "Folhas-de-charco",
        "description": "\"Dez folhas-de-charco, frescas. Não me venha com folha murcha. — Mãe Brígida\"",
        "goal": {"deliver": [["folha_charco", 10]]},
        "reward": {"xp": 120, "copper": 80}, "max_level": 12,
    },
    "entrega_carpas": {
        "name": "Carpas da ilhota",
        "description": "\"Quatro carpas prateadas assadas. Dizem que dão sorte. — Lírio\"",
        "goal": {"deliver": [["carpa_assada", 4]]},
        "reward": {"xp": 400, "copper": 260}, "if": {"flag": "barco_consertado"},
    },
}
