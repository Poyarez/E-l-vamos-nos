"""Perícias de coleta e produção (estilo Old School RuneScape).

Cada perícia evolui de 1 a 99 de forma independente do nível de combate.
A ordem do dicionário é a ordem de exibição na tela de perícias.
"""

SKILLS = {
    "mineracao": {
        "name": "Mineração",
        "kind": "coleta",
        "color": "yellow",
        "description": "Arranque minérios e gemas das rochas. Alimenta a Metalurgia.",
    },
    "metalurgia": {
        "name": "Metalurgia",
        "kind": "produção",
        "color": "bright_red",
        "description": "Funda barras na fornalha e forje armas e armaduras na bigorna.",
    },
    "pesca": {
        "name": "Pesca",
        "kind": "coleta",
        "color": "bright_cyan",
        "description": "Rios, lagos e mares escondem peixes cada vez mais raros. Alimenta a Culinária.",
    },
    "culinaria": {
        "name": "Culinária",
        "kind": "produção",
        "color": "bright_yellow",
        "description": "Transforme peixes e carnes em pratos que restauram vida e concedem bônus.",
    },
    "alfaiataria": {
        "name": "Alfaiataria",
        "kind": "produção",
        "color": "magenta",
        "description": "Costure linho, lã e seda em mantos, bolsas e vestes encantáveis.",
    },
    "alquimia": {
        "name": "Alquimia",
        "kind": "produção",
        "color": "bright_green",
        "description": "Destile ervas e reagentes em poções, elixires e venenos.",
    },
}
