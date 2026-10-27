#!/usr/bin/env python3
"""
Tests for the still-bank scripts.

Run:
    python3 -m unittest discover -s skills/workflows/video-production/still-bank/scripts -v
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

SCRIPTS = Path(__file__).parent
PARSE = SCRIPTS / "parse-shot-brief.py"
CONFIGS = SCRIPTS / "build-search-configs.py"
VARIETY = SCRIPTS / "check-variety.py"
OUTPUTS = SCRIPTS / "build-bank-outputs.py"
EDITOR = SCRIPTS / "build-editor-folder.py"

REPO_ROOT = SCRIPTS.parents[4]
FIXTURE_SCRIPT = """# Locked Script: Test Edition

## Hook Grid

| Panel | Brief |
|-------|-------|
| Top left | Lone figure in a dark theater |
| Top right | Silhouette facing a CRT |
| Bottom left | Kid close to an old TV |
| Bottom right | Projector beam over empty seats |

## B-Roll

**Name it** `0:05.6-0:08.6` — ~1.5s each

| # | t | shot |
|---|---|------|
| 01 | `0:05.6` | Dark theater from behind |
| 02 | `0:07.1` | Extreme close on eyes |

**Grid return** `0:08.6-0:10.6` — four panels in one frame

| # | shot |
|---|------|
| 03 | Scoring stage, orchestra, conductor |

## Promo Beat

