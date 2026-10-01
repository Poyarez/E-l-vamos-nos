"""Persistência: salvar, carregar, cópia de segurança e listagem de saves."""

import json
import unittest

from rpg import save_system
from rpg.save_system import SAVE_VERSION, SaveError
from rpg.state import GameState
from tests.helpers import TempSaveDirMixin, make_session


class SaveSystemTest(TempSaveDirMixin):
    def test_roundtrip_preserves_progress(self):
        session = make_session()
        session.walk("n", 3)
        session.state.flags["segredo_cachoeira"] = True
        session.add_journal("teste", "Título", "Texto")
        path = session.save()
        loaded = save_system.load_game(path)
        self.assertEqual(loaded.to_dict(), session.state.to_dict())
        self.assertEqual(loaded.pos, (30, 15))
        self.assertIn((30, 12), loaded.explored_on("vale_primordia"))

    def test_listing_and_deleting(self):
        first, second = make_session(name="Alfa"), make_session(name="Beta")
        first.save()
        second.save()
        infos = save_system.list_saves()
        self.assertEqual(sorted(info.name for info in infos), ["Alfa", "Beta"])
        self.assertTrue(all(info.class_name == "Guerreira" for info in infos))
        save_system.delete_save(infos[0].path)
        self.assertEqual(len(save_system.list_saves()), 1)

    def test_backup_is_used_when_save_is_damaged(self):
        session = make_session()
        path = session.save()
        session.walk("n")
        session.save()                          # o save anterior vira .bak
        path.write_text("{ isto não é json", encoding="utf-8")
        loaded = save_system.load_game(path)
        self.assertEqual(loaded.pos, (30, 18))  # recuperado da cópia de segurança
        self.assertTrue(save_system.list_saves()[0].damaged)

    def test_damaged_without_backup_raises(self):
        session = make_session()
        path = session.save()
        path.write_text("lixo", encoding="utf-8")
        with self.assertRaises(SaveError):
            save_system.load_game(path)

    def test_newer_version_is_rejected(self):
        path = make_session().save()
        data = json.loads(path.read_text(encoding="utf-8"))
        data["version"] = SAVE_VERSION + 1
        path.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(SaveError):
            save_system.load_game(path)

    def test_invalid_location_falls_back_to_start(self):
        data = make_session().state.to_dict()
        data["location"] = {"map": "mapa_que_nao_existe", "x": 1, "y": 1}
        state = GameState.from_dict(data)
        self.assertEqual((state.map_id, state.pos), ("vale_primordia", (30, 18)))


if __name__ == "__main__":
    unittest.main()
