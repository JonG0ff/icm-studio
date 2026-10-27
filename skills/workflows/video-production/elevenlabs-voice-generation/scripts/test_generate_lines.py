#!/usr/bin/env python3
"""Tests for generate_lines.py. HTTP and ffmpeg are mocked.

Run:
    python3 -m pytest skills/workflows/video-production/elevenlabs-voice-generation/scripts -q
"""

from __future__ import annotations

import base64
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).with_name("generate_lines.py")
SPEC = importlib.util.spec_from_file_location("generate_lines", SCRIPT)
gl = importlib.util.module_from_spec(SPEC)
sys.modules["generate_lines"] = gl
SPEC.loader.exec_module(gl)

SCRIPT_TEXT = """# Episode 1

Notes for the human. Ignored.

[h1-01] HOST: [excited] Three ways to build faster.
[h2-01] GUEST: Nobody tells you this.
[b-01] HOST: First, ship small.
[b-02] GUEST: [laughs] Then ship again.
"""

VOICES = {
    "HOST": {"voice_id": "v-host", "model_id": "eleven_v3",
             "settings": {"stability": 0.5, "similarity_boost": 0.75, "speed": 1.0}},
    "GUEST": {"voice_id": "v-guest"},
}


def fake_response(text: str = "hi") -> bytes:
    chars = list(text)
    return json.dumps({
        "audio_base64": base64.b64encode(b"ID3fake").decode(),
        "alignment": {
            "characters": chars,
            "character_start_times_seconds": [i * 0.1 for i in range(len(chars))],
            "character_end_times_seconds": [i * 0.1 + 0.1 for i in range(len(chars))],
        },
    }).encode()


class FakePost:
    def __init__(self, statuses=None):
        self.calls: list[tuple[str, dict, dict]] = []
        self.statuses = list(statuses or [])

    def __call__(self, url, headers, body):
        self.calls.append((url, headers, json.loads(body)))
        status = self.statuses.pop(0) if self.statuses else 200
        return (status, fake_response()) if status == 200 else (status, b'{"detail":"nope"}')


class ParseScriptTest(unittest.TestCase):
    def test_parses_spoken_lines_and_ignores_others(self):
        lines = gl.parse_script(SCRIPT_TEXT)
        self.assertEqual([l.id for l in lines], ["h1-01", "h2-01", "b-01", "b-02"])
        self.assertEqual(lines[0].speaker, "HOST")
        self.assertEqual(lines[0].text, "[excited] Three ways to build faster.")
        self.assertEqual(lines[0].hook_variant, 1)
        self.assertIsNone(lines[2].hook_variant)

    def test_malformed_id_line_fails(self):
        for bad in ("[b-1] HOST: hi", "[b-01] host: hi", "[h1-1] HOST: hi", "[b-01] HOST:"):
            with self.subTest(bad=bad), self.assertRaises(gl.ScriptError):
                gl.parse_script(bad)

    def test_tag_only_line_is_ignored(self):
        lines = gl.parse_script("[excited] not a script line\n[b-01] HOST: ok")
        self.assertEqual(len(lines), 1)

    def test_duplicate_and_empty(self):
        with self.assertRaises(gl.ScriptError):
            gl.parse_script("[b-01] HOST: a\n[b-01] HOST: b")
        with self.assertRaises(gl.ScriptError):
            gl.parse_script("# nothing here")

    def test_variant_order(self):
        lines = gl.parse_script(SCRIPT_TEXT)
        self.assertEqual(gl.hook_variants(lines), (1, 2))
        self.assertEqual([l.id for l in gl.variant_order(lines, 2)], ["h2-01", "b-01", "b-02"])
        with self.assertRaises(gl.ScriptError):
            gl.variant_order(lines, 3)

    def test_variant_without_hooks(self):
        lines = gl.parse_script("[b-01] HOST: a\n[b-02] HOST: b")
        self.assertEqual([l.id for l in gl.variant_order(lines, 1)], ["b-01", "b-02"])
        with self.assertRaises(gl.ScriptError):
            gl.variant_order(lines, 2)


