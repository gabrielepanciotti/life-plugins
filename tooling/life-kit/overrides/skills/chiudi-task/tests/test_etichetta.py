"""The brain note label must never come from another task.

The deposited filename is what people find when searching for an issue: if it
is taken from recent commits in a repo shared by multiple sessions, one task's
closure ends up labeled with another task's issue.

Run: python3 -m unittest discover -s skills/chiudi-task/tests
"""

import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import chiudi  # noqa: E402


class Etichetta(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.radice = self.tmp.name
        subprocess.run(["git", "init", "-q", self.radice], check=True)
        for k, v in (("user.email", "t@t"), ("user.name", "t")):
            subprocess.run(["git", "-C", self.radice, "config", k, v], check=True)
        # A commit from ANOTHER session, following the repo convention.
        with open(os.path.join(self.radice, "f.txt"), "w") as fh:
            fh.write("x")
        subprocess.run(["git", "-C", self.radice, "add", "f.txt"], check=True)
        subprocess.run(["git", "-C", self.radice, "commit", "-q", "-m",
                        "feat: roba di un altro\n\nCloses #15"], check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_non_prende_l_issue_dai_commit_di_altri(self):
        etichetta = chiudi._etichetta_issue(
            self.radice, "A report that does not close any issue.",
            percorso_resoconto="/x/.claude/chiusure/2026-09-21-audit-confini.md")
        self.assertEqual(etichetta, "audit-confini")

    def test_il_closes_del_proprio_resoconto_vince(self):
        etichetta = chiudi._etichetta_issue(
            self.radice, "Lavoro finito. Closes #42",
            percorso_resoconto="/x/.claude/chiusure/2026-09-21-audit-confini.md")
        self.assertEqual(etichetta, "42")

    def test_un_issue_solo_nominato_non_e_un_issue_chiuso(self):
        etichetta = chiudi._etichetta_issue(
            self.radice, "Restano aperti Altro#43 e Life#72.",
            percorso_resoconto="/x/.claude/chiusure/2026-09-21-audit-confini.md")
        self.assertEqual(etichetta, "audit-confini")

    def test_esplicita_batte_tutto(self):
        etichetta = chiudi._etichetta_issue(
            self.radice, "Closes #42", esplicita="7",
            percorso_resoconto="/x/.claude/chiusure/2026-09-21-audit-confini.md")
        self.assertEqual(etichetta, "7")


if __name__ == "__main__":
    unittest.main()
