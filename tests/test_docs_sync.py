"""tools/docs-sync.py + tools/docs-drift.sh: hit, allow, history, clean and config-error counter-probes."""
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SYNC = str(ROOT / "tools" / "docs-sync.py")
DRIFT = str(ROOT / "tools" / "docs-drift.sh")


_KEEP = []  # keep the TemporaryDirectory objects alive until the test run ends


class _Tmp:
    def __init__(self, td):
        self.td, self.name = td, td.name


def make(files):
    tmp = tempfile.TemporaryDirectory()
    _KEEP.append(tmp)
    for rel, text in files.items():
        p = pathlib.Path(tmp.name) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return _Tmp(tmp)


def sync(root):
    return subprocess.run([sys.executable, SYNC, "--root", root], capture_output=True, text=True, timeout=30)


def drift(root, rules=".github/docs-drift-rules.txt"):
    return subprocess.run(["bash", DRIFT, rules], cwd=root, capture_output=True, text=True, timeout=30)


BASE = {
    "README.md": "Run `tools/run.sh` and see `docs/x.md`.\n",
    "AGENTS.md": "Rules.\n",
    "tools/run.sh": "#!/bin/sh\n",
    "docs/x.md": "x\n",
}


class DocsSyncTest(unittest.TestCase):
    def test_clean(self):
        tmp = make(BASE)
        r = sync(tmp.name)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("docs-sync: OK", r.stdout)

    def test_missing_path_hit_and_suffix_ok(self):
        files = dict(BASE, **{"README.md": "See `tools/gone.sh`, `x.md` and shortened `docs/x.md`.\n"})
        r = sync(make(files).name)
        self.assertEqual(r.returncode, 1)
        self.assertIn("README.md:1: [paths] `tools/gone.sh`", r.stdout)
        self.assertNotIn("x.md` does not", r.stdout)

    def test_history_line_and_allow(self):
        files = dict(BASE, **{
            "README.md": "(2026-10-01: removed `tools/gone.sh`)\nHA's `configuration.yaml` lives elsewhere.\n",
            ".github/docs-sync.txt": "# comment\n^README\\.md:configuration\\.yaml$\n",
        })
        r = sync(make(files).name)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_docs_directive(self):
        files = dict(BASE, **{
            ".github/docs-sync.txt": "@docs README.md docs/x.md\n",
            "docs/x.md": "`tools/gone.sh`\n",
        })
        r = sync(make(files).name)
        self.assertEqual(r.returncode, 1)
        self.assertIn("docs/x.md:1: [paths]", r.stdout)

    def test_npm_scripts(self):
        files = dict(BASE, **{
            "package.json": '{"scripts": {"build": "x"}}',
            "README.md": "`npm run build` and `npm run nope`; plain npm audit is fine.\n",
        })
        r = sync(make(files).name)
        self.assertEqual(r.returncode, 1)
        self.assertIn("`npm run nope`", r.stdout)
        self.assertNotIn("npm run build`", r.stdout)

    def test_env_checks(self):
        files = dict(BASE, **{
            ".env.example": "USED_VAR=1\n# UNUSED_VAR=2\n",
            "src/config.ts": "const schema = z.object({\n  USED_VAR: z.string(),\n  NEW_KEY: z.string().optional(),\n  NODE_ENV: z.string(),\n});\n",
            "unraid/app.xml": '<Config Target="USED_VAR" Type="Variable"/>\n<Config Target="XML_ONLY" Type="Variable"/>\n',
            "README.md": "Set `USED_VAR`, `USED_MISSING` and `OTHER_THING`.\n",
        })
        r = sync(make(files).name)
        self.assertEqual(r.returncode, 1)
        out = r.stdout
        self.assertIn("UNUSED_VAR is documented but not used", out)
        self.assertIn("XML_ONLY is set in the Unraid template", out)
        self.assertIn("NEW_KEY is read by the config schema", out)
        self.assertIn("`USED_MISSING` is named in the docs", out)
        self.assertNotIn("OTHER_THING", out)  # prefix is not an env prefix of this repo
        self.assertNotIn("NODE_ENV", out)  # internal

    def test_bad_allow_regex_is_config_error(self):
        files = dict(BASE, **{".github/docs-sync.txt": "([\n"})
        self.assertEqual(sync(make(files).name).returncode, 2)


class DocsDriftScriptTest(unittest.TestCase):
    RULES = "@files README.md\n@allow \\(20[0-9]{2}-[0-9]{2}-[0-9]{2}: \nOldName\told name\n"

    def test_hit_allow_clean_and_config_error(self):
        tmp = make({"README.md": "Uses OldName.\n(2026-10-01: OldName retired)\n", "r.txt": self.RULES})
        r = drift(tmp.name, "r.txt")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout.strip().splitlines(), ["README.md:1: old name"])
        clean = make({"README.md": "Fine.\n", "r.txt": self.RULES})
        self.assertEqual(drift(clean.name, "r.txt").returncode, 0)
        bad = make({"README.md": "x\n", "r.txt": "@files README.md\nno tab here\n"})
        self.assertEqual(drift(bad.name, "r.txt").returncode, 2)
        self.assertEqual(drift(bad.name, "missing.txt").returncode, 2)

    def test_repo_is_clean(self):
        for cmd in (["bash", DRIFT], [sys.executable, SYNC]):
            r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=60)
            self.assertEqual(r.returncode, 0, r.stdout)


if __name__ == "__main__":
    unittest.main()
