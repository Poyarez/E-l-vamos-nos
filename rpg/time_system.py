"""Passagem do tempo: dias, períodos do dia, clima e fases da lua.

Cada ação custa minutos de jogo (andar pela estrada é mais rápido que atravessar o
pântano). O clima de cada dia é sorteado de forma determinística a partir da semente
do mundo, então salvar e carregar nunca muda o tempo que está fazendo.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional

MINUTES_PER_DAY = 24 * 60
START_MINUTES = 8 * 60          # o Dia 1 começa às 08:00
DAWN_HOUR = 6                   # hora em que um novo dia "amanhece" (autosave)

#: (id, hora de início, nome). Ordenado pela hora.
PERIODS = (
    ("madrugada", 0, "Madrugada"),
    ("amanhecer", 5, "Amanhecer"),
    ("manha", 7, "Manhã"),
    ("tarde", 12, "Tarde"),
    ("entardecer", 18, "Entardecer"),
    ("noite", 20, "Noite"),
)
NIGHT_PERIODS = {"noite", "madrugada"}
TWILIGHT_PERIODS = {"amanhecer", "entardecer"}

WEATHER = {
    "limpo": {
        "name": "Céu limpo", "weight": 36, "vision": 0,
        "day": ["O céu está limpo e azul.", "O sol brilha num céu sem nuvens."],
        "night": ["O céu está limpo e estrelado.", "Milhares de estrelas cobrem o céu."],
    },
    "nublado": {
        "name": "Nublado", "weight": 26, "vision": 0,
        "day": ["Nuvens cinzentas passam devagar, escondendo o sol.", "Um céu de chumbo pesa sobre o vale."],
        "night": ["Nuvens cobrem as estrelas; a noite é mais escura que de costume."],
    },
    "chuva": {
        "name": "Chuva", "weight": 18, "vision": 0,
        "day": ["Uma chuva fina e insistente encharca suas roupas.", "Gotas grossas tamborilam ao seu redor."],
        "night": ["A chuva fria da noite escorre pela sua nuca.", "A chuva apaga todos os sons, menos o dela."],
    },
    "neblina": {
        "name": "Neblina", "weight": 12, "vision": -1,
        "day": ["Uma neblina espessa reduz o mundo a poucos passos.", "A névoa engole as formas ao redor."],
        "night": ["A neblina noturna é tão densa que você mal enxerga as próprias mãos."],
    },
    "tempestade": {
        "name": "Tempestade", "weight": 8, "vision": -1,
        "day": ["Trovões rolam sobre as montanhas, e o vento chicoteia a chuva de lado.",
                "Relâmpagos rasgam o céu escuro do meio-dia."],
        "night": ["Relâmpagos iluminam o vale por instantes, revelando formas que somem no escuro.",
                  "A tempestade uiva; cada trovão faz o chão vibrar."],
    },
}

MOON_PHASES = (
    "Lua nova", "Lua crescente", "Quarto crescente", "Gibosa crescente",
    "Lua cheia", "Gibosa minguante", "Quarto minguante", "Lua minguante",
)


@dataclass
class TimeChange:
    """O que aconteceu durante um avanço de tempo."""

    dawns: int = 0                       # quantos amanheceres (06:00) foram cruzados
    period_changed: Optional[str] = None # novo período, se mudou


class GameClock:
    def __init__(self, minutes: int = START_MINUTES, seed: int = 0) -> None:
        self.minutes = max(0, int(minutes))
        self.seed = int(seed)

    # ------------------------------------------------------------------ leitura

    @property
    def day(self) -> int:
        return self.minutes // MINUTES_PER_DAY + 1

    @property
    def minute_of_day(self) -> int:
        return self.minutes % MINUTES_PER_DAY

    @property
    def hour(self) -> int:
        return self.minute_of_day // 60

    @property
    def time_str(self) -> str:
        return f"{self.hour:02d}:{self.minute_of_day % 60:02d}"

    @property
    def period(self) -> str:
        current = PERIODS[0][0]
        for period_id, start_hour, _name in PERIODS:
            if self.hour >= start_hour:
                current = period_id
        return current

    @property
    def period_name(self) -> str:
        return next(name for period_id, _hour, name in PERIODS if period_id == self.period)

    @property
    def is_night(self) -> bool:
        return self.period in NIGHT_PERIODS

    @property
    def is_twilight(self) -> bool:
        return self.period in TWILIGHT_PERIODS

    def weather_id(self, day: Optional[int] = None) -> str:
        """Clima do dia (determinístico para a semente do mundo)."""
        rng = random.Random(self.seed * 7919 + (day or self.day))
        ids = list(WEATHER)
        return rng.choices(ids, weights=[WEATHER[w]["weight"] for w in ids])[0]

    @property
    def weather(self) -> Dict[str, Any]:
        return WEATHER[self.weather_id()]

    @property
    def moon_phase(self) -> str:
        return MOON_PHASES[(self.day - 1 + self.seed) % len(MOON_PHASES)]

    # ------------------------------------------------------------------ avanço

    def advance(self, minutes: int) -> TimeChange:
        before_period = self.period
        before_dawn_index = (self.minutes - DAWN_HOUR * 60) // MINUTES_PER_DAY
        self.minutes += max(0, int(minutes))
        after_dawn_index = (self.minutes - DAWN_HOUR * 60) // MINUTES_PER_DAY
        change = TimeChange(dawns=after_dawn_index - before_dawn_index)
        if self.period != before_period or change.dawns:
            change.period_changed = self.period
        return change

    def minutes_until(self, hour: int) -> int:
        """Minutos até a próxima vez em que o relógio marcar ``hour``:00."""
        target = hour * 60
        delta = (target - self.minute_of_day) % MINUTES_PER_DAY
        return delta or MINUTES_PER_DAY

    # ------------------------------------------------------------------ persistência

    def to_dict(self) -> Dict[str, int]:
        return {"minutes": self.minutes, "seed": self.seed}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "GameClock":
        return cls(int(data.get("minutes", START_MINUTES)), int(data.get("seed", 0)))
