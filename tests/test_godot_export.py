"""A versão Godot lê os dados exportados para JSON (``tools/export_godot_data.py``).

Se alguém mudar um mapa, item ou diálogo no Python e esquecer de exportar, o Godot
continuaria com a versão velha: este teste avisa.
"""

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("export_godot_data", ROOT / "tools" / "export_godot_data.py")
exporter = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(exporter)


class GodotExportTest(unittest.TestCase):
    def test_exported_json_is_up_to_date(self):
        stale = []
        for name, content in exporter.build().items():
            path = exporter.OUT_DIR / name
            if not path.exists() or path.read_text(encoding="utf-8") != exporter.render(content):
                stale.append(name)
        self.assertEqual(stale, [], "dados do Godot desatualizados: rode python tools/export_godot_data.py")

    def test_maps_keep_their_shape(self):
        index = json.loads((exporter.OUT_DIR / "maps" / "index.json").read_text(encoding="utf-8"))
        self.assertIn("vale_primordia", index)
        for map_id in index:
            data = json.loads((exporter.OUT_DIR / "maps" / f"{map_id}.json").read_text(encoding="utf-8"))
            rows = data["rows"]
            self.assertTrue(rows and all(len(row) == len(rows[0]) for row in rows), map_id)
            self.assertLessEqual({char for row in rows for char in row}, set(data["legend"]), map_id)


if __name__ == "__main__":
    unittest.main()
