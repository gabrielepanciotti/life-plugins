"""Risoluzione del brain del tree di chiudi.py.

Una persona puo' avere piu' tree Life (`life-<id>`), ciascuno accanto al
framework: la chiusura di un nodo deve finire nel brain del Suo tree.

Run: python3 -m unittest discover -s skills/chiudi-task/tests
"""

import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import chiudi  # noqa: E402


class BrainIstanza(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = self.tmp.name
        self.env = mock.patch.dict(os.environ, {}, clear=False)
        self.env.start()
        os.environ.pop("LIFE_INSTANCE_DIR", None)

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def _bucket(self, nome, istanza):
        """<base>/<nome>/{life-<istanza>/brain, Nodo} - il layout reale."""
        bucket = os.path.join(self.base, nome)
        brain = os.path.join(bucket, f"life-{istanza}", "brain")
        os.makedirs(brain)
        nodo = os.path.join(bucket, "Nodo")
        os.makedirs(nodo)
        return nodo, brain

    def test_each_bucket_resolves_to_its_own_instance(self):
        nodo_a, brain_a = self._bucket("a", "alfa")
        nodo_b, brain_b = self._bucket("b", "beta")
        self.assertEqual(chiudi._brain_istanza(nodo_a), brain_a)
        self.assertEqual(chiudi._brain_istanza(nodo_b), brain_b)

    def test_explicit_selector_wins_over_the_layout(self):
        nodo_a, _ = self._bucket("a", "alfa")
        _, brain_b = self._bucket("b", "beta")
        os.environ["LIFE_INSTANCE_DIR"] = os.path.dirname(brain_b)
        self.assertEqual(chiudi._brain_istanza(nodo_a), brain_b)

    def test_no_instance_falls_back_to_brain_root_cli(self):
        orfano = os.path.join(self.base, "fuori-dai-bucket")
        os.makedirs(orfano)
        with mock.patch.object(chiudi, "_brain_root_cli", return_value="/brain/cli"):
            self.assertEqual(chiudi._brain_istanza(orfano), "/brain/cli")

    def test_two_instances_in_one_bucket_is_ambiguous_not_a_guess(self):
        bucket = os.path.join(self.base, "ambiguo")
        for i in ("uno", "due"):
            os.makedirs(os.path.join(bucket, f"life-{i}", "brain"))
        nodo = os.path.join(bucket, "Nodo")
        os.makedirs(nodo)
        with mock.patch.object(chiudi, "_brain_root_cli", return_value="/brain/cli"):
            self.assertEqual(chiudi._brain_istanza(nodo), "/brain/cli")

    def test_nothing_resolves_to_none(self):
        orfano = os.path.join(self.base, "solo")
        os.makedirs(orfano)
        with mock.patch.object(chiudi, "_brain_root_cli", return_value=None):
            self.assertIsNone(chiudi._brain_istanza(orfano))


if __name__ == "__main__":
    unittest.main()
