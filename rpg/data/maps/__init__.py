"""Registro de mapas. Para adicionar um mapa, crie o módulo e inclua-o em ``_MODULES``."""

from . import gruta_veu_prata, vale_primordia

_MODULES = (vale_primordia, gruta_veu_prata)

MAPS = {module.MAP["id"]: module.MAP for module in _MODULES}
