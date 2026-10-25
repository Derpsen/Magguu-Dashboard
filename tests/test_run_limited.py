"""tools/run-limited.sh: hard limit, nice 19, nothing left behind (Marco rule 2026-10-25)."""
import pathlib
import subprocess
import unittest

SCRIPT = str(pathlib.Path(__file__).resolve().parents[1] / "tools" / "run-limited.sh")


def run(*args):
    return subprocess.run(["sh", SCRIPT, *args], capture_output=True, text=True, timeout=30)


def leftovers(marker):
    return subprocess.run(["pgrep", "-af", marker], capture_output=True, text=True).stdout.strip()


class RunLimitedTest(unittest.TestCase):
    def test_exit_code_and_bad_input(self):
        self.assertEqual(run("5", "true").returncode, 0)
        self.assertEqual(run("5", "sh", "-c", "exit 7").returncode, 7)
        self.assertEqual(run("0", "true").returncode, 2)
        self.assertEqual(run("abc", "true").returncode, 2)
        self.assertEqual(run("5").returncode, 2)

    def test_nice_19(self):
        r = run("5", "sh", "-c", "nice")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "19")

    def test_limit_kills_whole_tree_even_term_ignoring(self):
        marker = "7777.77"
        r = run("1", "sh", "-c", f'sleep {marker} & (trap "" TERM; sleep {marker}) & sleep {marker}')
        self.assertEqual(r.returncode, 124)
        self.assertEqual(leftovers(f"sleep {marker}"), "")

    def test_background_children_of_normal_exit_are_swept(self):
        marker = "7778.78"
        r = run("5", "sh", "-c", f"sleep {marker} & exit 3")
        self.assertEqual(r.returncode, 3)
        self.assertEqual(leftovers(f"sleep {marker}"), "")


if __name__ == "__main__":
    unittest.main()
