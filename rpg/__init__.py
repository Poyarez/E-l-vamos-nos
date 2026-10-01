"""Crônicas de Primórdia — um RPG de fantasia medieval para o terminal.

Organização do pacote:

* ``rpg.data``  — o "banco de dados" do jogo: classes, itens, terrenos, mapas e NPCs
  descritos como dicionários puros (fáceis de expandir sem mexer na lógica).
* módulos de regra (``player``, ``world``, ``npcs``, ``skills``...) — transformam esses
  dados em objetos (padrão fábrica) e implementam as mecânicas.
* módulos de interface (``ui``, ``screens``, ``mapview``, ``commands``) — tudo o que
  desenha na tela ou interpreta comandos.
"""

__all__ = ["__version__"]

__version__ = "0.3.0"
