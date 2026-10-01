"""Pontos de coleta (lógica em ``rpg.crafting``).

Cada tipo de ponto diz qual perícia usa, o nível mínimo, o item colhido e a experiência
por item (em unidades do OSRS; ``rpg.crafting.SKILL_XP_RATE`` multiplica). Os locais dos
mapas apontam para estes tipos em ``resources``: ``{"node": "veio_cobre"}``, com um
``if`` opcional (condições de ``rpg.conditions``) para pontos revelados por segredos.

Campos:

* ``tool`` — tipo de ferramenta exigido (``picareta``, ``rede``, ``vara``, ``tesoura``);
  ``bait`` — isca gasta a cada peixe fisgado;
* ``chance`` — chance de sucesso por tentativa no nível mínimo (cresce 1,2% por nível
  acima dele, mais o ``power`` da ferramenta);
* ``minutes`` — tempo de jogo de cada tentativa;
* ``amount`` e ``respawn`` — quantos itens o ponto rende antes de se esgotar e em quantos
  minutos se recupera por completo (aos poucos, como no OSRS);
* ``rare`` — achados raros por item colhido: ``[item, chance]`` ou ``[item, chance, nível mínimo]``;
* ``if`` / ``closed`` — quando o ponto pode ser usado (ex.: só à noite) e o aviso fora disso.
"""

