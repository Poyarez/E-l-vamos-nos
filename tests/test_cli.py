"""Teste de ponta a ponta: executa ``main.py`` como o jogador faria, com entradas roteirizadas."""

import os
import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import TempSaveDirMixin

ROOT = Path(__file__).resolve().parent.parent


class MainScriptTest(TempSaveDirMixin):
    def play(self, *lines: str) -> subprocess.CompletedProcess:
        env = {**os.environ, "PRIMORDIA_SAVE_DIR": self._tmp.name, "PYTHONIOENCODING": "utf-8"}
        return subprocess.run([sys.executable, str(ROOT / "main.py")], input="\n".join(lines) + "\n",
                              capture_output=True, text=True, encoding="utf-8", env=env, timeout=60)

    def test_new_game_explore_save_and_continue(self):
        result = self.play(
            "1",                      # menu: novo jogo
            "1",                      # criar passo a passo
            "Tália", "2",             # nome, gênero
            "2", "s",                 # classe: Maga
            "4", "1",                 # cabelo e cor
            "1", "3", "5",            # traço, armadura, alinhamento
            "1", "",                  # confirmar; prólogo
            "n 3", "falar", "1", "4", # anda até a praça e conversa com o bardo
            "mapa", "", "ficha", "", "examinar", "salvar",
            "menu",                   # volta ao menu (já salvo, então não pergunta)
            "6",                      # sair
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertIn("PRÓLOGO", result.stdout)
        self.assertIn("Lírio", result.stdout)
        self.assertIn("Jogo salvo", result.stdout)

        again = self.play("1", "", "6")   # "Continuar" agora é a primeira opção
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertIn("Que bom ver você de volta, Tália!", again.stdout)
        self.assertIn("Maga nível 1", again.stdout)

    def test_input_ending_mid_game_exits_cleanly(self):
        result = self.play("1", "2", "1", "")     # personagem sorteado e prólogo; a entrada acaba
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Até a próxima aventura!", result.stdout)


if __name__ == "__main__":
    unittest.main()