Not part of the still bank.
"""


def run(script: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        check=False,
    )


class TempCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="still-bank-test-")
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def write(self, relative: str, text: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def write_json(self, relative: str, payload) -> Path:
        return self.write(relative, json.dumps(payload, indent=2))


class ParseShotBriefTest(TempCase):
    def test_parses_a_short_fixture(self) -> None:
        script = self.write("script.md", FIXTURE_SCRIPT)
        result = run(PARSE, "--script", str(script), "--slug", "test-edition")
        self.assertEqual(result.returncode, 0, result.stderr)
        brief = json.loads(result.stdout)

        self.assertEqual(brief["counts"], {"body": 3, "hook": 4, "total": 7})
        self.assertIn("Warning:", result.stderr)  # 3 body stills, format wants 40
        folders = [beat["folder"] for beat in brief["beats"]]
        self.assertEqual(folders, ["hook-grid", "01-name-it", "02-grid-return"])

    def test_rejects_gaps_in_numbering(self) -> None:
        broken = FIXTURE_SCRIPT.replace("| 03 | Scoring", "| 05 | Scoring")
        script = self.write("broken.md", broken)
        result = run(PARSE, "--script", str(script))
        self.assertEqual(result.returncode, 1)
        self.assertIn("Gaps in B-roll numbering", result.stderr)


class BuildSearchConfigsTest(TempCase):
    def setUp(self) -> None:
        super().setUp()
        script = self.write("script.md", FIXTURE_SCRIPT)
        parsed = run(PARSE, "--script", str(script), "--slug", "test-edition")
        self.brief_path = self.write("shot-brief.json", parsed.stdout)
        self.brief = json.loads(parsed.stdout)
        self.slots = [entry["slot"] for entry in self.brief["briefs"]]

    def plan(self, **overrides) -> list[dict]:
        base = [
            {"slot": slot, "method": "pexels", "queries": ["one", "two", "three"]}
            for slot in self.slots
        ]
        return [{**entry, **overrides.get(entry["slot"], {})} for entry in base]

    def test_writes_configs_for_a_valid_plan(self) -> None:
        plan = self.plan(
            **{
                "shot-02": {"method": "web-still", "queries": ["a", "b", "c"]},
                "shot-03": {
                    "method": "commons",
                    "queries": ["a", "b", "c"],
                    "subject": "Film scoring",
                    "categories": ["Category:Film scoring"],
                },
            }
        )
        queries_path = self.write_json("queries.json", plan)
        out = self.root / "configs"

        result = run(
            CONFIGS,
            "--shot-brief", str(self.brief_path),
            "--queries", str(queries_path),
            "--out", str(out),
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        pexels = json.loads((out / "pexels" / "01-name-it.searches.json").read_text())
        self.assertEqual(pexels, [{"shot_id": "shot-01", "query": "one", "count": 3}])

        alternates = json.loads((out / "pexels" / "01-name-it.alt-searches.json").read_text())
        self.assertEqual([entry["shot_id"] for entry in alternates], ["shot-01-alt1", "shot-01-alt2"])

        commons = json.loads((out / "commons" / "section-categories.json").read_text())
        self.assertEqual(commons[0]["section"], "shot-03")

        template = json.loads((out / "web-stills" / "test-edition-web-stills.json").read_text())
        self.assertEqual([entry["id"] for entry in template], ["shot-02a", "shot-02b", "shot-02c"])
        self.assertTrue(all(entry["url"] == "" for entry in template))

        packet = (out / "web-stills" / "test-edition-web-still-packet.md").read_text()
        self.assertIn("`shot-02a`", packet)

        plan_doc = json.loads((out / "test-edition-still-bank-search-plan.json").read_text())
        self.assertEqual(plan_doc["planned_candidates"], len(self.slots) * 3)

    def test_rejects_thin_query_sets(self) -> None:
        plan = self.plan(**{"shot-01": {"queries": ["only one"]}})
        queries_path = self.write_json("queries.json", plan)
        result = run(
            CONFIGS,
            "--shot-brief", str(self.brief_path),
            "--queries", str(queries_path),
            "--out", str(self.root / "configs"),
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("shot-01: 1 queries, needs at least 3", result.stderr)

    def test_rejects_an_uncovered_slot(self) -> None:
        plan = [entry for entry in self.plan() if entry["slot"] != "shot-02"]
        queries_path = self.write_json("queries.json", plan)
        result = run(
            CONFIGS,
            "--shot-brief", str(self.brief_path),
            "--queries", str(queries_path),
            "--out", str(self.root / "configs"),
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("no plan entry", result.stderr)
        self.assertIn("shot-02", result.stderr)

    def test_rejects_an_unknown_method(self) -> None:
        plan = self.plan(**{"shot-01": {"method": "getty"}})
        queries_path = self.write_json("queries.json", plan)
        result = run(
            CONFIGS,
            "--shot-brief", str(self.brief_path),
            "--queries", str(queries_path),
            "--out", str(self.root / "configs"),
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("is not one of", result.stderr)

    def test_generation_needs_a_reason(self) -> None:
        plan = self.plan(**{"shot-01": {"method": "generation", "queries": []}})
        queries_path = self.write_json("queries.json", plan)
        result = run(
            CONFIGS,
            "--shot-brief", str(self.brief_path),
            "--queries", str(queries_path),
            "--out", str(self.root / "configs"),
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("generation entries need a reason", result.stderr)


class CheckVarietyTest(TempCase):
    def make_image(self, relative: str, color: str, noise: bool = False) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        image = Image.new("RGB", (240, 420), color)
        if noise:
            pixels = image.load()
            for x in range(0, 240, 3):
                for y in range(0, 420, 3):
                    pixels[x, y] = (255, 255, 255)
        image.save(path)
        return path

    def test_flags_the_same_image_in_two_slots(self) -> None:
        first = self.make_image("bank/01-beat/shot-01_option-1.jpg", "#4a3b2a", noise=True)
        shutil.copy(first, self.root / "bank/01-beat/shot-02_option-1.jpg")

        result = run(VARIETY, "--bank-root", str(self.root / "bank"), "--slug", "test")
        self.assertEqual(result.returncode, 1)
        self.assertIn("shot-01_option-1.jpg", result.stdout)
        self.assertIn("shot-02_option-1.jpg", result.stdout)
        self.assertIn("1 repeats", result.stderr)

    def test_does_not_flag_siblings_of_the_same_slot(self) -> None:
        first = self.make_image("bank/01-beat/shot-01_option-1.jpg", "#4a3b2a", noise=True)
        shutil.copy(first, self.root / "bank/01-beat/shot-01_option-2.jpg")

        result = run(VARIETY, "--bank-root", str(self.root / "bank"), "--slug", "test")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("No still repeats", result.stdout)

    def test_separates_flat_panels_by_colour(self) -> None:
        """Flat frames share a degenerate hash; colour has to break the tie."""
        self.make_image("bank/hook-grid/shot-41_option-1.jpg", "#c0392b")
        self.make_image("bank/hook-grid/shot-42_option-1.jpg", "#2471a3")

        result = run(VARIETY, "--bank-root", str(self.root / "bank"), "--slug", "test")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("No still repeats", result.stdout)
        self.assertIn("Too flat to read", result.stdout)

    def test_flags_a_frame_too_dark_to_read(self) -> None:
        self.make_image("bank/01-beat/shot-01_option-1.jpg", "#050505")
        self.make_image("bank/01-beat/shot-02_option-1.jpg", "#c0392b", noise=True)

        result = run(VARIETY, "--bank-root", str(self.root / "bank"), "--slug", "test")
        self.assertIn("## Too dark to read", result.stdout)
        self.assertIn("shot-01_option-1.jpg", result.stdout.split("## Too dark to read")[1])


class BuildBankOutputsTest(TempCase):
    def setUp(self) -> None:
        super().setUp()
        self.bank = self.root / "bank"
        self.out = self.root / "out"

        for name in ("shot-01_option-1.jpg", "shot-01_option-2.jpg"):
            path = self.bank / "01-name-it" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            Image.new("RGB", (120, 200), "#333333").save(path)

        self.write_json(
            "bank/01-name-it/download-tracker.json",
            {
                "shot-01": [
                    {
                        "filename": "shot-01_option-1.jpg",
                        "pexels_id": 111,
                        "url": "https://www.pexels.com/photo/111/",
                        "photographer": "A Photographer",
                    },
                    {
                        "filename": "shot-01_option-2.jpg",
                        "pexels_id": 222,
                        "url": "https://www.pexels.com/photo/222/",
                        "photographer": "B Photographer",
                    },
                ]
            },
        )

        web_path = self.bank / "01-name-it" / "shot-02a.jpg"
        Image.new("RGB", (120, 200), "#884422").save(web_path)
        self.write_json(
            "bank/01-name-it/shot-02a.json",
            {
                "id": "shot-02a",
                "url": "https://example.com/eyes.jpg",
                "query": "extreme close up eyes screen reflection",
                "local_path": str(web_path),
                "rights_note": "unclear",
            },
        )

        self.brief_path = self.write_json(
            "shot-brief.json",
            {
                "slug": "test-edition",
                "source": "locked-script.md",
                "counts": {"body": 3, "hook": 0, "total": 3},
                "beats": [
                    {
                        "beat": "name-it",
                        "title": "Name it",
                        "window": "0:05.6-0:10.6",
                        "folder": "01-name-it",
                        "slots": ["shot-01", "shot-02", "shot-03"],
                    }
                ],
                "briefs": [
                    {
                        "slot": "shot-01", "n": 1, "kind": "body", "beat": "name-it",
                        "beat_title": "Name it", "folder": "01-name-it", "t": "0:05.6",
                        "brief": "Dark theater from behind",
                    },
                    {
                        "slot": "shot-02", "n": 2, "kind": "body", "beat": "name-it",
                        "beat_title": "Name it", "folder": "01-name-it", "t": "0:07.1",
                        "brief": "Extreme close on eyes",
                    },
                    {
                        "slot": "shot-03", "n": 3, "kind": "body", "beat": "name-it",
                        "beat_title": "Name it", "folder": "01-name-it", "t": "0:09.1",
                        "brief": "Projector beam through dust",
                    },
                ],
            },
        )

    def build(self, *extra: str) -> subprocess.CompletedProcess:
        return run(
            OUTPUTS,
            "--shot-brief", str(self.brief_path),
            "--bank-root", str(self.bank),
            "--out", str(self.out),
            *extra,
        )

    def test_builds_map_inventory_and_rows(self) -> None:
        result = self.build("--write-manifest")
        # shot-03 has no file on disk, so the run reports an unsourced slot.
        self.assertEqual(result.returncode, 1)
        self.assertIn("Unsourced slots: ST-03", result.stderr)

        inventory = json.loads((self.out / "test-edition-still-bank-on-disk.json").read_text())
        self.assertEqual(len(inventory), 3)
        self.assertEqual({entry["method"] for entry in inventory}, {"pexels", "web-still"})

        rows = (self.out / "test-edition-still-bank-manifest-rows.md").read_text()
        self.assertIn("| ST-01a |", rows)
        self.assertIn("Pexels License", rows)
        self.assertIn("rights unclear", rows)
        self.assertIn("needs-source", rows)
        self.assertIn("- ready: 2", rows)

        bank_map = (self.out / "test-edition-still-bank-map.md").read_text()
        self.assertIn("**pick**", bank_map)
        self.assertIn("https://www.pexels.com/photo/111/", bank_map)
        self.assertIn("**not sourced**", bank_map)

        manifest = (self.out / "test-edition-asset-manifest.md").read_text()
        self.assertIn("## Source Readiness Summary", manifest)
        self.assertIn("| Asset ID | Scene / Beat | Type |", manifest)

        # Generated pointers are relative to the production output folder.
        production_output = REPO_ROOT / "workspaces/video-production/stages/03-asset-gathering/output"
        for relative in ["../../../../../libraries/media/assets/index.md",
                         "../../../../../libraries/media/shared/asset-record-format.md"]:
            self.assertIn(relative, manifest)
            self.assertTrue((production_output / relative).resolve().is_file())

    def test_honours_an_explicit_pick(self) -> None:
        picks = self.write_json("picks.json", {"shot-01": "b"})
        self.build("--picks", str(picks))
        rows = (self.out / "test-edition-still-bank-manifest-rows.md").read_text()
        self.assertIn("| ST-01b |", rows)
        self.assertIn("shot-01_option-2.jpg", rows)
        # The unpicked sibling becomes the named fallback.
        self.assertIn("ST-01a", rows.split("| ST-01b |")[1].split("\n")[0])

    def test_never_overwrites_an_existing_manifest(self) -> None:
        self.out.mkdir(parents=True, exist_ok=True)
        manifest = self.out / "test-edition-asset-manifest.md"
        manifest.write_text("# Hand-written manifest\n", encoding="utf-8")

        result = self.build("--write-manifest")
        self.assertEqual(manifest.read_text(), "# Hand-written manifest\n")
        self.assertIn("not overwritten", result.stderr)


class BuildEditorFolderTest(TempCase):
    def make_bank(self) -> Path:
        bank = self.root / "bank"
        for rel in (
            "00-hook-grid/avatar-glow.jpg",
            "01-the-read/team-campfire.jpg",
            "01-the-read/pexels/lecture-hall_001.jpeg",
            "_clips/avatar/footage/frame.jpg",
        ):
            path = bank / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            Image.new("RGB", (64, 36), "red").save(path)
        (bank / "01-the-read/pexels/download-tracker.json").write_text("{}", encoding="utf-8")
        return bank

    def run_editor(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(EDITOR), *args], capture_output=True, text=True
        )

    def test_builds_numbered_flat_beat_folders(self) -> None:
        bank = self.make_bank()
        dest = self.root / "desktop-stills"
        result = self.run_editor("--bank-root", str(bank), "--dest", str(dest))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            sorted(p.name for p in dest.iterdir() if p.is_dir()),
            ["0-HOOK-GRID", "1-THE-READ"],
        )
        self.assertEqual(
            sorted(p.name for p in (dest / "1-THE-READ").iterdir()),
            ["pexels-lecture-hall_001.jpeg", "team-campfire.jpg"],
        )
        self.assertTrue((dest / "00-PREVIEW.jpg").exists())
        self.assertTrue((bank / "01-the-read/team-campfire.jpg").exists())

    def test_marks_picks(self) -> None:
        bank = self.make_bank()
        dest = self.root / "desktop-stills"
        result = self.run_editor(
            "--bank-root", str(bank), "--dest", str(dest), "--pick", "avatar-glow"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((dest / "0-HOOK-GRID/PICK_avatar-glow.jpg").exists())

    def test_marks_nested_picks_without_a_false_warning(self) -> None:
        bank = self.make_bank()
        dest = self.root / "desktop-stills"
        result = self.run_editor(
            "--bank-root", str(bank), "--dest", str(dest), "--pick", "lecture-hall_001"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((dest / "1-THE-READ/PICK_pexels-lecture-hall_001.jpeg").exists())
        self.assertNotIn("matched no image", result.stderr)

    def test_refuses_to_overwrite_a_foreign_folder(self) -> None:
        bank = self.make_bank()
        dest = self.root / "someone-elses"
        dest.mkdir()
        (dest / "keep.txt").write_text("x", encoding="utf-8")
        result = self.run_editor("--bank-root", str(bank), "--dest", str(dest), "--replace")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((dest / "keep.txt").exists())

    def test_replace_rebuilds_its_own_folder(self) -> None:
        bank = self.make_bank()
        dest = self.root / "desktop-stills"
        self.run_editor("--bank-root", str(bank), "--dest", str(dest))
        again = self.run_editor("--bank-root", str(bank), "--dest", str(dest))
        self.assertNotEqual(again.returncode, 0)
        replaced = self.run_editor("--bank-root", str(bank), "--dest", str(dest), "--replace")
        self.assertEqual(replaced.returncode, 0, replaced.stderr)


if __name__ == "__main__":
    unittest.main()
