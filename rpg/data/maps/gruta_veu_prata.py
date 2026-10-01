"""Gruta do Véu de Prata — mapa secreto atrás da cachoeira (16 x 9).

Legenda: # rocha   . chão da gruta   x cristais   ~ lago subterrâneo   & paredes entalhadas
         D porta selada
"""

MAP = {
    "id": "gruta_veu_prata",
    "name": "Gruta do Véu de Prata",
    "outdoor": False,
    "light": 2,
    "start": (4, 8),
    "legend": {
        "#": "parede_gruta", ".": "chao_gruta", "x": "cristais", "~": "lago_subterraneo",
        "&": "entalhes", "D": "porta_selada",
    },
    "layout": '''
################
##x..#####..x###
#x....###.....##
#..&..........D#
##....##~~~..###
###..###~~~.x###
####.###########
####.###########
####.###########
''',
    "regions": [
        {
            "id": "gruta_veu", "name": "Gruta do Véu de Prata", "rects": [(0, 0, 15, 8)], "xp": 60,
            "intro": ("Uma gruta escondida atrás da cachoeira, intocada há séculos. O ar é frio, úmido e "
                      "estranhamente perfumado, e cristais azulados iluminam o caminho."),
            "day": ["Gotas caem do teto e ecoam como sinos distantes.",
                    "O rugido da cachoeira chega aqui abafado, como uma respiração."],
        },
    ],
    "landmarks": [
        {
            "id": "atras_do_veu", "name": "Atrás do Véu", "x": 4, "y": 8, "xp": 20,
            "description": ("A cortina de água cai a um palmo do seu rosto, transformando o mundo lá fora num "
                            "borrão prateado. Degraus de pedra, gastos por pés que não passam aqui há séculos, "
                            "sobem para dentro da rocha."),
            "examine": ("Nos degraus, sob o musgo, há marcas de passos antigos — e um conjunto de pegadas "
                        "recentes, de botas, que sobem e não voltam a descer."),
        },
        {
            "id": "salao_cristais", "name": "Salão dos Cristais", "x": 2, "y": 2, "xp": 40,
            "description": ("Uma câmara alta onde cristais azuis brotam do chão e do teto como dentes de um animal "
                            "gigante, banhando tudo numa luz fria e suave. O som da cachoeira chega aqui como um "
                            "murmúrio, quase uma canção de ninar."),
            "examine": ("Os cristais vibram quando tocados, cada um numa nota diferente. Alguns, mais escuros e "
                        "densos, ecoam por muito tempo: cristais-de-eco, raríssimos, que só mãos muito "
                        "experientes em mineração conseguiriam extrair sem estilhaçar."),
            "resources": [{"node": "cristais_eco"}],
        },
        {
            "id": "mural_veltharas", "name": "Mural de Vel'Tharas", "x": 3, "y": 3, "xp": 40,
            "description": ("Uma parede inteira foi esculpida num relevo de tirar o fôlego: um gigante de pedra "
                            "deitado em sono profundo sob o vale, com rios e raízes atravessando seu corpo. Acima "
                            "dele, figuras de olhos grandes — o povo de Vel'Tharas — erguem três luas em oferenda."),
            "examine": ("O gigante adormecido do mural parece observar você. Agora você sabe o que os tremores "
                        "do vale significam."),
            "secret": {
                "flag": "lenda_primordial",
                "xp": 80,
                "text": ("Abaixo do relevo, uma inscrição em letras antigas: \"Aqui dorme o Primordial que deu "
                         "forma ao vale. Nós, os Vigias da Lua, guardamos seu sono. Se o sono se romper antes do "
                         "tempo, a terra tremerá, as feras enlouquecerão e o fogo violeta subirá das pedras.\" "
                         "Você pensa nos tremores, nos lobos, na luz das ruínas... e um calafrio percorre sua "
                         "espinha."),
                "journal": {
                    "title": "O sono do Primordial",
                    "text": ("Um mural na gruta da cachoeira revela que um ser Primordial dorme sob o vale, "
                             "guardado pelos antigos Vigias da Lua. Se despertar antes do tempo: tremores, feras "
                             "enlouquecidas e fogo violeta. Tudo isso já está acontecendo."),
                },
            },
        },
        {
            "id": "bau_esquecido", "name": "Baú Esquecido", "x": 11, "y": 1, "xp": 30,
            "description": ("Num nicho da parede, protegido da umidade, repousa um pequeno baú de madeira escura "
                            "com cantoneiras de prata, coberto de pó e teias. Não tem fechadura — apenas um fecho "
                            "em forma de lua."),
            "examine": ("O baú está vazio agora, mas o forro de veludo ainda guarda a marca do pingente — e de "
                        "outros dois objetos de mesmo formato que já não estão lá."),
            "loot": {
                "flag": "bau_gruta_aberto",
                "copper": 4500,
                "items": [["pingente_pedra_da_lua", 1]],
                "xp": 50,
                "text": ("Você abre o fecho em forma de lua. Dentro, sobre um forro de veludo apodrecido, há um "
                         "punhado de moedas antigas de prata e um pingente com uma pedra leitosa, que brilha em "
                         "resposta à sua presença."),
            },
        },
        {
            "id": "margem_lago_escuro", "name": "Margem do Lago Escuro", "x": 11, "y": 4, "xp": 30,
            "description": ("A gruta se abre sobre um lago subterrâneo de água negra e imóvel, que reflete os "
                            "cristais do teto como um céu estrelado. Às vezes, algo pálido passa sob a "
                            "superfície, rápido demais para os olhos."),
            "examine": ("Os peixes que vivem aqui são brancos como leite e não têm olhos: nunca precisaram. "
                        "Anselmo daria um braço para fisgar um desses."),
            "resources": [{"node": "cardume_peixe_cego"}],
        },
        {
            "id": "veio_prateado", "name": "Veio Prateado", "x": 12, "y": 5, "xp": 30,
            "description": ("No canto mais fundo da gruta, a parede é riscada por um veio de prata tão puro que "
                            "reflete a luz azul dos cristais como um espelho. Talvez seja daqui que a cachoeira "
                            "tirou o nome."),
            "examine": ("Ao redor do veio há marcas antigas de cinzel, pequenas e precisas. O povo de Vel'Tharas "
                        "também mineirava aqui — e sabia exatamente o que procurava."),
            "resources": [{"node": "veio_prata"}],
        },
        {
            "id": "porta_tres_luas", "name": "Porta Selada das Três Luas", "x": 13, "y": 3, "xp": 50,
            "description": ("A gruta termina numa porta de pedra lisa, sem fechadura nem dobradiças, que não se "
                            "move nem um milímetro. Três concavidades — lua crescente, cheia e minguante — foram "
                            "talhadas em seu centro, todas vazias."),
            "examine": ("Você encosta o ouvido na pedra. Do outro lado, muito ao longe, algo enorme respira — "
                        "uma vez a cada longo minuto. A concavidade crescente parece feita para encaixar uma "
                        "joia."),
        },
    ],
    "portals": [
        {
            "id": "gruta_saida", "x": 4, "y": 8, "direction": "s", "verb": "sair",
            "label": "Cachoeira do Véu de Prata", "target": ("vale_primordia", 23, 3),
            "travel_text": ("Você desce os degraus e atravessa a cortina d'água de volta à luz do vale, "
                            "encharcando-se da cabeça aos pés."),
        },
    ],
}