class VoicesTest(unittest.TestCase):
    def test_missing_voice_for_speaker(self):
        lines = gl.parse_script(SCRIPT_TEXT)
        with self.assertRaisesRegex(gl.ScriptError, "GUEST"):
            gl.check_voices(lines, {"HOST": VOICES["HOST"]})

    def test_load_voices_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "v.json"
            path.write_text(json.dumps({"HOST": {"voice_id": ""}}))
            with self.assertRaises(gl.ScriptError):
                gl.load_voices(path)
            path.write_text("[]")
            with self.assertRaises(gl.ScriptError):
                gl.load_voices(path)
            path.write_text("{bad")
            with self.assertRaises(gl.ScriptError):
                gl.load_voices(path)

    def test_line_ids_and_format(self):
        lines = gl.parse_script(SCRIPT_TEXT)
        self.assertEqual(gl.parse_line_ids("b-01, h2-01", lines), {"b-01", "h2-01"})
        with self.assertRaises(gl.ScriptError):
            gl.parse_line_ids("b-09", lines)
        self.assertEqual(gl.sample_rate("mp3_22050_32"), 22050)
        with self.assertRaises(gl.ScriptError):
            gl.sample_rate("pcm_16000")


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.line = gl.parse_script(SCRIPT_TEXT)[0]

    def test_request_shape(self):
        post = FakePost()
        gl.tts_with_timestamps(self.line, VOICES["HOST"], "key", "mp3_44100_128", post, lambda s: None)
        url, headers, body = post.calls[0]
        self.assertIn("/v1/text-to-speech/v-host/with-timestamps?output_format=mp3_44100_128", url)
        self.assertEqual(headers["xi-api-key"], "key")
        self.assertEqual(body["text"], "[excited] Three ways to build faster.")
        self.assertEqual(body["model_id"], "eleven_v3")
        self.assertEqual(body["voice_settings"]["stability"], 0.5)

    def test_retries_429_and_5xx_then_succeeds(self):
        post, sleeps = FakePost([429, 503]), []
        gl.tts_with_timestamps(self.line, VOICES["HOST"], "k", "mp3_44100_128", post, sleeps.append)
        self.assertEqual(len(post.calls), 3)
        self.assertEqual(sleeps, [1.0, 2.0])

    def test_gives_up_after_three_retries(self):
        post = FakePost([500, 500, 500, 500])
        with self.assertRaisesRegex(gl.ApiError, "HTTP 500"):
            gl.tts_with_timestamps(self.line, VOICES["HOST"], "k", "mp3_44100_128", post, lambda s: None)
        self.assertEqual(len(post.calls), 4)

    def test_client_error_fails_fast(self):
        post = FakePost([401])
        with self.assertRaisesRegex(gl.ApiError, "HTTP 401: .*nope"):
            gl.tts_with_timestamps(self.line, VOICES["HOST"], "k", "mp3_44100_128", post, lambda s: None)
        self.assertEqual(len(post.calls), 1)

    def test_save_take_rejects_bad_response(self):
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(gl.ApiError):
            gl.save_take({"audio_base64": "eA=="}, "b-01", Path(tmp))

    def test_api_key_from_env(self):
        with mock.patch.dict("os.environ", {"ELEVEN_API_KEY": "abc"}, clear=True):
            self.assertEqual(gl.read_api_key(), "abc")
        with mock.patch.dict("os.environ", {}, clear=True), self.assertRaisesRegex(gl.ScriptError, "ELEVENLABS_API_KEY"):
            gl.read_api_key()

    def test_http_post_handles_http_and_network_errors(self):
        import urllib.error
        err = urllib.error.HTTPError("u", 429, "slow", {}, None)
        err.read = lambda: b"rate"
        with mock.patch("urllib.request.urlopen", side_effect=err):
            self.assertEqual(gl.http_post("http://x", {}, b""), (429, b"rate"))
        with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("down")):
            self.assertEqual(gl.http_post("http://x", {}, b""), (0, b"down"))
        response = mock.MagicMock()
        response.__enter__.return_value.status = 200
        response.__enter__.return_value.read.return_value = b"{}"
        with mock.patch("urllib.request.urlopen", return_value=response):
            self.assertEqual(gl.http_post("http://x", {}, b""), (200, b"{}"))


class StitchTest(unittest.TestCase):
    def test_command_has_gaps_between_lines_only(self):
        cmd = gl.stitch_command([Path("a.mp3"), Path("b.mp3"), Path("c.mp3")], Path("o.mp3"), 150, 44100, "ffmpeg")
        graph = cmd[cmd.index("-filter_complex") + 1]
        self.assertEqual(graph.count("anullsrc"), 2)
        self.assertIn("atrim=duration=0.150", graph)
        self.assertIn("concat=n=5:v=0:a=1[out]", graph)

    def test_zero_gap(self):
        cmd = gl.stitch_command([Path("a.mp3"), Path("b.mp3")], Path("o.mp3"), 0, 44100, "ffmpeg")
        self.assertIn("concat=n=2", cmd[cmd.index("-filter_complex") + 1])

    def test_run_command_raises_on_failure(self):
        with self.assertRaisesRegex(RuntimeError, "false failed"):
            gl.run_command(["false"])


class RunTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        (root / "script.md").write_text(SCRIPT_TEXT)
        (root / "cast-voices.json").write_text(json.dumps(VOICES))
        self.root = root
        self.audio = root / "audio"
        self.runner_calls: list[list[str]] = []
        self.which = mock.patch("shutil.which", return_value="/usr/bin/ffmpeg")
        self.which.start()
        self.env = mock.patch.dict("os.environ", {"ELEVENLABS_API_KEY": "test-key"})
        self.env.start()

    def tearDown(self):
        self.which.stop()
        self.env.stop()
        self.tmp.cleanup()

    def args(self, *extra):
        return gl.build_parser().parse_args([
            "--script", str(self.root / "script.md"), "--voices", str(self.root / "cast-voices.json"),
            "--out-audio", str(self.audio), "--out-manifest", str(self.root / "manifest"), *extra])

    def runner(self, cmd):
        self.runner_calls.append(cmd)
        Path(cmd[-1]).write_bytes(b"stitched")

    def test_dry_run_makes_no_calls(self):
        post = FakePost()
        with mock.patch.dict("os.environ", {}, clear=True):
            self.assertEqual(gl.run(self.args("--dry-run"), post, lambda s: None, self.runner), 0)
        self.assertEqual(post.calls, [])
        self.assertEqual(self.runner_calls, [])
        self.assertFalse(self.audio.exists())

    def test_full_run_writes_takes_variants_and_manifest(self):
        post = FakePost()
        gl.run(self.args(), post, lambda s: None, self.runner)
        self.assertEqual(len(post.calls), 4)
        self.assertTrue((self.audio / "b-02.alignment.json").exists())
        self.assertTrue((self.audio / "variant-v1.mp3").exists())
        self.assertTrue((self.audio / "variant-v2.mp3").exists())
        manifest = (self.root / "manifest" / "voice-manifest.md").read_text()
        self.assertIn("| b-02 | GUEST | ../audio/b-02.mp3 | made | 25 |", manifest)
        self.assertIn("| v2 | ../audio/variant-v2.mp3 | h2-01, b-01, b-02 |", manifest)

    def test_reroll_only_listed_lines(self):
        gl.run(self.args(), FakePost(), lambda s: None, self.runner)
        post = FakePost()
        gl.run(self.args("--lines", "b-01,h2-01"), post, lambda s: None, self.runner)
        texts = [body["text"] for _, _, body in post.calls]
        self.assertEqual(texts, ["Nobody tells you this.", "First, ship small."])

    def test_second_run_skips_existing(self):
        gl.run(self.args(), FakePost(), lambda s: None, self.runner)
        post = FakePost()
        with mock.patch.dict("os.environ", {}, clear=True):
            gl.run(self.args(), post, lambda s: None, self.runner)
        self.assertEqual(post.calls, [])

    def test_missing_take_skips_variant(self):
        self.audio.mkdir()
        lines = gl.parse_script(SCRIPT_TEXT)
        stitched = gl.stitch_variants(lines, self.audio, 150, 44100, self.runner)
        self.assertEqual(stitched, [])

    def test_main_reports_errors(self):
        (self.root / "cast-voices.json").write_text(json.dumps({"HOST": VOICES["HOST"]}))
        argv = ["--script", str(self.root / "script.md"), "--voices", str(self.root / "cast-voices.json"),
                "--out-audio", str(self.audio), "--out-manifest", str(self.root), "--dry-run"]
        self.assertEqual(gl.main(argv), 1)

    def test_bad_inputs(self):
        with self.assertRaises(gl.ScriptError):
            gl.run(self.args("--gap-ms", "-1"))
        (self.root / "script.md").unlink()
        with self.assertRaises(gl.ScriptError):
            gl.run(self.args())

    def test_no_ffmpeg(self):
        with mock.patch("shutil.which", return_value=None), self.assertRaisesRegex(gl.ScriptError, "ffmpeg"):
            gl.stitch_variants(gl.parse_script(SCRIPT_TEXT), self.audio, 150, 44100, self.runner)


if __name__ == "__main__":
    unittest.main()
