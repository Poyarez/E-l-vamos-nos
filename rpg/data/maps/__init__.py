"""Registro de mapas. Para adicionar um mapa, crie o módulo e inclua-o em ``_MODULES``."""

from . import (camara_vigia, gruta_veu_prata, ilhota_garca, mina_ferro_velho, rota_mercadores, santuario_profano,
               toca_dos_lobos, vale_primordia)

_MODULES = (vale_primordia, gruta_veu_prata, toca_dos_lobos, mina_ferro_velho, ilhota_garca, santuario_profano,
            rota_mercadores, camara_vigia)

MAPS = {module.MAP["id"]: module.MAP for module in _MODULES}
