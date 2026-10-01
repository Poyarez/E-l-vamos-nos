"""Vale de Primórdia — a zona inicial (60 x 30).

Legenda do desenho:
  ^ montanhas   . campina    " relva alta   , lavoura     T floresta   Y mata antiga
  n colinas     o pedregulhos ~ água funda  w água rasa   = estrada    # ponte/passarela
  % pântano     : ruas        H construções & ruínas      + túmulos    O caverna   | cachoeira

Regiões são retângulos (x1, y1, x2, y2); a primeira que contém o tile vence.
Nas dicas (``hint``), ``{direcao}`` vira a direção até o local ("ao noroeste").
"""

MAP = {
    "id": "vale_primordia",
    "name": "Vale de Primórdia",
    "outdoor": True,
    "start": (30, 18),
    "legend": {
        "^": "montanha", ".": "planicie", '"': "relva_alta", ",": "lavoura", "T": "floresta",
        "Y": "mata_antiga", "n": "colinas", "o": "rochas", "~": "agua", "w": "agua_rasa",
        "=": "estrada", "#": "ponte", "%": "pantano", ":": "calcamento", "H": "construcao",
        "&": "ruinas", "+": "tumulos", "O": "caverna", "|": "cachoeira",
    },
    "layout": '''
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^=^^^^^^^^^^^^^^^^^^^
^^..."......^^^^^^^^^^^^^^^^^^^^^^^^^^^^=^^^^^&&&^^^^^^^^^^^
^^TTTT.TTTTTTTTTT^^^^|^^^^^^^^."....^^^^=^^^.&.&&&.&&&&&.^^^
^^TTYYY.TTTTTTT"TTT.~~~o...."...."...".==....&...o.o..&..&^^
^^YYYYYYYTT.TT.TTT.o~~~o..........".."=="..".....o...o....&^
^^YYYYYYYYTTT...TTTT.~...............==......&...o.o.....&^^
^^YYYYYYYYTTTT.TTTT..~~...........====.......&...........&.^
^^YYYYYYYYTTTTTTTT....~.."....=====..."......&&.&&&.&&&&&&.^
^^YYYYYYY..TTT.TTTT...~.......=".."...""......."......"....^
^^TTYYYT...TTTTTTTT...~~......=..........".nnnnn"..nnnnnno^^
^^TTTT.T..TTT.TTTTTT...~......=.....+++......nnnnnnnnonnnn^^
^^.TTTTTTTTTTTTTT......~....T.:.....+++.."..nn".nnnn.nno..^^
^^TTTTTTTTTTTTTTTT""...~~..H:::H:H..+++.".."n"n""nn==O"on.^^
^^T.TTT.TTTT.TTTTT.."...~..:H:::::H.........n.n"====nnnnon^^
^^TTTTTTTT....TTT.......~..:::::HH:........"n.===nn".n"nn.^^
^^TOTTTTTT...T.TTTT=====w==::::::::============nonn.onnnn"^^
^^TTT.TTT.TTTTT.TT."....~..:H:::::..,,,,,,,,nnnnnnnnnnnnon^^
^^TTTTTTTTTTTTTTTT......~..H:::::H..,,,,,,,,n.nnon.nnnnnnn^^
^^TTTTT.TTTTTTTT."......~.....=.....,.,H,,,,"no.nnn"nnowno.^
^^TTTTT.TTTTTT.TT......"~~,,,,=.,.,,H,.,,,,..noonn.n.nnnn".^
^^%Tw%%TT%%%%%%T%.w%...."~~~.,=,,",,,,,,.,,,n"onn..nnon..n.^
^^%%T.%wT.%%.%%%%.........,~~~#~~.,.....~#~~~~~~....."...".^
^^%%%T%.w.T.########......,,,"=,~~~~~.~~~#~~~~~~~~..&......^
^^%w.%w%.H.%%.Tw%%............=.."..~~~~~~~~~~~~~~~........^
^^%%%%%.T.%%%%%.%.%...........=.....~~~~~~~~~T.~~~~~......^^
^^%%w%w%%.T%%%%%%.."."....."..=".....~~~~~~~~~~~~~~.."....^^
^^%%%%%%%.%%.%w%%w%....."...".=....."~~~~~~~~~~~~~~...."..^^
^^%.w%%%%.%%%.w%%.%%..........=..."....~~~~~~~~~~......."..^
^^^^^^....".^^^^^^^^^^^^^^^^^^=^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^=^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
''',
    # ------------------------------------------------------------------ regiões
    "regions": [
        {
            "id": "vila_primordia", "name": "Vila de Primórdia", "rects": [(26, 11, 35, 18)], "xp": 0,
            "intro": ("Uma vila de pedra e palha aninhada no coração do vale, onde todos se conhecem pelo "
                      "nome — e todos já sabem que há alguém de fora na cidade."),
            "day": ["O martelo da forja ecoa pelas ruas em um ritmo constante.",
                    "Crianças correm entre as casas brincando de cavaleiros e dragões.",
                    "Cheiro de pão quente escapa de alguma janela."],
            "night": ["Música abafada e risadas escapam da estalagem.",
                      "Um vigia passa com uma lanterna e cumprimenta você com um aceno cansado."],
        },
        {
            "id": "ruinas_veltharas", "name": "Ruínas de Vel'Tharas", "rects": [(44, 1, 58, 8)], "xp": 45,
            "intro": ("Os restos de um templo de pedra branca, mais antigo que qualquer reino conhecido. Os "
                      "moradores evitam o lugar: dizem que nas noites sem lua uma luz violeta dança entre "
                      "as colunas."),
            "day": ["O vento assobia entre as colunas partidas, formando quase uma melodia.",
                    "Nenhum pássaro canta aqui. Nenhum inseto zumbe.",
                    "Você tem a nítida sensação de estar sendo observado."],
            "night": ["Um brilho violeta pulsa fraco nas frestas das pedras, como uma respiração.",
                      "Sussurros numa língua desconhecida parecem vir de todos os lados — e de lugar nenhum."],
        },
        {
            "id": "colinas_de_cobre", "name": "Colinas de Cobre", "rects": [(44, 9, 58, 21)], "xp": 35,
            "intro": ("Morros de terra vermelha riscados de veios verdes de cobre. Antes das tremuras, "
                      "mineiros subiam a Estrada da Mina todos os dias; hoje, só o vento faz esse caminho."),
            "day": ["O sol arranca reflexos esverdeados das pedras expostas.",
                    "Um gavião plana sobre as colinas, à procura de lebres.",
                    "Restos de trilhos de vagonete enferrujam na encosta."],
            "night": ["O vento carrega um eco metálico, como picaretas batendo muito longe.",
                      "Lá no alto, perto da mina, uma luz bruxuleia — e se apaga."],
        },
        {
            "id": "campos_dourados", "name": "Campos Dourados", "rects": [(36, 9, 43, 20), (25, 19, 35, 20)],
            "xp": 30,
            "intro": ("As lavouras que alimentam o vale: trigo, cevada e nabos até onde a vista alcança, "
                      "cortados por cercas de pedra e trilhas de carroça."),
            "day": ["Um lavrador ergue o chapéu de palha em cumprimento, sem parar de trabalhar.",
                    "As pás do moinho giram preguiçosas ao vento.",
                    "Corvos levantam voo em bando, protestando contra a sua passagem."],
            "night": ["O vento faz o trigo sussurrar como uma multidão inquieta.",
                      "Uma lanterna solitária balança ao longe, perto do moinho."],
            "encounters": {
                "chance": 0.04, "night_bonus": 0.06,
                "groups": [
                    {"monsters": ["corvo_ladrao"], "weight": 4, "time": "dia"},
                    {"monsters": ["javali_jovem"], "weight": 1},
                    {"monsters": ["rato_gigante"], "weight": 4, "time": "noite"},
                    {"monsters": ["rato_gigante", "rato_gigante"], "weight": 2, "time": "noite"},
                ],
            },
        },
        {
            "id": "lago_espelhado", "name": "Lago Espelhado", "rects": [(35, 21, 58, 28)], "xp": 30,
            "intro": ("Um lago tão parado que o céu parece ter dois andares. Garças pescam nas margens, e "
                      "uma ilhota coberta de árvores repousa em seu centro, inalcançável sem um barco."),
            "day": ["Uma garça mergulha o bico na água e volta com um peixe prateado.",
                    "O lago reflete as nuvens com uma perfeição inquietante.",
                    "Libélulas azuis zumbem rente à água."],
            "night": ["A lua se duplica no lago, imóvel como um olho aberto.",
                      "Algo grande quebra a superfície do lago ao longe — e some."],
        },
        {
            "id": "coracao_floresta", "name": "Coração da Floresta", "rects": [(1, 1, 9, 19)], "xp": 45,
            "intro": ("Aqui a Floresta Sussurrante fica velha de verdade: troncos colossais, musgo até os joelhos "
                      "e um silêncio que pesa. Os caçadores não passam do Carvalho Ancião — e os lobos sabem "
                      "disso."),
            "day": ["Um galho estala atrás de você. Quando você se vira, não há nada.",
                    "Marcas de garras profundas riscam a casca de um tronco, na altura do seu rosto.",
                    "A luz do dia chega aqui verde e fraca, filtrada por mil camadas de folhas."],
            "night": ["Olhos azuis brilham entre as árvores e somem antes que você os conte.",
                      "Os sussurros das copas parecem combinar algo entre si."],
            "encounters": {
                "chance": 0.11, "night_bonus": 0.06,
                "groups": [
                    {"monsters": ["lobo_cinzento"], "weight": 4},
                    {"monsters": ["lobo_cinzento", "lobo_faminto"], "weight": 2},
                    {"monsters": ["aranha_da_mata"], "weight": 3},
                    {"monsters": ["aranha_da_mata", "aranha_da_mata"], "weight": 1},
                    {"monsters": ["javali_espinhento"], "weight": 2},
                    {"monsters": ["lobo_gelido"], "weight": 2, "if": {"not_flag": "presa_de_gelo_derrotado"}},
                    {"monsters": ["espirito_sussurrante"], "weight": 3, "time": "noite"},
                ],
            },
        },
        {
            "id": "floresta_sussurrante", "name": "Floresta Sussurrante", "rects": [(1, 1, 19, 19)], "xp": 40,
            "intro": ("Uma floresta antiga e densa a oeste do vale. O nome vem do vento nas copas, que soa "
                      "como vozes — mas os caçadores juram que, às vezes, as vozes dizem nomes."),
            "day": ["As folhas sussurram acima de você. Por um instante, parece o seu nome.",
                    "Um veado ergue a cabeça, encara você e desaparece entre as árvores.",
                    "Um pica-pau martela um tronco em algum lugar próximo."],
            "night": ["Uivos distantes respondem uns aos outros pela floresta.",
                      "Os sussurros das copas ficam mais altos no escuro, mais insistentes."],
            "encounters": {
                "chance": 0.08, "night_bonus": 0.06,
                "groups": [
                    {"monsters": ["lobo_faminto"], "weight": 4},
                    {"monsters": ["lobo_faminto", "lobo_faminto"], "weight": 2},
                    {"monsters": ["lobo_cinzento"], "weight": 2, "levels": [3, 4]},
                    {"monsters": ["javali_espinhento"], "weight": 2, "levels": [3, 4]},
                    {"monsters": ["aranha_da_mata"], "weight": 2, "levels": [3, 4]},
                    {"monsters": ["espirito_sussurrante"], "weight": 3, "time": "noite", "levels": [4, 5]},
                ],
            },
        },
        {
            "id": "pantano_lodo_negro", "name": "Pântano de Lodo-Negro", "rects": [(1, 20, 20, 28)], "xp": 40,
            "intro": ("Um charco fétido no canto sudoeste do vale, onde a água escorre e apodrece. Os "
                      "aldeões só vêm aqui por necessidade — geralmente para comprar remédios da velha "
                      "que mora na cabana."),
            "day": ["Uma garça-negra observa você de cima de um tronco podre.",
                    "Bolhas estouram na lama com um som obsceno.",
                    "Nuvens de mosquitos seguem você como uma sombra zumbidora."],
            "night": ["Fogos-fátuos acendem e se apagam sobre o charco.",
                      "Um coaxar grave, grande demais para qualquer sapo, ecoa pela névoa."],
        },
        {
            "id": "ribeirao_prateado", "name": "Margens do Ribeirão Prateado", "rects": [(20, 1, 25, 22)],
            "xp": 30,
            "intro": ("O Ribeirão Prateado nasce na grande cachoeira ao norte e corta o vale até o Lago "
                      "Espelhado. Lavadeiras, pescadores e crianças disputam suas margens."),
            "day": ["A água do ribeirão corre clara e rápida sobre as pedras.",
                    "Salgueiros mergulham os galhos no ribeirão como se bebessem.",
                    "Uma lontra desliza para dentro da água ao ouvir seus passos."],
            "night": ["O murmúrio do ribeirão é o único som da noite.",
                      "A água reflete a lua em fragmentos dançantes."],
            "encounters": {
                "chance": 0.05, "night_bonus": 0.02,
                "groups": [
                    {"monsters": ["lagarto_ribeirao"], "weight": 3},
                    {"monsters": ["corvo_ladrao"], "weight": 1, "time": "dia"},
                ],
            },
        },
        {
            "id": "prados_do_norte", "name": "Prados do Norte", "rects": [(26, 0, 43, 10)], "xp": 30,
            "intro": ("Campinas abertas entre a vila e as montanhas, cortadas pela Estrada Real que sobe ao "
                      "Passo do Norte. O ar aqui é mais fino e cheira a flores do campo."),
            "day": ["Ovelhas pastam ao longe, vigiadas por um cão atento.",
                    "O vento desce das montanhas trazendo um frescor de neve.",
                    "Abelhas zumbem de flor em flor, carregadas de pólen."],
            "night": ["As estrelas parecem mais próximas aqui, quase ao alcance da mão.",
                      "O vento frio das montanhas faz você apertar a capa contra o corpo."],
            "encounters": {
                "chance": 0.05, "night_bonus": 0.03,
                "groups": [
                    {"monsters": ["corvo_ladrao"], "weight": 4},
                    {"monsters": ["javali_jovem"], "weight": 3},
                    {"monsters": ["corvo_ladrao", "corvo_ladrao"], "weight": 1},
                ],
            },
        },
        {
            "id": "caminho_do_sul", "name": "Caminho do Sul", "rects": [(21, 21, 34, 29)], "xp": 25,
            "intro": ("A parte baixa do vale, por onde a Estrada Real desce até o Portão Sul. Foi por aqui "
                      "que você chegou."),
            "day": ["Marcas de rodas recentes sulcam a estrada — talvez da carroça que trouxe você.",
                    "Um bando de pardais se banha na poeira da estrada."],
            "night": ["A estrada para o sul está deserta e silenciosa.",
                      "Ao longe, no Portão Sul, uma fogueira de vigia crepita."],
            "encounters": {
                "chance": 0.04, "night_bonus": 0.03,
                "groups": [
                    {"monsters": ["corvo_ladrao"], "weight": 2, "time": "dia"},
                    {"monsters": ["javali_jovem"], "weight": 2},
                    {"monsters": ["rato_gigante"], "weight": 2, "time": "noite"},
                ],
            },
        },
    ],
    # ------------------------------------------------------------------ locais notáveis
    "landmarks": [
        # --- Vila de Primórdia
        {
            "id": "entrada_vila", "name": "Entrada da Vila", "x": 30, "y": 18, "xp": 0,
            "description": ("Uma placa de madeira pintada à mão balança em correntes: \"VILA DE PRIMÓRDIA — "
                            "PAZ A QUEM CHEGA\". Ao norte, as ruas de pedra levam à praça; ao sul, a Estrada "
                            "Real desce rumo à ponte e ao Portão Sul do Vale."),
            "night": ("A placa da vila range ao vento. Um lampião num poste ilumina as primeiras casas; "
                      "além dele, a estrada para o sul mergulha na escuridão."),
            "examine": ("Alguém entalhou pequenas marcas na base da placa: dezenas de tracinhos, agrupados de "
                        "cinco em cinco, sob a inscrição \"aventureiros que chegaram\". Ao lado, uma segunda "
                        "coluna tem bem menos marcas: \"aventureiros que voltaram\"."),
        },
        {
            "id": "praca_poco", "name": "Praça do Poço Antigo", "x": 30, "y": 15, "xp": 15,
            "description": ("O coração da vila. Um poço de pedra, muito mais antigo que as casas ao redor, "
                            "ocupa o centro da praça, com um telhadinho de madeira e um balde preso a uma "
                            "corrente. Bancos de pedra, uma figueira e o quadro de avisos completam a cena."),
            "night": ("A praça está quieta. A luz da estalagem, a leste, pinta as pedras do poço de laranja; "
                      "o balde balança devagar, sem vento algum."),
            "examine": ("As pedras do poço são brancas e lisas — iguais às das ruínas a nordeste, nada "
                        "parecidas com as do resto da vila. No quadro de avisos, entre pedidos de ferreiro e "
                        "um gato perdido, está o mesmo cartaz que trouxe você: \"PROCURAM-SE AVENTUREIROS\". "
                        "Lá embaixo, no fundo do poço, cintilam moedas atiradas por gerações de desejos."),
        },
        {
            "id": "estalagem", "name": "Estalagem do Javali Dourado", "x": 33, "y": 14, "xp": 15, "rest": True,
            "description": ("Uma construção de dois andares com um javali dourado (bem pouco dourado, na "
                            "verdade) entalhado sobre a porta. Lá dentro, uma lareira enorme, mesas de carvalho "
                            "manchadas de cerveja e cheiro de ensopado. Aqui você pode dormir em segurança."),
            "night": ("A estalagem é o lugar mais vivo da vila à noite: música de alaúde, canecas batendo e "
                      "risadas vazando pelas janelas embaçadas. Um quarto quente espera por você."),
            "examine": ("Atrás do balcão, uma cabeça de javali empalhada usa um chapéu de festa. Num quadro de "
                        "giz: \"Ensopado do dia: javali (de novo). Quarto: 5 cobres. Fiado: NÃO.\" Alguém "
                        "escreveu embaixo, com outra letra: \"exceto para heróis\"."),
            "stations": [{"id": "fogo", "name": "Cozinha da estalagem", "burn": 0.75}],
        },
        {
            "id": "forja", "name": "Forja do Martelo Rubro", "x": 28, "y": 16, "xp": 15,
            "description": ("O calor da forja atinge você antes mesmo da porta. Uma bigorna gasta, um fole de "
                            "couro e prateleiras de ferraduras, foices e pregos dividem espaço com algumas "
                            "espadas expostas — simples, mas honestas."),
            "night": ("As brasas ainda brilham sob as cinzas, vermelhas como olhos sonolentos. A porta da "
                      "forja está trancada com uma corrente."),
            "examine": ("Pendurado acima da bigorna, um martelo de cabo vermelho tem um nome gravado: "
                        "\"Davi\". Ao lado, um capacete de mineiro amassado, coberto de poeira. Ninguém parece "
                        "ter coragem de tirá-los dali."),
            "stations": [
                {"id": "fornalha", "name": "Fornalha do Brom", "if": {"period": ["amanhecer", "manha", "tarde"]},
                 "closed": "A porta da forja está trancada com uma corrente. Brom só acende a fornalha de dia."},
                {"id": "bigorna", "name": "Bigorna do Brom", "if": {"period": ["amanhecer", "manha", "tarde"]},
                 "closed": "A porta da forja está trancada com uma corrente. Volte de dia."},
            ],
        },
        {
            "id": "capela", "name": "Capela da Aurora", "x": 31, "y": 12, "xp": 15,
            "description": ("Uma capela pequena de pedra clara, com um vitral redondo voltado para o leste: o sol "
                            "nascente da Senhora da Aurora. Bancos de madeira, velas e flores do campo ocupam o "
                            "interior silencioso."),
            "night": ("A capela fica aberta à noite, iluminada por uma única lamparina. O vitral, sem sol, "
                      "revela um detalhe que de dia passa despercebido: no canto, há uma pequena lua prateada."),
            "examine": ("No altar, um livro de orações está aberto numa prece antiga: \"Que a Aurora nos guie e "
                        "a Lua nos guarde, até que o Guardião desperte em paz.\" A palavra \"Guardião\" foi "
                        "sublinhada muitas vezes, por mãos diferentes."),
        },
        {
            "id": "casa_ancia", "name": "Casa da Anciã", "x": 28, "y": 13, "xp": 15,
            "description": ("Uma casa baixa coberta de hera, com ervas secando na janela e um sino de vento feito "
                            "de conchas. A porta está sempre entreaberta, como se a dona esperasse visitas — ou "
                            "soubesse quando elas vão chegar."),
            "night": ("Uma vela queima na janela da casa da Anciã. Pela fresta da porta, você vê pergaminhos "
                      "espalhados sobre a mesa."),
            "examine": ("Sobre a mesa, um mapa antigo do vale tem círculos a carvão sobre três lugares: as ruínas "
                        "a nordeste, a cachoeira ao norte e um ponto no meio da floresta. Ao lado de cada "
                        "círculo, alguém desenhou uma pequena lua."),
        },
        {
            "id": "portao_norte", "name": "Portão Norte da Vila", "x": 30, "y": 11, "xp": 10,
            "description": ("Uma paliçada de troncos aponta para o céu, com um portão de madeira aberto durante o "
                            "dia. Uma guarita com o brasão do vale — um sol nascendo atrás de uma montanha — "
                            "abriga a guarda. Ao norte, a Estrada Real sobe pelos prados."),
            "night": ("O portão está fechado e uma tocha arde na guarita. Uma janelinha se abre quando você "
                      "se aproxima — e se fecha ao reconhecer você."),
            "examine": ("Pregado ao portão, um aviso da guarda: \"POR ORDEM DA CAPITÃ: não entrar na Floresta "
                        "Sussurrante depois do pôr do sol. Não se aproximar da Mina de Ferro-Velho. Não mexer "
                        "nas ruínas. Isso vale para VOCÊ, Tomé.\""),
        },
        {
            "id": "mercado", "name": "Mercado da Vila", "x": 32, "y": 16, "xp": 10,
            "description": ("Barracas de lona colorida se espremem neste trecho da rua: queijos, maçãs, cestos de "
                            "vime, ferramentas usadas e um vendedor de amuletos de procedência duvidosa. O "
                            "falatório é constante."),
            "night": ("As barracas estão fechadas, com as lonas amarradas. Um gato rouba um peixe esquecido e "
                      "some no escuro."),
            "examine": ("Há muitas vagas vazias entre as barracas. Uma vendedora explica, sem você perguntar: "
                        "desde que a Rota dos Mercadores foi fechada, as caravanas do sul pararam de vir. "
                        "\"Se continuar assim, no inverno vamos comer nabo com nabo.\""),
        },
        # --- Campos Dourados
        {
            "id": "moinho", "name": "Moinho do Velho Tobias", "x": 39, "y": 18, "xp": 20,
            "hint": "Pás de moinho rangem ao vento, em algum lugar ao {direcao}.",
            "description": ("Um moinho de vento de pedra e madeira, com pás remendadas que giram devagar. Sacos "
                            "de farinha se empilham na porta, com um gato gordo dormindo em cima. O rangido das "
                            "engrenagens lá dentro nunca para."),
            "night": ("As pás do moinho giram contra o céu estrelado, rangendo. Uma luz fraca brilha na janela "
                      "do alto."),
            "examine": ("Na parede, um papel pregado: \"RATOS NO CELEIRO. GRANDES. MUITO GRANDES. PAGO EM "
                        "FARINHA. — T.\" Marcas de garras na porta do celeiro sugerem que \"muito grandes\" "
                        "não é exagero."),
        },
        {
            "id": "sitio_moreira", "name": "Sítio dos Moreira", "x": 36, "y": 19, "xp": 15,
            "description": ("Uma casa de fazenda com um curral de ovelhas, galinheiro, uma horta caprichada e um "
                            "linhal de flores azuis balançando ao vento. Na varanda, uma roca de fiar descansa "
                            "ao lado de cestos de lã. Roupas secam no varal, e um cão sarnento late para você "
                            "abanando o rabo, sem decidir se é ameaça ou festa."),
            "night": ("As galinhas estão no poleiro e o cão dorme na varanda. Pela janela, uma família janta em "
                      "silêncio, os olhos voltados para as plantações."),
            "examine": ("Há marcas de patas enormes na lama perto do galinheiro, e a cerca foi remendada às "
                        "pressas. Na porta, uma ferradura pendurada de cabeça para cima — para segurar a sorte. "
                        "Um bilhete preso à roca diz: \"Pode fiar à vontade, só não leve a roca. — Família "
                        "Moreira\"."),
            "resources": [{"node": "linhal"}, {"node": "ovelhas"}],
            "stations": [{"id": "roca", "name": "Roca de fiar dos Moreira"}],
        },
        {
            "id": "espantalho", "name": "Espantalho Solitário", "x": 42, "y": 19, "xp": 20,
            "description": ("No meio do trigal, um espantalho de roupas puídas e cabeça de saco ergue os braços "
                            "para o céu. O rosto foi costurado com linha vermelha num sorriso largo demais. Os "
                            "corvos, curiosamente, mantêm distância."),
            "night": ("O espantalho... estava virado para o outro lado durante o dia? O sorriso costurado "
                      "parece mais largo à luz da lua."),
            "examine": ("De perto, você nota que a palha está chamuscada nas pontas e que há terra fresca em "
                        "volta da estaca, como se ela tivesse sido arrancada e recolocada. Um dos botões que "
                        "fazem os olhos é de prata antiga."),
        },
        {
            "id": "cemiterio", "name": "Cemitério da Colina", "x": 37, "y": 11, "xp": 20,
            "description": ("Uma pequena colina cercada por um muro baixo de pedra, onde os mortos da vila "
                            "descansam sob lápides tortas e um salgueiro solitário. Algumas lápides não têm nome, "
                            "apenas uma lua entalhada."),
            "night": ("Névoa se acumula entre as lápides. O salgueiro range. Por um instante, você jura ver "
                      "alguém de pé junto ao muro — mas não há ninguém."),
            "examine": ("As lápides mais antigas, no topo da colina, são de pedra branca e trazem a mesma lua "
                        "crescente entalhada. A mais velha tem um nome quase apagado: \"Kael, último Vigia da "
                        "Lua\". Há flores frescas diante dela. Quem as deixou?"),
        },
        # --- Prados do Norte
        {
            "id": "pedra_viajante", "name": "Pedra do Viajante", "x": 32, "y": 8, "xp": 25,
            "description": ("Um enorme bloco de granito à beira da Estrada Real, coberto de nomes, datas, desenhos "
                            "e recados entalhados por gerações de viajantes. Diz a tradição que quem deixa sua "
                            "marca aqui sempre encontra o caminho de volta."),
            "night": ("A pedra é uma sombra maciça à beira da estrada. Os entalhes parecem se mover quando as "
                      "nuvens passam pela lua."),
            "examine": ("Entre centenas de nomes, alguns recados chamam sua atenção:\n"
                        "  \"Tobias + Marta\", dentro de um coração.\n"
                        "  \"Os lobos de olhos azuis não são lobos. — R.\"\n"
                        "  \"Atrás do véu de prata, a lua dorme em sua casa. — K.\"\n"
                        "  \"Cheguei aqui com nada e saio com menos. Valeu a pena. — L.\""),
        },
        {
            "id": "caravana", "name": "Acampamento da Caravana", "x": 35, "y": 9, "xp": 20,
            "description": ("Três carroças coloridas formam um semicírculo em volta de uma fogueira. Tapetes, "
                            "especiarias, lamparinas de cobre e caixotes com etiquetas em línguas estrangeiras "
                            "se amontoam ao redor. Mulas pastam presas a uma estaca."),
            "night": ("A fogueira da caravana arde baixo; alguém toca uma melodia triste num instrumento de "
                      "cordas que você não conhece. Um guarda corpulento cochila com uma cimitarra no colo."),
            "examine": ("As rodas das carroças estão cobertas de lama seca do sul, e há uma flecha quebrada "
                        "cravada na lateral de uma delas. A caravana chegou ao vale por pouco — e não parece "
                        "ter pressa de sair."),
            "stations": [{"id": "fogo", "name": "Fogueira da caravana"}],
        },
        {
            "id": "passo_norte", "name": "Passo do Norte", "x": 40, "y": 0, "xp": 40,
            "hint": "Um vento gelado desce das montanhas ao {direcao}.",
            "description": ("A Estrada Real sobe em ziguezague até uma garganta estreita entre dois picos nevados: "
                            "o Passo do Norte, caminho para a cidade mineira de Pedravale. Ou era: um deslizamento "
                            "de pedras do tamanho de casas fecha completamente a passagem."),
            "night": ("O vento uiva pelo desfiladeiro, gelado. Pedras soltas ainda rolam do alto, de vez em "
                      "quando, com estalos que ecoam como trovões."),
            "examine": ("As rochas do deslizamento têm marcas estranhas: não parecem ter caído sozinhas. Algumas "
                        "estão fundidas umas às outras, como se algo muito quente as tivesse tocado. Do outro "
                        "lado, muito abafado, você ouve o som de picaretas."),
        },
        # --- Margens do Ribeirão Prateado
        {
            "id": "cachoeira", "name": "Cachoeira do Véu de Prata", "x": 23, "y": 3, "xp": 40,
            "hint": "Você ouve o rugido de muita água caindo, em algum lugar ao {direcao}.",
            "description": ("O Ribeirão Prateado despenca de um penhasco altíssimo numa cortina de água tão fina e "
                            "brilhante que parece um véu de noiva. A névoa forma arco-íris sobre o poço lá "
                            "embaixo, e as pedras ao redor estão cobertas de musgo esmeralda."),
            "night": ("Sob a lua, a cachoeira parece feita de prata líquida. O rugido da água abafa todos os "
                      "outros sons do mundo."),
            "examine": ("A passagem atrás do véu continua lá, escura e convidativa. Os degraus de pedra brilham, "
                        "molhados. (Use 'entrar' para atravessar.)"),
            "resources": [{"node": "musgo_prateado"}],
            "secret": {
                "flag": "segredo_cachoeira",
                "xp": 120,
                "text": ("Você se arrisca pelas pedras escorregadias junto à queda d'água e percebe algo que só "
                         "se vê bem de perto: a cortina de água não toca a rocha. Há um vão escuro atrás do véu "
                         "de prata — e degraus talhados na pedra, cobertos de musgo, levando para dentro da "
                         "montanha. Uma passagem secreta! (Use 'entrar' para atravessar o véu.)"),
                "journal": {
                    "title": "A passagem atrás do véu",
                    "text": ("Atrás da Cachoeira do Véu de Prata existe uma gruta escondida. Degraus antigos "
                             "levam para dentro da rocha."),
                },
            },
        },
        {
            "id": "vau_lavadeiras", "name": "Vau das Lavadeiras", "x": 24, "y": 15, "xp": 20,
            "description": ("Aqui o Ribeirão Prateado se alarga e fica raso o bastante para atravessar a pé. "
                            "Pedras chatas servem de tábua para as lavadeiras da vila, que esfregam roupas e "
                            "trocam fofocas na margem."),
            "night": ("O vau está deserto. A água gelada corre veloz no escuro; sem as lavadeiras, o lugar "
                      "parece maior e mais solitário."),
            "examine": ("Presa entre duas pedras no fundo, você vê uma escama do tamanho de uma moeda, "
                        "azul-prateada e quase transparente. Grande demais para qualquer peixe do ribeirão... "
                        "não é?"),
            "resources": [{"node": "cardume_trutas"}, {"node": "cardume_salmoes"}],
        },
        # --- Floresta Sussurrante
        {
            "id": "orla_floresta", "name": "Orla da Floresta Sussurrante", "x": 19, "y": 15, "xp": 20,
            "description": ("A estrada termina abruptamente onde começam as árvores. Um marco de madeira pintado "
                            "de vermelho avisa: \"Floresta Sussurrante. Volte antes do anoitecer.\" Além dele, só "
                            "uma trilha de caçadores, estreita e sombria."),
            "night": ("Daqui, a floresta é uma muralha negra. O marco vermelho parece preto sob a lua, e os "
                      "sussurros das copas soam como um convite."),
            "examine": ("Alguém riscou o aviso do marco e escreveu por cima, em letras tortas: \"ELES ESTÃO "
                        "OUVINDO.\" Embaixo, marcas de garras profundas na madeira."),
        },
        {
            "id": "acampamento_cacadores", "name": "Acampamento de Caçadores Abandonado", "x": 12, "y": 14,
            "xp": 30, "hint": "Um cheiro de cinzas frias vem de algum lugar ao {direcao}.",
            "description": ("Uma clareira com restos de barracas de lona rasgada, uma fogueira apagada há dias e "
                            "peles de animais esquecidas num varal. Panelas viradas e uma mochila revirada "
                            "indicam que os caçadores saíram com muita pressa — ou não saíram."),
            "night": ("As lonas rasgadas balançam como fantasmas. Nas trevas ao redor da clareira, você ouve "
                      "passos que param sempre que você para."),
            "examine": ("Dentro da mochila revirada há um diário encharcado. A última página legível diz: "
                        "\"Terceiro dia. Os lobos voltaram, e o grande estava com eles — branco, olhos azuis "
                        "como gelo. Não atacam. Só olham. Como se esperassem uma ordem.\""),
            "stations": [{"id": "fogo", "name": "Fogueira dos caçadores", "fuel": "tocha"}],
        },
        {
            "id": "clareira_cogumelos", "name": "Clareira dos Cogumelos Luminosos", "x": 9, "y": 9, "xp": 35,
            "hint": "Um brilho azulado escapa por entre as árvores ao {direcao}.",
            "description": ("Uma clareira perfeitamente circular onde cogumelos de chapéu azulado crescem em "
                            "anéis concêntricos. Mesmo de dia eles emitem uma luz fraca, e o ar tem gosto de "
                            "chuva."),
            "night": ("À noite, a clareira é uma visão de sonho: os cogumelos brilham num azul intenso, pulsando "
                      "devagar, e esporos luminosos flutuam como neve ao contrário."),
            "examine": ("Os anéis de cogumelos formam uma espiral perfeita, e no centro a grama é branca e morta, "
                        "num círculo do tamanho de uma pessoa deitada. Os aldeões chamam isso de \"cama das "
                        "fadas\": dormir aqui, dizem, traz sonhos verdadeiros."),
            "resources": [{"node": "cogumelos_lume"}],
        },
        {
            "id": "carvalho_anciao", "name": "Carvalho Ancião", "x": 5, "y": 6, "xp": 45,
            "hint": "Você sente uma presença antiga e imensa ao {direcao}.",
            "description": ("Um carvalho de tamanho impossível domina a mata antiga: dez pessoas de mãos dadas não "
                            "abraçariam o tronco, e as raízes formam grutas e pontes. Os galhos mais baixos estão "
                            "enfeitados com fitas, amuletos e sinos de osso deixados por gerações."),
            "night": ("Na escuridão, o Carvalho Ancião parece respirar. Os sinos de osso nos galhos tilintam "
                      "baixinho, embora não haja vento."),
            "examine": ("Na casca, um rosto foi entalhado há tanto tempo que a árvore cresceu em volta dele, "
                        "tornando-o quase natural. Ao tocar a madeira, você sente uma vibração lenta — como um "
                        "coração que bate uma vez por minuto."),
        },
        {
            "id": "toca_lobos", "name": "Toca dos Lobos", "x": 3, "y": 15, "xp": 40,
            "hint": "Uivos graves ecoam de algum lugar ao {direcao}.",
            "description": ("Uma fenda negra se abre entre raízes e rochas, exalando um cheiro forte de animal e "
                            "carne velha. Ossos roídos se espalham na entrada. Lá dentro, no escuro, algo se move."),
            "night": ("Olhos amarelos brilham aos pares no fundo da toca. Um rosnado grave, longo e paciente faz "
                      "os pelos da sua nuca se arrepiarem."),
            "examine": ("Entre as pegadas de lobo na lama, há uma muito maior que as outras, com garras longas e "
                        "finas. E, ao lado dela, inconfundível: a marca de uma bota humana."),
        },
        {
            "id": "santuario_lua", "name": "Santuário da Lua", "x": 14, "y": 5, "xp": 40,
            "hint": "Por entre as árvores ao {direcao}, você vislumbra pedra trabalhada.",
            "description": ("Numa pequena clareira, um arco de pedra branca coberto de hera abriga um pedestal com "
                            "uma concavidade em forma de lua crescente. O silêncio aqui parece intencional, como "
                            "o de uma biblioteca."),
            "night": ("Sob a lua, o arco brilha suavemente e a concavidade do pedestal parece cheia de luz "
                      "líquida — até você piscar, e ela estar vazia de novo."),
            "examine": ("Gravado no pedestal, em letras antigas que você mal decifra: \"Três luas guardam a "
                        "porta. Uma no véu, uma na mata, uma no altar. Quando as três se unirem, o Vigia "
                        "despertará.\" A concavidade tem o tamanho exato de um pingente."),
            "resources": [{"node": "lirios_da_lua", "if": {"flag": "lirios_da_lua"}}],
            "secret": {
                "flag": "lirios_da_lua",
                "skill": {"alquimia": 30},
                "xp": 80,
                "hint": ("Entre a hera do arco crescem botões brancos e fechados, de uma planta que você não "
                         "reconhece."),
                "text": ("Os botões brancos entre a hera são lírios-da-lua, uma das plantas mais raras do mundo: "
                         "só se abrem sob a lua, e só onde a lua é venerada. Mãe Brígida daria tudo por um "
                         "punhado deles. Volte à noite para colhê-los."),
                "journal": {
                    "title": "Lírios-da-lua",
                    "text": ("No Santuário da Lua crescem lírios-da-lua, que só se abrem à noite. São ingrediente "
                             "dos elixires e frascos mais poderosos da alquimia."),
                },
            },
        },
        # --- Pântano de Lodo-Negro
        {
            "id": "cabana_brigida", "name": "Cabana da Mãe Brígida", "x": 9, "y": 23, "xp": 30,
            "description": ("Uma cabana torta sobre palafitas, com telhado de juncos, potes de vidro com coisas "
                            "flutuando em líquidos turvos e ervas penduradas em todos os caibros. Uma fumaça "
                            "verde-clara sai da chaminé, cheirando a hortelã e a algo que você prefere não "
                            "identificar."),
            "night": ("Velas de cores estranhas ardem nas janelas. Lá dentro, uma voz rouca canta numa língua "
                      "antiga, acompanhada pelo borbulhar de um caldeirão."),
            "examine": ("Na porta, uma placa: \"Remédios, unguentos, conselhos. Pagamento em moedas, favores ou "
                        "segredos.\" Abaixo, menor: \"Não toque nos potes.\" Um dos potes tem um olho que "
                        "acompanha seus movimentos."),
            "resources": [{"node": "ervas_pantano"}],
            "stations": [{"id": "caldeirao", "name": "Caldeirão da Mãe Brígida"}],
        },
        {
            "id": "arvore_enforcados", "name": "Árvore dos Enforcados", "x": 4, "y": 21, "xp": 30,
            "hint": "Um rangido de cordas vem de algum lugar ao {direcao}.",
            "description": ("Um salgueiro morto e retorcido, de casca preta, ergue-se sozinho num ilhote de lama. "
                            "Dos galhos pendem cordas apodrecidas, balançando sem vento. Os aldeões juram que, "
                            "antigamente, ladrões eram julgados aqui."),
            "night": ("As cordas balançam e rangem no escuro. Fogos-fátuos dançam ao redor do tronco, como "
                      "numa ciranda."),
            "examine": ("Uma das cordas não está podre: é nova, de cânhamo trançado, amarrada há pouco tempo. Na "
                        "casca, alguém entalhou uma lua minguante cortada ao meio por um risco."),
        },
        {
            "id": "passarela_troncos", "name": "Passarela de Troncos", "x": 15, "y": 22, "xp": 20,
            "description": ("Uma passarela de troncos amarrados atravessa o pior trecho do pântano, apoiada em "
                            "estacas fincadas na lama. Algumas tábuas estão podres; outras foram trocadas há "
                            "pouco — alguém ainda cuida deste caminho."),
            "night": ("A passarela range e balança sob seus pés. Dos dois lados, a água negra borbulha, e você "
                      "tenta não pensar no que pode estar logo abaixo."),
            "examine": ("Pequenos amuletos de osso e fios coloridos estão amarrados às estacas, a cada dez "
                        "passos. Proteção contra alguma coisa, sem dúvida. Os últimos foram arrancados — e há "
                        "marcas de dentes na madeira."),
        },
        {
            "id": "poca_borbulhante", "name": "Poça Borbulhante", "x": 14, "y": 26, "xp": 30,
            "hint": "Um cheiro forte de enxofre vem de algum lugar ao {direcao}.",
            "description": ("Uma poça de água morna e esverdeada borbulha sem parar, soltando vapores de enxofre. "
                            "As plantas ao redor cresceram estranhas: flores de pétalas negras, juncos retorcidos "
                            "em espiral e um musgo que muda de cor quando você se aproxima."),
            "night": ("A poça brilha com uma fosforescência esverdeada. As bolhas estouram em ritmo regular, "
                      "como se alguma coisa lá no fundo respirasse."),
            "examine": ("Ao mexer na borda com um graveto, você levanta do fundo um pedaço de pedra branca "
                        "entalhada — idêntica às das ruínas de Vel'Tharas. A pedra está morna, como se tivesse "
                        "vida."),
            "resources": [{"node": "flor_de_breu"}],
        },
        # --- Colinas de Cobre
        {
            "id": "mirante_colinas", "name": "Mirante das Colinas", "x": 55, "y": 10, "xp": 50, "reveal": 13,
            "description": ("O ponto mais alto das Colinas de Cobre: um platô de pedra vermelha varrido pelo "
                            "vento, com um velho marco de agrimensor. Daqui, o vale inteiro se descortina aos "
                            "seus pés — a vila, o lago, a floresta escura e as ruínas brancas ao norte."),
            "night": ("Do alto, o vale é um mapa de sombras e pontinhos de luz: as janelas da vila, a fogueira "
                      "da caravana, os fogos-fátuos do pântano. E, nas ruínas, um brilho violeta que pulsa."),
            "examine": ("No marco de agrimensor, uma placa de bronze lista as distâncias até cada canto do vale. "
                        "Alguém acrescentou, a faca, uma seta apontando para a mina, com a palavra \"NÃO\"."),
        },
        {
            "id": "afloramento_cobre", "name": "Afloramento de Cobre", "x": 48, "y": 17, "xp": 25,
            "description": ("Uma encosta desmoronou e expôs a rocha viva, riscada de veios verdes e alaranjados. "
                            "Picaretas abandonadas e um carrinho de mão tombado mostram que os mineiros da vila "
                            "trabalhavam aqui antes das tremuras."),
            "night": ("Os veios de cobre refletem as estrelas com um brilho esverdeado. O vento faz o carrinho "
                      "de mão tombado ranger."),
            "examine": ("As marcas na rocha são recentes, de no máximo uma semana — e não foram feitas por "
                        "ferramentas humanas: são finas, numerosas e baixas, como se feitas por algo da altura "
                        "de uma criança."),
            "resources": [{"node": "veio_cobre"}, {"node": "veio_estanho"},
                          {"node": "veio_ferro", "if": {"flag": "veio_ferro_raso"}}],
            "loot": {
                "flag": "picareta_afloramento",
                "items": [["picareta_velha", 1]],
                "xp": 10,
                "text": ("Entre as picaretas abandonadas pelos mineiros, uma ainda tem o cabo inteiro. A ponta "
                         "está cega, mas ela ainda serve — e ninguém vai sentir falta. (Use 'minerar' aqui.)"),
            },
            "secret": {
                "flag": "veio_ferro_raso",
                "skill": {"mineracao": 15},
                "xp": 60,
                "hint": ("Na base do afloramento, uma faixa de rocha avermelhada chama sua atenção, mas você "
                         "ainda não tem olho de mineiro para entender o que é."),
                "text": ("Com o olho treinado, você reconhece a faixa avermelhada na base do afloramento: ferro! "
                         "Um veio raso e pobre — nada que se compare ao da mina —, mas é ferro. Dá para "
                         "minerá-lo aqui mesmo."),
                "journal": {
                    "title": "Ferro no afloramento",
                    "text": ("Há um veio raso de ferro na base do Afloramento de Cobre. Pobre, mas suficiente para "
                             "começar a forjar ferro na bigorna do Brom."),
                },
            },
        },
        {
            "id": "fonte_termal", "name": "Fonte Termal", "x": 55, "y": 18, "xp": 30,
            "hint": "Vapor sobe de algum lugar ao {direcao}.",
            "description": ("Entre rochas vermelhas, uma fonte de água quente forma uma piscina natural fumegante, "
                            "cercada de musgo e de flores que não deveriam crescer nesta altitude. A água tem um "
                            "leve cheiro mineral e é deliciosamente morna."),
            "night": ("O vapor da fonte sobe em espirais prateadas sob a lua. Há algo de mágico em mergulhar os "
                      "pés aqui enquanto o resto do vale dorme."),
            "examine": ("No fundo da fonte, pedras lisas formam um mosaico desbotado: uma figura alta, de braços "
                        "abertos, segurando três luas. Quem construiu as ruínas também esteve aqui."),
            "resources": [{"node": "orquideas_termais"}],
        },
        {
            "id": "mina_ferro_velho", "name": "Mina de Ferro-Velho", "x": 53, "y": 12, "xp": 45,
            "hint": "Um eco metálico vem de algum lugar ao {direcao}.",
            "description": ("A entrada da velha mina de ferro é um buraco escorado por vigas negras de fuligem, com "
                            "trilhos de vagonete sumindo na escuridão. Uma placa caída diz \"MINA DE FERRO-VELHO "
                            "— CONCESSÃO DO VALE\". Há marcas de pequenos pés descalços na poeira."),
            "night": ("Da boca da mina vem um cântico baixo e ritmado, em vozes agudas, acompanhado de batidas de "
                      "metal contra pedra. Uma luz de tochas dança lá no fundo."),
            "examine": ("As vigas da entrada foram marcadas com símbolos grosseiros, pintados com algo vermelho: "
                        "um olho dentro de um círculo, repetido muitas vezes. No chão, um capacete de mineiro "
                        "igual ao que está pendurado na forja da vila."),
        },
        # --- Ruínas de Vel'Tharas
        {
            "id": "portal_ruinas", "name": "Portal das Ruínas", "x": 47, "y": 7, "xp": 35,
            "hint": "Pedras brancas reluzem ao longe, ao {direcao}.",
            "description": ("Dois pilares de pedra branca, ainda de pé, marcam a antiga entrada do templo de "
                            "Vel'Tharas. O arco que os unia jaz partido no chão, coberto de luas entalhadas em "
                            "todas as fases. Além dele, colunas tombadas e muros arruinados seguem para o norte."),
            "night": ("Os pilares emitem um brilho violeta fraco. Ao atravessá-los, você sente um arrepio — como "
                      "passar por uma cortina de água fria."),
            "examine": ("No pilar da esquerda, uma inscrição meio apagada: \"...entra quem traz a luz das três... "
                        "o Vigia guarda... o sono do Primordial...\" O resto foi arrancado a golpes, e as marcas "
                        "parecem recentes."),
        },
        {
            "id": "circulo_runas", "name": "Círculo de Pedras Rúnicas", "x": 50, "y": 4, "xp": 45,
            "description": ("No centro das ruínas, pedras verticais formam um círculo perfeito em volta de um disco "
                            "de pedra no chão. Cada pedra tem uma runa diferente, e o disco mostra uma lua cheia "
                            "rodeada por uma serpente que morde a própria cauda."),
            "night": ("As runas brilham em violeta, uma de cada vez, numa sequência que se repete. O ar no centro "
                      "do círculo é morno, e um zumbido grave sobe do subsolo."),
            "examine": ("O disco central tem uma rachadura recente, de onde escapa um ar quente com cheiro de "
                        "tempestade. Você encosta a mão na pedra e sente: lá embaixo, muito fundo, algo está "
                        "acordando."),
        },
        {
            "id": "altar_rachado", "name": "Altar Rachado", "x": 54, "y": 3, "xp": 40,
            "description": ("Sobre uma plataforma de degraus quebrados, um altar de pedra branca foi partido ao "
                            "meio por uma rachadura que desce até o chão. Na superfície, uma concavidade em forma "
                            "de lua crescente — vazia — e restos de velas derretidas, algumas recentes."),
            "night": ("Velas violetas que ninguém acendeu queimam sobre o altar, sem vento que as apague. A "
                      "concavidade em forma de lua parece esperar alguma coisa."),
            "examine": ("A cera das velas recentes é violeta e cheira a enxofre — a mesma cor da luz que dizem "
                        "dançar sobre as ruínas. Alguém tem vindo aqui. Na rachadura do altar, um pedaço de "
                        "tecido negro ficou preso numa farpa de pedra."),
        },
        {
            "id": "torre_tombada", "name": "Torre Tombada", "x": 48, "y": 1, "xp": 35, "reveal": 7,
            "description": ("Os restos de uma torre de observação desabaram contra a encosta da montanha. Subindo "
                            "pelos blocos caídos, você chega a uma plataforma de onde se vê todo o norte do "
                            "vale."),
            "night": ("Do alto da Torre Tombada, o céu noturno é um oceano de estrelas. É fácil imaginar os "
                      "antigos de Vel'Tharas aqui, estudando a lua."),
            "examine": ("Gravado no parapeito, um mapa celeste mostra a lua em oito fases, com a lua cheia "
                        "marcada por um olho aberto. Abaixo: \"Quando o olho se abre, o caminho se revela.\""),
        },
        # --- Lago Espelhado
        {
            "id": "pier_lago", "name": "Píer do Lago Espelhado", "x": 41, "y": 22, "xp": 25,
            "description": ("Um píer de madeira avança sobre o lago, com um barquinho furado amarrado e uma cadeira "
                            "de vime gasta na ponta. Redes secam ao sol, e um balde de iscas cheira a minhoca e "
                            "esperança."),
            "night": ("O píer está vazio, as redes recolhidas. A água negra bate de leve nas estacas, e a ilhota "
                      "no centro do lago é só uma sombra contra o reflexo da lua."),
            "examine": ("Na cadeira de vime, marcas de peixes pescados: dezenas de risquinhos e, em destaque, o "
                        "desenho de um peixe enorme usando uma coroa. Embaixo: \"O Rei do Lago existe. — A.\""),
            "resources": [{"node": "cardume_camaroes"}, {"node": "cardume_sardinhas"}],
        },
        {
            "id": "torre_vigia", "name": "Torre de Vigia em Ruínas", "x": 52, "y": 22, "xp": 40, "reveal": 9,
            "hint": "Uma torre escura se recorta contra o céu, ao {direcao}.",
            "description": ("Uma torre de vigia de pedra escura, metade desmoronada, ergue-se na margem leste do "
                            "lago. A escada em espiral ainda permite subir até o andar de cima, de onde se vigia "
                            "todo o sul do vale."),
            "night": ("Do alto da torre, você vê as luzes da vila, a fogueira do Portão Sul e o reflexo da lua no "
                      "lago. Algo se move na água, rumo à ilhota."),
            "examine": ("As pedras desta torre são escuras e grosseiras — obra humana. Uma placa diz: \"Torre do "
                        "Lago, erguida no ano 412 da Era das Brasas para vigiar o que dorme sob o vale.\" "
                        "Vigiar o quê, exatamente, a placa não diz."),
        },
        # --- Caminho do Sul
        {
            "id": "ponte_pedra", "name": "Ponte de Pedra Velha", "x": 30, "y": 21, "xp": 15,
            "description": ("Uma ponte de pedra em arco único cruza o Ribeirão Prateado, tão antiga que o musgo "
                            "virou parte da alvenaria. Crianças se penduram no parapeito para ver os peixes; os "
                            "mais velhos dizem que a ponte já estava aqui quando a vila foi fundada."),
            "night": ("A ponte está deserta. O ribeirão murmura sob o arco escuro, e as pedras do parapeito estão "
                      "frias e úmidas de sereno."),
            "examine": ("Na pedra-chave do arco, quase apagada, há uma lua crescente entalhada. A ponte, como o "
                        "poço da vila, foi construída com a mesma pedra branca das ruínas."),
        },
        {
            "id": "portao_sul", "name": "Portão Sul do Vale", "x": 30, "y": 29, "xp": 25,
            "description": ("A Estrada Real passa entre duas encostas íngremes e chega a uma guarita com cancela: o "
                            "Portão Sul do Vale. Além dela, a Rota dos Mercadores desce rumo à capital, Alvorada. "
                            "Hoje a cancela está baixada, e uma barricada de carroças bloqueia o caminho."),
            "night": ("Uma fogueira arde junto à barricada. Dois guardas sonolentos vigiam a escuridão da "
                      "estrada, lanças em punho, assustando-se com cada pio de coruja."),
            "examine": ("Pregado na cancela, um aviso oficial: \"ROTA DOS MERCADORES INTERDITADA. O Bando do Corvo "
                        "ataca caravanas entre o vale e Alvorada. Por ordem da Capitã Renna Valbrand, ninguém "
                        "passa.\" Alguém desenhou um corvo embaixo — e riscou um X sobre ele."),
        },
    ],
    # ------------------------------------------------------------------ passagens
    "portals": [
        {
            "id": "passo_norte_saida", "x": 40, "y": 0, "direction": "n", "label": "Passo do Norte",
            "locked": True,
            "locked_text": ("Você escala as primeiras pedras do deslizamento, mas logo percebe que é impossível: "
                            "os blocos são do tamanho de casas, e qualquer passo em falso provoca uma nova "
                            "avalanche. O caminho para Pedravale está fechado — por enquanto."),
        },
        {
            "id": "portao_sul_saida", "x": 30, "y": 29, "direction": "s", "label": "Rota dos Mercadores",
            "locked": True,
            "locked_text": ("Um dos guardas ergue a lança e balança a cabeça: \"Ninguém passa, ordens da Capitã. O "
                            "Bando do Corvo está na estrada. Quando a rota for liberada, você será a primeira "
                            "pessoa a saber.\""),
        },
        {
            "id": "mina_entrada", "x": 53, "y": 12, "verb": "entrar", "label": "Mina de Ferro-Velho",
            "locked": True,
            "locked_text": ("Você dá alguns passos para dentro da mina, e o cântico agudo lá no fundo para de "
                            "repente. Dezenas de olhinhos brilham na escuridão. Sem companhia, sem preparo e sem "
                            "saber o que enfrenta, avançar seria loucura. Melhor voltar com mais experiência."),
        },
        {
            "id": "toca_lobos_entrada", "x": 3, "y": 15, "verb": "entrar", "label": "Toca dos Lobos",
            "target": ("toca_dos_lobos", 4, 13), "min_level": 4,
            "locked_text": ("Você se agacha para entrar e um rosnado grave vem do escuro. Dois olhos azuis como "
                            "gelo — muito acima de onde deveriam estar os olhos de um lobo — se acendem lá no "
                            "fundo. Seu instinto grita para recuar. Ainda não. (Recomendado: nível 4 ou mais.)"),
            "travel_text": ("Você se abaixa e entra na toca. O cheiro de fera e de carne velha é sufocante, e o ar "
                            "fica mais frio a cada passo."),
        },
        {
            "id": "gruta_entrada", "x": 23, "y": 3, "verb": "entrar", "label": "Gruta atrás do Véu",
            "target": ("gruta_veu_prata", 4, 8), "requires_flag": "segredo_cachoeira",
            "travel_text": ("Você respira fundo, cola o corpo à rocha e atravessa o vão atrás da cortina d'água. O "
                            "rugido da cachoeira fica abafado, e a luz do dia se transforma num brilho azulado..."),
        },
    ],
}
