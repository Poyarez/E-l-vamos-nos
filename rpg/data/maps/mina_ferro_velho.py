"""Mina de Ferro-Velho — galerias tomadas por kobolds e o fosso da forja do capataz (34 x 14).

Legenda: # rocha   . galeria   = trilhos de vagonete   : entulho   ~ água parada
         v fogo violeta (a forja do culto)

O capataz Gorran guarda o Fosso da Forja: quem atravessa o fosso precisa passar por ele.
Depois que ele cai, os kobolds deixam de atacar e um deles, Pip, abre uma venda no
Salão das Velas.
"""

KOBOLDS_FREE = {"flag": "gorran_derrotado"}
KOBOLDS_ENSLAVED = {"not_flag": "gorran_derrotado"}

MAP = {
    "id": "mina_ferro_velho",
    "name": "Mina de Ferro-Velho",
    "outdoor": False,
    "light": 2,
    "start": (4, 12),
    "legend": {"#": "parede_gruta", ".": "chao_mina", "=": "trilhos", ":": "entulho", "~": "lago_subterraneo",
               "v": "fogo_violeta"},
    "layout": '''
##################################
#........##........###......##...#
#........##......:.##.......##...#
#......:.##........##.......##...#
#........##........##......:##...#
#........#####.:#####.#########.##
####=.########.:#####.#########.##
####=.########.:###::::########.##
####=.......:......::::..........#
####====================.........#
####=.###......####::::..........#
##..=......~~..########........vv#
##..=..#..~~~..########:.......vv#
##################################
''',
    "regions": [
        {
            "id": "galerias_superiores", "name": "Galerias Superiores", "rects": [(0, 0, 18, 13)], "xp": 60,
            "intro": ("A Mina de Ferro-Velho por dentro: galerias escoradas por vigas negras, trilhos de vagonete "
                      "e o cheiro de ferro e de cera quente. De algum lugar adiante vem um cântico agudo, no "
                      "ritmo das picaretas."),
            "day": ["Picaretas batem na rocha em algum lugar, num ritmo que parece música.",
                    "Gotas de cera derretida marcam o chão: alguém passou por aqui com velas.",
                    "Uma voz fininha canta lá na frente e, quando você para, ela para também."],
            "encounters": {
                "chance": 0.12,
                "groups": [
                    {"monsters": ["kobold_escavador"], "weight": 3, "if": KOBOLDS_ENSLAVED},
                    {"monsters": ["kobold_escavador", "kobold_vela"], "weight": 2, "if": KOBOLDS_ENSLAVED},
                    {"monsters": ["kobold_vela"], "weight": 2, "if": KOBOLDS_ENSLAVED},
                    {"monsters": ["kobold_geomante"], "weight": 1, "if": KOBOLDS_ENSLAVED},
                    {"monsters": ["toupeira_ferro"], "weight": 2},
                    {"monsters": ["morcego_caverna", "morcego_caverna"], "weight": 1, "levels": [8, 9],
                     "if": KOBOLDS_FREE},
                ],
            },
        },
        {
            "id": "fosso_da_forja", "name": "Fosso da Forja", "rects": [(19, 0, 33, 13)], "xp": 80,
            "intro": ("A parte funda da mina, onde o veio de ferro encontra o carvão. O ar é quente e seco, e um "
                      "brilho violeta pulsa nas paredes, vindo de uma forja que não deveria existir."),
            "day": ["O calor da forja violeta chega até aqui, sem cheiro de lenha nem de fumaça.",
                    "Correntes rangem em algum lugar, presas a alguma coisa que se mexe.",
                    "Marteladas ecoam pelo fosso: uma, duas, três... e um chicote estala."],
            "encounters": {
                "chance": 0.14,
                "groups": [
                    {"monsters": ["kobold_escavador", "kobold_vela"], "weight": 2, "if": KOBOLDS_ENSLAVED},
                    {"monsters": ["kobold_geomante", "kobold_escavador"], "weight": 2, "if": KOBOLDS_ENSLAVED},
                    {"monsters": ["toupeira_ferro"], "weight": 2},
                    {"monsters": ["toupeira_ferro", "toupeira_ferro"], "weight": 1, "if": KOBOLDS_FREE},
                ],
            },
        },
    ],
    "landmarks": [
        {
            "id": "boca_mina", "name": "Boca da Mina", "x": 4, "y": 12, "xp": 30,
            "description": ("A luz das colinas morre poucos passos depois da entrada. Os trilhos de vagonete descem "
                            "para o escuro, entre vigas marcadas com olhos pintados de vermelho."),
            "examine": ("Na viga mais baixa, alguém riscou com um prego: \"D. — 3ª lua — ainda vivo\". Os riscos "
                        "continuam por toda a madeira, um para cada dia. São muitos."),
        },
        {
            "id": "salao_velas", "name": "Salão das Velas", "x": 4, "y": 3, "xp": 40,
            "description": ("Um salão escavado onde centenas de velas queimam em nichos, prateleiras e capacetes "
                            "pendurados. Os kobolds fazem aqui as velas que levam na cabeça — e, pelo jeito, as "
                            "acendem todas ao mesmo tempo."),
            "examine": ("No centro do salão, um altarzinho de pedras empilhadas sustenta um pedaço de minério em "
                        "forma de rosto adormecido. Os kobolds deixaram oferendas: velas, carvão, um dente. "
                        "Rezam para alguma coisa que dorme debaixo deles."),
        },
        {
            "id": "poco_fundo", "name": "Poço Fundo", "x": 1, "y": 1, "xp": 30, "hidden": True,
            "description": ("Num canto do salão, um poço vertical desce para a escuridão. Uma escada de corda presa a "
                            "estacas some lá embaixo, e um ar morno sobe do fundo, cheirando a enxofre."),
            "examine": ("Você joga uma pedrinha no poço e conta. E conta. O som não volta. Os kobolds chamam o que "
                        "há lá embaixo de \"Fundo-Fundo\" — e foi de lá que eles vieram."),
        },
        {
            "id": "galeria_ferro", "name": "Galeria do Ferro", "x": 16, "y": 2, "xp": 40,
            "description": ("Uma galeria larga onde a rocha é vermelha como carne: o grande veio de ferro que deu nome "
                            "à mina. Picaretas de mineiro e de kobold jazem lado a lado, abandonadas no meio do "
                            "trabalho."),
            "examine": ("O veio é largo e rico — Brom tinha razão: ferro bom mesmo, só aqui. As marcas de "
                        "picareta mais recentes são pequenas e numerosas: os kobolds cavaram dia e noite."),
            "resources": [{"node": "veio_ferro_bom"}],
        },
        {
            "id": "galeria_alagada", "name": "Galeria Alagada", "x": 11, "y": 10, "xp": 35,
            "description": ("A tremura rompeu um veio de água, e esta galeria virou um poço escuro e parado. Capacetes "
                            "de mineiro boiam na superfície, girando devagar."),
            "examine": ("Os capacetes são da vila — você reconhece o modelo do que está pendurado na forja do Brom. "
                        "Ninguém morreu aqui, felizmente: as botas e os casacos foram largados na fuga."),
            "loot": {
                "flag": "galeria_alagada_bolsa",
                "items": [["pocao_cura", 2], ["vela_kobold", 3]],
                "copper": 350,
                "xp": 40,
                "text": ("Presa numa viga, acima da linha da água, está a bolsa de um mineiro: duas poções, uns "
                         "tocos de vela e as economias de alguém que fugiu com pressa demais para voltar."),
            },
        },
        {
            "id": "veio_carvao", "name": "Veio de Carvão", "x": 25, "y": 2, "xp": 40,
            "description": ("Uma câmara de paredes negras e brilhantes, onde o ferro dá lugar ao carvão. Montes de "
                            "carvão já quebrado esperam ao lado de cestos de vime do tamanho de um kobold."),
            "examine": ("Ferro mais carvão no fogo mais quente: é assim que se faz aço. Alguém aqui embaixo sabia "
                        "disso muito bem — os cestos vão todos na direção do fosso."),
            "resources": [{"node": "veio_carvao"}],
        },
        {
            "id": "fosso_forja", "name": "Fosso da Forja", "x": 27, "y": 10, "xp": 50,
            "description": ("O fundo da mina virou uma forja: bigornas, foles de couro e montes de pontas de flecha "
                            "recém-temperadas, tudo iluminado por um fogo violeta que brota da própria rocha e não "
                            "solta fumaça."),
            "examine": ("As pontas de flecha são idênticas à que estava cravada na carroça de Zahir: ferro bom, "
                        "forjado com capricho. Num canto, correntes partidas e uma esteira de palha mostram onde o "
                        "ferreiro prisioneiro dormia."),
            "stations": [{"id": "fornalha", "name": "Fornalha violeta", "if": KOBOLDS_FREE,
                          "closed": "Com o capataz vigiando, ninguém chega perto da fornalha."},
                         {"id": "bigorna", "name": "Bigorna do fosso", "if": KOBOLDS_FREE,
                          "closed": "Com o capataz vigiando, ninguém chega perto da bigorna."}],
            "encounter": {
                "flag": "gorran_derrotado", "radius": 2, "boss": True,
                "monsters": [["capataz_gorran", 10]],
                "intro": ("Um meio-ogro enorme, largo como uma porta, solta o martelo sobre a bigorna e estala um "
                          "chicote em brasa. Atrás dele, um rapaz magro e acorrentado ergue a cabeça. \"Mais um "
                          "voluntário?\", ri o capataz. \"A Senhora vai gostar de saber.\""),
                "victory": ("Gorran cai de joelhos sobre a própria bigorna, e o fogo violeta encolhe até virar uma "
                            "brasa comum. Lá das galerias, o cântico dos kobolds muda de tom — fica alegre. Num "
                            "canto da forja, o rapaz acorrentado olha para você sem acreditar."),
                "journal": {
                    "id": "capataz_derrotado", "title": "O capataz da mina",
                    "text": ("Gorran, um meio-ogro marcado com a lua cortada, escravizava os kobolds da Mina de "
                             "Ferro-Velho e forjava pontas de flecha no Fosso da Forja. Ele carregava a chave de um "
                             "cofre."),
                },
            },
        },
        {
            "id": "cofre_capataz", "name": "Cofre do Capataz", "x": 31, "y": 2, "xp": 40,
            "description": ("Uma câmara escavada à parte, com uma cama de verdade, uma mesa e um cofre de ferro "
                            "pregado à rocha. O capataz não dormia com os outros."),
            "examine": ("Na mesa, restos de cera de lacre violeta e um tinteiro seco: o capataz recebia e mandava "
                        "cartas. O cofre de ferro, pregado à rocha, é a única coisa bem cuidada do quarto."),
            "chest": {
                "flag": "cofre_capataz_aberto",
                "key": "chave_capataz",
                "locked": "O cofre de ferro tem uma fechadura grossa, com uma lua cortada gravada em volta.",
                "items": [["carta_capataz", 1], ["barra_aco", 3]],
                "copper": 800,
                "xp": 120,
                "text": ("Dentro do cofre: um saco de moedas, três barras de aço e uma carta com lacre violeta, "
                         "assinada apenas com um \"M.\". Você lê e sente o sangue gelar: o Bando do Corvo, a mina, "
                         "as luas — tudo faz parte do mesmo plano."),
            },
        },
    ],
    "portals": [
        {
            "id": "mina_saida", "x": 4, "y": 12, "direction": "s", "verb": "sair",
            "label": "Colinas de Cobre", "target": ("vale_primordia", 53, 12),
            "travel_text": "Você segue os trilhos de volta à luz e sai, piscando, para o vento das colinas.",
        },
        {
            "id": "poco_fundo_descida", "x": 1, "y": 1, "verb": "entrar", "label": "Fundo-Fundo",
            "locked": True,
            "locked_text": ("Você desce alguns degraus da escada de corda, e ela termina no vazio: o resto foi "
                            "cortado. Lá embaixo, muito longe, brilham luzinhas de vela. Para descer ao Fundo-Fundo "
                            "será preciso muito mais corda — e muito mais coragem. (Um dia, talvez.)"),
        },
    ],
}