NODES = {
    # ------------------------------------------------------------------ mineração
    "veio_cobre": {
        "name": "Veio de Cobre", "skill": "mineracao", "level": 1, "item": "minerio_cobre", "xp": 17.5,
        "tool": "picareta", "chance": 0.5, "minutes": 3, "amount": 8, "respawn": 120,
        "rare": [["granada_bruta", 0.02]],
        "verb": "Você golpeia a rocha esverdeada com a picareta.",
    },
    "veio_estanho": {
        "name": "Veio de Estanho", "skill": "mineracao", "level": 1, "item": "minerio_estanho", "xp": 17.5,
        "tool": "picareta", "chance": 0.5, "minutes": 3, "amount": 8, "respawn": 120,
        "rare": [["granada_bruta", 0.02]],
        "verb": "Você arranca lascas cinzentas do veio de estanho.",
    },
    "veio_ferro": {
        "name": "Veio de Ferro Raso", "skill": "mineracao", "level": 15, "item": "minerio_ferro", "xp": 35,
        "tool": "picareta", "chance": 0.42, "minutes": 4, "amount": 5, "respawn": 240,
        "rare": [["granada_bruta", 0.03]],
        "verb": "Você trabalha a rocha avermelhada, cuidando para não perder o veio fino.",
    },
    "veio_prata": {
        "name": "Veio de Prata", "skill": "mineracao", "level": 20, "item": "minerio_prata", "xp": 40,
        "tool": "picareta", "chance": 0.38, "minutes": 4, "amount": 5, "respawn": 300,
        "rare": [["granada_bruta", 0.04]],
        "verb": "A picareta tilinta contra a prata, e o eco corre a gruta inteira.",
    },
    "veio_ferro_bom": {
        "name": "Veio de Ferro", "skill": "mineracao", "level": 15, "item": "minerio_ferro", "xp": 35,
        "tool": "picareta", "chance": 0.48, "minutes": 4, "amount": 10, "respawn": 180,
        "rare": [["granada_bruta", 0.03]],
        "verb": "Você ataca o veio largo e vermelho que deu nome à mina.",
    },
    "veio_carvao": {
        "name": "Veio de Carvão", "skill": "mineracao", "level": 30, "item": "carvao", "xp": 50,
        "tool": "picareta", "chance": 0.42, "minutes": 4, "amount": 8, "respawn": 240,
        "rare": [["granada_bruta", 0.02]],
        "verb": "Pó negro sobe a cada golpe. Você tosse, mas o carvão vem.",
    },
    "cristais_eco": {
        "name": "Cristais-de-eco", "skill": "mineracao", "level": 40, "item": "cristal_eco", "xp": 80,
        "tool": "picareta", "chance": 0.25, "minutes": 6, "amount": 3, "respawn": 720,
        "verb": "Você bate de leve, no ponto certo, e o cristal canta ao se soltar.",
    },
    # ------------------------------------------------------------------ pesca
    "cardume_camaroes": {
        "name": "Cardume de Camarões", "skill": "pesca", "level": 1, "item": "camarao_cru", "xp": 10,
        "tool": "rede", "chance": 0.55, "minutes": 2, "amount": 15, "respawn": 90,
        "rare": [["bota_velha", 0.03]],
        "verb": "Você lança a rede rente à margem.",
    },
    "cardume_sardinhas": {
        "name": "Cardume de Sardinhas", "skill": "pesca", "level": 5, "item": "sardinha_crua", "xp": 20,
        "tool": "vara", "bait": "isca_minhoca", "chance": 0.5, "minutes": 3, "amount": 12, "respawn": 120,
        "rare": [["bota_velha", 0.03]],
        "verb": "Você espeta uma minhoca no anzol e lança a linha.",
    },
    "cardume_trutas": {
        "name": "Cardume de Trutas", "skill": "pesca", "level": 10, "item": "truta_crua", "xp": 50,
        "tool": "vara", "bait": "pena_corvo", "chance": 0.45, "minutes": 3, "amount": 10, "respawn": 150,
        "verb": "Você amarra uma pena de corvo no anzol e faz a mosca dançar na correnteza.",
    },
    "cardume_salmoes": {
        "name": "Cardume de Salmões", "skill": "pesca", "level": 25, "item": "salmao_cru", "xp": 70,
        "tool": "vara", "bait": "pena_corvo", "chance": 0.4, "minutes": 4, "amount": 8, "respawn": 180,
        "verb": "Você lança a mosca rio acima, onde os salmões saltam contra a corrente.",
    },
    "cardume_peixe_cego": {
        "name": "Peixes-cegos", "skill": "pesca", "level": 30, "item": "peixe_cego_cru", "xp": 85,
        "tool": "vara", "bait": "isca_minhoca", "chance": 0.35, "minutes": 4, "amount": 6, "respawn": 300,
        "verb": "Você desce a linha devagar na água negra e imóvel do lago subterrâneo.",
    },
    "poco_do_rei": {
        "name": "Poço do Rei", "skill": "pesca", "level": 20, "item": "carpa_prateada", "xp": 60,
        "tool": "vara", "bait": "isca_minhoca", "chance": 0.42, "minutes": 4, "amount": 8, "respawn": 240,
        "rare": [["rei_do_lago", 0.04, 35], ["bota_velha", 0.02]],
        "verb": "Você deixa a isca descer até o fundo do poço, onde a água fica escura e parada.",
    },
    # ------------------------------------------------------------------ ervas (alquimia)
    "ervas_pantano": {
        "name": "Ervas do Pântano", "skill": "alquimia", "level": 1, "item": "folha_charco", "xp": 8,
        "chance": 0.7, "minutes": 2, "amount": 8, "respawn": 180,
        "verb": "Você colhe folhas-de-charco com a lama até os tornozelos.",
    },
    "cogumelos_lume": {
        "name": "Cogumelos-lume", "skill": "alquimia", "level": 10, "item": "cogumelo_lume", "xp": 15,
        "chance": 0.6, "minutes": 2, "amount": 6, "respawn": 240,
        "verb": "Você colhe os cogumelos com cuidado, sem quebrar os anéis.",
    },
    "flor_de_breu": {
        "name": "Flor-de-breu", "skill": "alquimia", "level": 15, "item": "flor_breu", "xp": 20,
        "chance": 0.55, "minutes": 3, "amount": 5, "respawn": 300,
        "verb": "Você corta as flores negras, que deixam os dedos melados de piche.",
    },
    "orquideas_termais": {
        "name": "Orquídeas-das-termas", "skill": "alquimia", "level": 20, "item": "orquidea_termal", "xp": 28,
        "chance": 0.5, "minutes": 3, "amount": 4, "respawn": 360,
        "verb": "Você se inclina sobre o vapor e colhe as orquídeas mornas.",
    },
    "musgo_prateado": {
        "name": "Musgo-prata", "skill": "alquimia", "level": 25, "item": "musgo_prata", "xp": 35,
        "chance": 0.5, "minutes": 3, "amount": 4, "respawn": 360,
        "verb": "Você raspa o musgo das pedras molhadas, escorregando um pouco.",
    },
    "lirios_da_lua": {
        "name": "Lírios-da-lua", "skill": "alquimia", "level": 30, "item": "lirio_lua", "xp": 45,
        "chance": 0.45, "minutes": 4, "amount": 3, "respawn": 720,
        "if": {"night": True}, "closed": "Os lírios-da-lua estão fechados. Eles só se abrem à noite.",
        "verb": "Você colhe um lírio aberto, e um pouco do luar parece vir junto.",
    },
    # ------------------------------------------------------------------ fibras (alfaiataria)
    "linhal": {
        "name": "Linhal", "skill": "alfaiataria", "level": 1, "item": "linho", "xp": 5,
        "chance": 0.8, "minutes": 2, "amount": 12, "respawn": 240,
        "verb": "Você arranca os talos de linho pela raiz, como os Moreira ensinam.",
    },
    "ovelhas": {
        "name": "Ovelhas do Curral", "skill": "alfaiataria", "level": 8, "item": "la_crua", "xp": 12,
        "tool": "tesoura", "chance": 0.6, "minutes": 4, "amount": 4, "respawn": 720,
        "verb": "Você segura uma ovelha entre os joelhos e tosquia com cuidado.",
    },
}

#: Nome da ação de coleta de cada perícia (para mensagens e comandos).
GATHER_VERBS = {"mineracao": "minerar", "pesca": "pescar", "alquimia": "colher", "alfaiataria": "colher"}
