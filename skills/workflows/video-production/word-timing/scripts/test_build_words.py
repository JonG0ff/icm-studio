#!/usr/bin/env python3
"""Tests for build_words.py. ffprobe, ffmpeg, and Whisper are mocked.

Run:
    python3 -m pytest skills/workflows/video-production/word-timing/scripts -q
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).with_name("build_words.py")
SPEC = importlib.util.spec_from_file_location("build_words", SCRIPT)
bw = importlib.util.module_from_spec(SPEC)
sys.modules["build_words"] = bw
SPEC.loader.exec_module(bw)

SCRIPT_TEXT = """# Episode
[h1-01] HOST: [excited] Build it now.
[h2-01] GUEST: Wait for it.
[b-01] HOST: Ada ships every day.
[b-02] GUEST: [laughs] Then she rests.
"""


def alignment_for(text: str, step: float = 0.1) -> dict:
    chars = list(text)
    return {"characters": chars,
            "character_start_times_seconds": [i * step for i in range(len(chars))],
            "character_end_times_seconds": [i * step + step for i in range(len(chars))]}


def heard_words(spec: list[tuple[str, float]]) -> list[dict]:
    return [{"word": w, "start": s, "end": s + 0.3} for w, s in spec]


class ParseTest(unittest.TestCase):
    def test_parse_and_variant_order(self):
        lines = bw.parse_script(SCRIPT_TEXT)
        self.assertEqual([l.id for l in bw.variant_order(lines, 1)], ["h1-01", "b-01", "b-02"])
        self.assertEqual(lines[0].words, ("Build", "it", "now."))
        with self.assertRaises(bw.TimingError):
            bw.variant_order(lines, 5)

    def test_bad_lines(self):
        for bad in ("[b-1] HOST: x", "[b-01] HOST: a\n[b-01] HOST: b", "nothing"):
            with self.subTest(bad=bad), self.assertRaises(bw.TimingError):
                bw.parse_script(bad)

    def test_body_only_script(self):
        lines = bw.parse_script("[b-01] HOST: a")
        self.assertEqual(len(bw.variant_order(lines, 1)), 1)
        with self.assertRaises(bw.TimingError):
            bw.variant_order(lines, 2)


class ModeATest(unittest.TestCase):
    def test_alignment_to_words_skips_tags_and_offsets(self):
        line = bw.ScriptLine("b-02", "GUEST", "[laughs] Then she rests.")
        words = bw.alignment_to_words(alignment_for("[laughs] Then she"), 2.0, line)
        self.assertEqual([w["word"] for w in words], ["Then", "she"])
        self.assertEqual(words[0], {"word": "Then", "start": 2.9, "end": 3.3, "speaker": "GUEST", "line": "b-02"})

    def test_alignment_length_mismatch(self):
        bad = {"characters": ["a", "b"], "character_start_times_seconds": [0], "character_end_times_seconds": [0, 1]}
        with self.assertRaises(bw.TimingError):
            bw.alignment_to_words(bad, 0, bw.ScriptLine("b-01", "HOST", "ab"))

    def test_build_made_offsets_match_stitching(self):
        lines = bw.variant_order(bw.parse_script(SCRIPT_TEXT), 1)
        durations = {"h1-01.mp3": 1.0, "b-01.mp3": 2.0, "b-02.mp3": 1.5}
        with tempfile.TemporaryDirectory() as tmp:
            audio = Path(tmp)
            for line in lines:
                (audio / f"{line.id}.mp3").write_bytes(b"x")
                if line.id != "b-02":
                    (audio / f"{line.id}.alignment.json").write_text(json.dumps(alignment_for(line.text)))
            results, duration = bw.build_made(lines, audio, 150, lambda p: durations[p.name])
        self.assertEqual(duration, 4.8)
        self.assertEqual((results[1].start, results[1].end), (1.15, 3.15))
        self.assertEqual(results[1].words[0]["word"], "Ada")
        self.assertEqual(results[1].words[0]["start"], 1.15)
        self.assertFalse(results[2].found)
        self.assertIn("missing b-02.alignment.json", results[2].notes)

    def test_missing_mp3_fails(self):
        lines = bw.variant_order(bw.parse_script(SCRIPT_TEXT), 1)
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(bw.TimingError):
            bw.build_made(lines, Path(tmp), 150, lambda p: 1.0)


class ModeBTest(unittest.TestCase):
    def setUp(self):
        self.lines = bw.variant_order(bw.parse_script(SCRIPT_TEXT), 1)

    def test_fuzzy_match_respells_misheard_word(self):
        heard = heard_words([("Build", 0.0), ("it", 0.3), ("now.", 0.6),
                             ("Ayda", 1.2), ("ships", 1.5), ("every", 1.8), ("day.", 2.1),
                             ("Then", 2.6), ("she", 2.9), ("rests.", 3.2)])
        results = bw.align_lines(self.lines, heard)
        self.assertTrue(all(r.found for r in results))
        first = results[1].words[0]
        self.assertEqual(first, {"word": "Ada", "start": 1.2, "end": 1.5, "speaker": "HOST", "line": "b-01"})
        self.assertIn("script 'Ada' heard 'Ayda'", results[1].notes)
        self.assertEqual(results[2].words[-1]["word"], "rests.")

    def test_not_found_line_reported(self):
        heard = heard_words([("Build", 0.0), ("it", 0.3), ("now", 0.6),
                             ("Then", 2.6), ("she", 2.9), ("rests", 3.2)])
        results = bw.align_lines(self.lines, heard)
        self.assertEqual([r.found for r in results], [True, False, True])
        self.assertIn("matched 0/4 words", results[1].notes)
        report = bw.report_markdown("B", 1, 4.0, results)
        self.assertIn("| b-01 | HOST | NOT FOUND |", report)

    def test_dropped_word_gets_interpolated_time(self):
        heard = heard_words([("Build", 0.0), ("now", 1.0)])
        result = bw.align_lines(self.lines[:1], heard)[0]
        self.assertTrue(result.found)
        self.assertEqual([w["word"] for w in result.words], ["Build", "it", "now."])
        self.assertEqual((result.words[1]["start"], result.words[1]["end"]), (0.3, 1.0))
        self.assertIn("script 'it' not heard", result.notes)

    def test_fill_gaps_edges(self):
        self.assertEqual(bw.fill_gaps([None, (1.0, 2.0)]), [(1.0, 1.0), (1.0, 2.0)])
        self.assertEqual(bw.fill_gaps([(1.0, 2.0), None]), [(1.0, 2.0), (2.0, 2.0)])

    def test_run_whisper_parses_cli_json(self):
        def fake_run(cmd, capture_output, text):
            out = Path(cmd[cmd.index("--output_dir") + 1]) / "full.json"
            out.write_text(json.dumps({"segments": [{"words": [{"word": " Hi", "start": 0, "end": 0.2},
                                                                {"word": " ", "start": 0.2, "end": 0.2}]}]}))
            return subprocess.CompletedProcess(cmd, 0, "", "")
        with mock.patch("subprocess.run", side_effect=fake_run) as run:
            words = bw.run_whisper(Path("full.wav"), "medium.en", "whisper")
        self.assertEqual(words, [{"word": "Hi", "start": 0.0, "end": 0.2}])
        self.assertIn("--word_timestamps", run.call_args[0][0])
        with mock.patch("subprocess.run", return_value=subprocess.CompletedProcess([], 1, "", "boom")):
            with self.assertRaisesRegex(bw.TimingError, "boom"):
                bw.run_whisper(Path("full.wav"), "medium", "whisper")

    def test_find_whisper(self):
        self.assertEqual(bw.find_whisper("/x/whisper"), "/x/whisper")
        with mock.patch("shutil.which", return_value=None), \
             mock.patch.object(bw, "FALLBACK_WHISPER", Path("/nonexistent/whisper")), \
             self.assertRaises(bw.TimingError):
            bw.find_whisper(None)


class ToolsTest(unittest.TestCase):
    def test_ffprobe_duration(self):
        with mock.patch("shutil.which", return_value="ffprobe"), \
             mock.patch("subprocess.run", return_value=subprocess.CompletedProcess([], 0, "2.5\n", "")):
            self.assertEqual(bw.ffprobe_duration(Path("a.mp3")), 2.5)
        with mock.patch("shutil.which", return_value="ffprobe"), \
             mock.patch("subprocess.run", return_value=subprocess.CompletedProcess([], 1, "", "bad")), \
             self.assertRaises(bw.TimingError):
            bw.ffprobe_duration(Path("a.mp3"))
        with mock.patch("shutil.which", return_value=None), self.assertRaises(bw.TimingError):
            bw.ffprobe_duration(Path("a.mp3"))

    def test_split_lines(self):
        line = bw.ScriptLine("b-01", "HOST", "hi")
        results = (bw.LineResult(line, True, 0.02, 1.0, ()),
                   bw.LineResult(bw.ScriptLine("b-02", "HOST", "x"), False, None, None, ()))
        with tempfile.TemporaryDirectory() as tmp, mock.patch("shutil.which", return_value="ffmpeg"), \
             mock.patch("subprocess.run", return_value=subprocess.CompletedProcess([], 0, "", "")) as run:
            written = bw.split_lines(Path("t.wav"), results, Path(tmp) / "lines", 1.02)
        self.assertEqual([p.name for p in written], ["b-01.wav"])
        cmd = run.call_args[0][0]
        self.assertEqual(cmd[cmd.index("-ss") + 1], "0.000")
        self.assertEqual(cmd[cmd.index("-to") + 1], "1.020")
        with mock.patch("shutil.which", return_value=None), self.assertRaises(bw.TimingError):
            bw.split_lines(Path("t.wav"), results, Path("x"), 1.0)


class RunTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "script.md").write_text(SCRIPT_TEXT)

    def tearDown(self):
        self.tmp.cleanup()

    def test_mode_b_end_to_end(self):
        track = self.root / "full.wav"
        track.write_bytes(b"x")
        heard = heard_words([("Build", 0.0), ("it", 0.3), ("now", 0.6), ("Ada", 1.2), ("ships", 1.5),
                             ("every", 1.8), ("day", 2.1), ("Then", 2.6), ("she", 2.9), ("rests", 3.2)])
        out = self.root / "out" / "words.json"
        args = bw.build_parser().parse_args(["--script", str(self.root / "script.md"), "--track", str(track),
                                             "--whisper-bin", "w", "--out", str(out)])
        bw.run(args, whisper=lambda *a: heard, probe=lambda p: 4.0)
        data = json.loads(out.read_text())
        self.assertEqual((data["variant"], data["duration"]), (1, 4.0))
        self.assertEqual(len(data["words"]), 10)
        self.assertEqual(data["words"][-1]["word"], "rests.")
        report = (self.root / "out" / "timing-report.md").read_text()
        self.assertIn("Words per minute: 150", report)

    def test_main_errors(self):
        script = str(self.root / "script.md")
        out = str(self.root / "w.json")
        self.assertEqual(bw.main(["--script", script, "--track", str(self.root / "nope.wav"), "--out", out]), 1)
        self.assertEqual(bw.main(["--script", script, "--audio-dir", str(self.root), "--out", out,
                                  "--split-lines", "x"]), 1)
        self.assertEqual(bw.main(["--script", script, "--audio-dir", str(self.root), "--out", out,
                                  "--gap-ms", "-5"]), 1)
        self.assertEqual(bw.main(["--script", str(self.root / "missing.md"), "--audio-dir", ".", "--out", out]), 1)

    def test_mode_a_via_run(self):
        audio = self.root / "audio"
        audio.mkdir()
        for line_id, text in (("h2-01", "Wait for it."), ("b-01", "Ada ships every day."),
                              ("b-02", "[laughs] Then she rests.")):
            (audio / f"{line_id}.mp3").write_bytes(b"x")
            (audio / f"{line_id}.alignment.json").write_text(json.dumps(alignment_for(text, 0.05)))
        out = self.root / "words.json"
        args = bw.build_parser().parse_args(["--script", str(self.root / "script.md"), "--audio-dir", str(audio),
                                             "--variant", "2", "--out", str(out)])
        bw.run(args, probe=lambda p: 1.0)
        data = json.loads(out.read_text())
        self.assertEqual(data["duration"], 3.3)
        self.assertEqual(data["lines"][1]["start"], 1.15)
        self.assertEqual(data["words"][0]["speaker"], "GUEST")


if __name__ == "__main__":
    unittest.main()
