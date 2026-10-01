"""Lojas. O preço de compra é o valor do item vezes ``markup``; a venda paga o valor do item.

Cada loja pertence a um NPC (``"shop": "<id>"`` em ``rpg.data.npcs``), que a abre num nó
de diálogo com o efeito ``open_shop``.
"""

SHOPS = {
    "graca": {
        "name": "Barraca da Dona Graça",
        "markup": 4,
        "stock": ["pao_de_viagem", "cantil_agua", "tocha", "farinha", "frasco_vazio", "kit_costura",
                  "tesoura_tosquia", "pocao_cura_menor", "pocao_mana_menor", "pocao_cura"],
    },
    "brom": {
        "name": "Forja do Martelo Rubro",
        "markup": 4,
        "stock": ["martelo_ferreiro", "picareta_bronze", "barra_bronze", "adaga_bronze", "machadinha_bronze",
                  "maca_bronze", "espada_bronze", "elmo_bronze", "escudo_bronze", "cota_bronze"],
    },
    "anselmo": {
        "name": "Tralha de Pesca do Anselmo",
        "markup": 3,
        "stock": ["rede_pesca", "vara_pesca", "isca_minhoca"],
    },
    "brigida": {
        "name": "Prateleiras da Mãe Brígida",
        "markup": 4,
        "stock": ["almofariz", "frasco_vazio", "pocao_cura_menor", "pocao_mana_menor", "elixir_javali"],
    },
    "tobias": {
        "name": "Moinho do Velho Tobias",
        "markup": 3,
        "stock": ["farinha", "pao_de_viagem"],
    },
    "zahir": {
        "name": "Carroças de Zahir",
        "markup": 5,
        "stock": ["especiarias", "bolsa_linho", "fio_seda", "picareta_ferro", "oleo_inflamavel"],
    },
}
