"""Slug del nodo e guardia contro i nodi fantasma di chiudi.py.

Run: python3 -m unittest discover -s skills/chiudi-task/tests
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import chiudi  # noqa: E402


def _git_init(path):
    os.makedirs(path, exist_ok=True)
    subprocess.run(["git", "init", "-q", path], check=True)


class SlugNodo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_dotted_basename_loses_the_dot(self):
        repo = os.path.join(self.base, ".nascosto")
        _git_init(repo)
        self.assertEqual(chiudi._slug_nodo(repo), "nascosto")

    def test_node_config_slug_wins(self):
        repo = os.path.join(self.base, "Some_Repo")
        _git_init(repo)
        with open(os.path.join(repo, "node.config"), "w") as fh:
            json.dump({"slug": "someRepo"}, fh)
        self.assertEqual(chiudi._slug_nodo(repo), "someRepo")


class GhostNodeGuard(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = self.tmp.name
        # Layout tree: <tree>/life.graph.json + <tree>/brain/nodi/
        istanza = os.path.join(base, "life-test")
        self.brain = os.path.join(istanza, "brain")
        os.makedirs(os.path.join(self.brain, "nodi", "legacy-folder"))
        with open(os.path.join(istanza, "life.graph.json"), "w") as fh:
            json.dump({"nodes": {"alpha": {"id": "alpha"}}}, fh)
        # Grafo del framework in un finto checkout di Life.
        dati = os.path.join(base, "Life", "shell", "src", "data")
        os.makedirs(dati)
        with open(os.path.join(dati, "life.graph.default.json"), "w") as fh:
            json.dump({"nodes": [{"id": "llm"}, {"id": "system"}]}, fh)
        self.env = mock.patch.dict(os.environ, {
            "LIFE_INSTANCE_DIR": istanza,
            "LIFE_FRAMEWORK_DIR": os.path.join(base, "Life"),
        })
        self.env.start()
        self.resoconto = os.path.join(base, "resoconto.md")
        with open(self.resoconto, "w") as fh:
            fh.write("# Resoconto\n\nCloses #1\n")
        self.base = base

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_known_nodes_come_from_all_three_sources(self):
        noti = chiudi._nodi_noti(self.brain)
        self.assertTrue({"legacy-folder", "alpha", "llm", "system"} <= noti)

    def test_unknown_node_is_not_created(self):
        repo = os.path.join(self.base, "NotANode")
        _git_init(repo)
        esito = chiudi.porta_nel_brain(self.resoconto, repo)
        self.assertIn("non depositata", esito)
        self.assertFalse(os.path.exists(os.path.join(self.brain, "nodi", "notanode")))

    def test_known_node_gets_the_note_with_frontmatter(self):
        repo = os.path.join(self.base, "Alpha")
        _git_init(repo)
        with open(os.path.join(repo, "node.config"), "w") as fh:
            json.dump({"slug": "alpha"}, fh)
        with mock.patch.object(chiudi, "_rigenera_indice", return_value=(False, "indice non rigenerato (test)")):
            esito = chiudi.porta_nel_brain(self.resoconto, repo)
        cartella = os.path.join(self.brain, "nodi", "alpha", "chiusure")
        note = os.listdir(cartella)
        self.assertEqual(len(note), 1)
        self.assertTrue(note[0].endswith("-1.md"))
        with open(os.path.join(cartella, note[0]), encoding="utf-8") as fh:
            self.assertTrue(fh.read().startswith("---\ntitle:"))
        self.assertIn("brain:", esito)

    def test_no_brain_is_said_not_raised(self):
        with mock.patch.object(chiudi, "_brain_istanza", return_value=None):
            esito = chiudi.porta_nel_brain(self.resoconto, self.base)
        self.assertIn("nota non depositata", esito)


if __name__ == "__main__":
    unittest.main()
