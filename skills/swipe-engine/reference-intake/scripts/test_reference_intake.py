#!/usr/bin/env python3
"""Fixture-based integration tests for reference_intake.py."""

from __future__ import annotations

import contextlib
import http.server
import json
import os
import shlex
import shutil
import socketserver
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

from PIL import Image


SCRIPT = Path(__file__).with_name("reference_intake.py")


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, _format: str, *_args: object) -> None:
        return


class ReferenceIntakeIntegrationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="reference-intake-test-")
        self.root = Path(self.temp.name)
        (self.root / "libraries/swipes/stages/01-save/output/assets").mkdir(parents=True)
        (self.root / "libraries/swipes/knowledge-layer/assets").mkdir(parents=True)
        self.fixtures = self.root / "fixtures"
        self.fixtures.mkdir()
        self.image = self.fixtures / "reference.png"
        Image.new("RGB", (320, 180), "#2d45ff").save(self.image)
        self.direct_image = self.fixtures / "direct.png"
        Image.new("RGB", (320, 180), "#ff6b2d").save(self.direct_image)
        self.webpage_image = self.fixtures / "full-page.png"
        Image.new("RGB", (640, 1200), "#131722").save(self.webpage_image)
        self.pdf = self.fixtures / "reference.pdf"
        Image.new("RGB", (640, 480), "white").save(self.pdf, "PDF", resolution=150)
        self.video = self.fixtures / "reference.mp4"
        self.audio = self.fixtures / "reference.mp3"
        self.transcript = self.fixtures / "provided-transcript.txt"
        self.transcript.write_text("Stop scrolling. Book a call today.\n", encoding="utf-8")
        self.cookies = self.fixtures / "cookies.txt"
        self.cookies.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            self.skipTest("ffmpeg is required")
        result = subprocess.run(
            [
                ffmpeg,
                "-v",
                "error",
                "-f",
                "lavfi",
                "-i",
                "testsrc=size=320x180:rate=12",
                "-f",
                "lavfi",
                "-i",
                "sine=frequency=880:sample_rate=44100",
                "-t",
                "2",
                "-shortest",
                "-pix_fmt",
                "yuv420p",
                str(self.video),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode:
            self.fail(result.stderr)
        audio_result = subprocess.run(
            [
                ffmpeg,
                "-v",
                "error",
                "-f",
                "lavfi",
                "-i",
                "sine=frequency=440:sample_rate=44100",
                "-t",
                "2",
                str(self.audio),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if audio_result.returncode:
            self.fail(audio_result.stderr)
        self.env = os.environ.copy()
        self.env["SWIPE_ENGINE_REPO_ROOT"] = str(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def command(self, *arguments: str, env: dict[str, str] | None = None) -> dict[str, object]:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            env=env or self.env,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode:
            self.fail(result.stderr)
        return json.loads(result.stdout)

    def failed_command(self, *arguments: str) -> dict[str, object]:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            env=self.env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        return json.loads(result.stderr)

    @contextlib.contextmanager
    def server(self):
        handler = lambda *args, **kwargs: QuietHandler(*args, directory=str(self.fixtures), **kwargs)
        with socketserver.TCPServer(("127.0.0.1", 0), handler) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                yield f"http://127.0.0.1:{server.server_address[1]}"
            finally:
                server.shutdown()
                thread.join()

    def test_all_local_and_url_routes_and_promotion(self) -> None:
        image_manifest = self.command("acquire", str(self.image), "--slug", "local-image")
        self.assertEqual(image_manifest["source_type"], "image")
        self.assertTrue((self.root / str(image_manifest["primary_context"])).is_file())

        duplicate = self.command("acquire", str(self.image), "--slug", "duplicate-image")
        self.assertEqual(duplicate["status"], "duplicate")
        self.assertFalse((self.root / "libraries/swipes/stages/01-save/output/assets/duplicate-image").exists())

        with self.server() as base_url:
            direct = self.command("acquire", f"{base_url}/direct.png", "--slug", "direct-image")
        self.assertEqual(direct["source_type"], "image")

        webpage = self.command(
            "acquire",
            "https://example.test/landing",
            "--slug",
            "webpage-shot",
            "--captured-file",
            str(self.webpage_image),
        )
        self.assertEqual(webpage["source_type"], "webpage")
        self.assertIn("browser-capture", webpage["tools"])

        failed_webpage = self.failed_command(
            "acquire",
            "https://example.test/missing-capture",
            "--slug",
            "failed-webpage",
        )
        self.assertEqual(failed_webpage["status"], "failed")
        self.assertFalse((self.root / "libraries/swipes/stages/01-save/output/assets/failed-webpage").exists())

        pdf = self.command("acquire", str(self.pdf), "--slug", "pdf-reference")
        self.assertEqual(pdf["source_type"], "pdf")
        self.assertTrue(any(item["role"] == "pdf-page" for item in pdf["files"]))
        if {"pdftotext", "pypdf"}.intersection(set(pdf["tools"])):
            self.assertTrue(any(item["role"] == "extracted-text" for item in pdf["files"]))
        else:
            self.assertTrue(any("PDF text extraction unavailable" in item for item in pdf["warnings"]))

        video = self.command(
            "acquire",
            str(self.video),
            "--slug",
            "local-video",
            "--transcript-file",
            str(self.transcript),
        )
        self.assertEqual(video["schema_version"], 3)
        self.assertEqual(video["status"], "staged")
        self.assertEqual(video["workflow_state"], "awaiting-save-approval")
        self.assertFalse(video["ready_for_stage_02"])
        roles = {item["role"] for item in video["files"]}
        self.assertTrue(
            {
                "audio-profile",
                "contact-sheet",
                "frame-index",
                "media-analysis",
                "media-timeline",
                "motion-index",
                "probe",
                "scene-index",
                "source-media",
                "transcript",
                "video-frame",
            }.issubset(roles)
        )
        self.assertTrue(str(video["primary_context"]).endswith("context/contact-sheet.jpg"))
        self.assertTrue(all(not item["persist"] for item in video["files"] if item["role"] == "source-media"))
        self.assertFalse(any("optional transcript unavailable" in item for item in video["warnings"]))
        self.assertFalse(any("frame extraction failed" in item for item in video["warnings"]))

        finalized = self.command(
            "finalize-save",
            str(self.root / "libraries/swipes/stages/01-save/output/assets/local-video/manifest.json"),
            "--title",
            "Local video",
            "--type",
            "social-post",
            "--tags",
            "inspiration,hook",
            "--why-saved",
            "The pacing and hook are useful references.",
            "--human-approved",
        )
        self.assertEqual(finalized["status"], "save-approved")
        self.assertTrue(finalized["intake_record"].endswith("local-video-intake.md"))
        extraction_dir = self.root / "libraries/swipes/stages/02-extract/output"
        extraction_dir.mkdir(parents=True, exist_ok=True)
        (extraction_dir / "local-video-extraction.md").write_text(
            "# Local video extraction\n\n## Visual inspection\n\n- Opened context/contact-sheet.jpg and representative sampled frames with the local image viewer.\n",
            encoding="utf-8",
        )
        missing_handoff = self.failed_command(
            "promote",
            str(self.root / "libraries/swipes/stages/01-save/output/assets/local-video/manifest.json"),
            "--human-approved",
        )
        self.assertIn("stage handoff is missing", missing_handoff["error"])
        (extraction_dir / "local-video-handoff.md").write_text(
            "# Stage Handoff: Local video\n\n"
            "- slug: local-video\n"
            "- stage: 02-extract\n"
            "- state: ready-for-review\n"
            "- completed-at: 2026-07-20T00:00:00Z\n"
            "- next-action: human-review\n"
            "- user-response: approve Stage 02\n\n"
            "## Completed\n\n- Extraction written.\n\n"
            "## Artifacts\n\n- local-video-extraction.md\n\n"
            "## Visual inspection\n\n- Contact sheet opened.\n\n"
            "## Warnings or blockers\n\n- None.\n",
            encoding="utf-8",
        )

        promoted = self.command(
            "promote",
            str(self.root / "libraries/swipes/stages/01-save/output/assets/local-video/manifest.json"),
            "--human-approved",
        )
        self.assertEqual(promoted["status"], "curated")
        self.assertFalse(any(item["role"] == "source-media" for item in promoted["files"]))
        self.assertTrue(any(item["role"] == "media-analysis" for item in promoted["files"]))
        self.assertTrue((self.root / str(promoted["primary_context"])).is_file())
        curated_packages = sorted((self.root / "libraries/swipes/knowledge-layer/assets").glob("*/manifest.json"))
        self.assertEqual([path.parent.name for path in curated_packages], ["local-video"])

    def test_audio_route_with_mocked_whisper(self) -> None:
        mock_bin = self.root / "mock-whisper-bin"
        mock_bin.mkdir()
        mock = mock_bin / "whisper"
        mock.write_text(
            "#!/bin/sh\n"
            "out=''\n"
            "while [ \"$#\" -gt 0 ]; do\n"
            "  if [ \"$1\" = \"--output_dir\" ]; then shift; out=\"$1\"; fi\n"
            "  shift || true\n"
            "done\n"
            "mkdir -p \"$out\"\n"
            "printf '%s\\n' 'Open with the problem. Visit the site to book a call.' > \"$out/transcript.txt\"\n"
            "printf '%s\\n' '{\"text\":\"Open with the problem. Visit the site to book a call.\"}' > \"$out/transcript.json\"\n",
            encoding="utf-8",
        )
        mock.chmod(0o755)
        env = dict(self.env)
        env["PATH"] = f"{mock_bin}{os.pathsep}{env.get('PATH', '')}"
        audio = self.command("acquire", str(self.audio), "--slug", "local-audio", env=env)
        self.assertEqual(audio["source_type"], "audio")
        self.assertEqual(audio["schema_version"], 3)
        self.assertTrue(str(audio["primary_context"]).endswith("context/media-analysis.md"))
        self.assertIn("whisper", audio["tools"])
        roles = {item["role"] for item in audio["files"]}
        self.assertTrue({"audio-profile", "media-analysis", "media-timeline", "probe", "source-media", "transcript"}.issubset(roles))
        analysis = self.root / str(audio["primary_context"])
        self.assertIn("spoken CTA candidates", analysis.read_text(encoding="utf-8"))

        self.command(
            "finalize-save",
            str(self.root / "libraries/swipes/stages/01-save/output/assets/local-audio/manifest.json"),
            "--title",
            "Local audio",
            "--type",
            "other",
            "--tags",
            "inspiration",
            "--why-saved",
            "The opening line is a useful hook reference.",
            "--human-approved",
        )
        extraction_dir = self.root / "libraries/swipes/stages/02-extract/output"
        extraction_dir.mkdir(parents=True, exist_ok=True)
        (extraction_dir / "local-audio-extraction.md").write_text(
            "# Local audio extraction\n\n## Visual inspection\n\n- Not applicable; audio-only source.\n",
            encoding="utf-8",
        )
        (extraction_dir / "local-audio-handoff.md").write_text(
            "# Stage Handoff: Local audio\n\n"
            "- slug: local-audio\n"
            "- stage: 02-extract\n"
            "- state: ready-for-review\n"
            "- completed-at: 2026-07-20T00:00:00Z\n"
            "- next-action: human-review\n"
            "- user-response: approve Stage 02\n\n"
            "## Completed\n\n- Extraction written.\n\n"
            "## Artifacts\n\n- local-audio-extraction.md\n\n"
            "## Visual inspection\n\n- Not applicable.\n\n"
            "## Warnings or blockers\n\n- None.\n",
            encoding="utf-8",
        )

        promoted = self.command(
            "promote",
            str(self.root / "libraries/swipes/stages/01-save/output/assets/local-audio/manifest.json"),
            "--human-approved",
        )
        self.assertEqual(promoted["status"], "curated")
        self.assertFalse(any(item["role"] == "source-media" for item in promoted["files"]))
        self.assertTrue(any(item["role"] == "transcript" for item in promoted["files"]))

    def test_stage_gates_require_explicit_approval(self) -> None:
        manifest = self.command("acquire", str(self.image), "--slug", "approval-gate")
        manifest_path = str(self.root / "libraries/swipes/stages/01-save/output/assets/approval-gate/manifest.json")

        failed_finalize = self.failed_command(
            "finalize-save",
            manifest_path,
            "--title",
            "Approval gate",
            "--type",
            "screenshot",
            "--tags",
            "inspiration",
            "--why-saved",
            "Human reason.",
        )
        self.assertIn("save approval is required", failed_finalize["error"])

        failed_promote = self.failed_command("promote", manifest_path)
        self.assertIn("curation approval is required", failed_promote["error"])

    def test_handoff_check_requires_terminal_contract(self) -> None:
        handoff = self.root / "libraries/swipes/stages/02-extract/output/example-handoff.md"
        handoff.parent.mkdir(parents=True, exist_ok=True)
        handoff.write_text(
            "# Stage Handoff: Example\n\n"
            "- slug: example\n"
            "- stage: 02-extract\n"
            "- state: ready-for-review\n"
            "- completed-at: 2026-07-20T00:00:00Z\n"
            "- next-action: human-review\n"
            "- user-response: approve Stage 02\n\n"
            "## Completed\n\n- Done.\n\n"
            "## Artifacts\n\n- extraction.md\n\n"
            "## Visual inspection\n\n- Contact sheet opened.\n\n"
            "## Warnings or blockers\n\n- None.\n",
            encoding="utf-8",
        )
        checked = self.command(
            "check-handoff",
            str(handoff),
            "--stage",
            "02-extract",
            "--slug",
            "example",
            "--state",
            "ready-for-review",
        )
        self.assertEqual(checked["status"], "valid")
        failed = self.failed_command(
            "check-handoff",
            str(handoff),
            "--stage",
            "03-curate",
            "--slug",
            "example",
        )
        self.assertIn("stage mismatch", failed["error"])

    def test_social_route_with_mocked_downloader(self) -> None:
        mock_bin = self.root / "mock-bin"
        mock_bin.mkdir()
        mock = mock_bin / "yt-dlp"
        args_log = mock_bin / "yt-dlp-args.txt"
        mock.write_text(
            "#!/bin/sh\n"
            f"printf '%s\\n' \"$@\" > {shlex.quote(str(args_log))}\n"
            "while [ \"$1\" != \"-o\" ]; do shift; done\n"
            "shift\n"
            "dir=$(dirname \"$1\")\n"
            "out=$dir/source-mock.mp4\n"
            f"cp '{self.video}' \"$out\"\n"
            "printf '%s\\n' \"$out\"\n",
            encoding="utf-8",
        )
        mock.chmod(0o755)
        env = dict(self.env)
        env["PATH"] = f"{mock_bin}{os.pathsep}{env.get('PATH', '')}"
        social = self.command(
            "acquire",
            "https://www.instagram.com/reel/example/",
            "--slug",
            "social-video",
            "--cookies-from-browser",
            "chrome",
            env=env,
        )
        self.assertEqual(social["source_type"], "social-video")
        self.assertIn("yt-dlp", social["tools"])
        self.assertTrue(any(item["role"] == "contact-sheet" for item in social["files"]))
        yt_dlp_args = args_log.read_text(encoding="utf-8").splitlines()
        self.assertIn("--cookies-from-browser", yt_dlp_args)
        self.assertIn("chrome", yt_dlp_args)

    def test_social_image_carousel_with_mocked_downloader(self) -> None:
        mock_bin = self.root / "mock-carousel-bin"
        mock_bin.mkdir()
        mock = mock_bin / "yt-dlp"
        args_log = mock_bin / "yt-dlp-args.txt"
        mock.write_text(
            "#!/bin/sh\n"
            f"printf '%s\\n' \"$@\" > {shlex.quote(str(args_log))}\n"
            "while [ \"$1\" != \"-o\" ]; do shift; done\n"
            "shift\n"
            "dir=$(dirname \"$1\")\n"
            f"cp '{self.image}' \"$dir/source-one.png\"\n"
            f"cp '{self.direct_image}' \"$dir/source-two.png\"\n"
            "printf '%s\\n' \"$dir/source-one.png\" \"$dir/source-two.png\"\n",
            encoding="utf-8",
        )
        mock.chmod(0o755)
        env = dict(self.env)
        env["PATH"] = f"{mock_bin}{os.pathsep}{env.get('PATH', '')}"
        carousel = self.command(
            "acquire",
            "https://www.instagram.com/p/example/",
            "--slug",
            "social-carousel",
            "--cookies",
            str(self.cookies),
            env=env,
        )
        roles = [item["role"] for item in carousel["files"]]
        self.assertEqual(carousel["source_type"], "social-video")
        self.assertEqual(roles.count("primary-context"), 1)
        self.assertEqual(roles.count("image-reference"), 1)
        self.assertIn("social carousel acquired with 2 images", carousel["warnings"])
        yt_dlp_args = args_log.read_text(encoding="utf-8").splitlines()
        self.assertIn("--cookies", yt_dlp_args)
        self.assertIn(str(self.cookies.resolve()), yt_dlp_args)

    def test_social_cookie_options_are_exclusive(self) -> None:
        failed = self.failed_command(
            "acquire",
            "https://www.instagram.com/reel/example/",
            "--slug",
            "social-cookie-conflict",
            "--cookies",
            str(self.cookies),
            "--cookies-from-browser",
            "chrome",
        )
        self.assertEqual(failed["status"], "failed")
        self.assertIn("use either --cookies or --cookies-from-browser", failed["error"])

    def test_local_fallback_records_failed_social_acquisition(self) -> None:
        fallback = self.command(
            "acquire",
            str(self.video),
            "--slug",
            "manual-social-fallback",
            "--source-type",
            "video",
            "--fallback-source",
            "https://www.instagram.com/reel/private-example/",
            "--fallback-tool",
            "yt-dlp",
            "--fallback-reason",
            "Instagram required authentication, so the reel was downloaded with a Chrome extension.",
            "--fallback-error",
            "ERROR: requested content is not available",
        )

        self.assertEqual(fallback["fallback"]["original_source"], "https://www.instagram.com/reel/private-example/")
        self.assertEqual(fallback["fallback"]["fallback_source"], "fixtures/reference.mp4")
        self.assertEqual(fallback["fallback"]["failed_tool"], "yt-dlp")
        self.assertIn("fallback acquisition recorded after yt-dlp failed", fallback["warnings"])
        note_records = [item for item in fallback["files"] if item["role"] == "fallback-note"]
        self.assertEqual(len(note_records), 1)
        self.assertTrue(note_records[0]["persist"])
        note = self.root / note_records[0]["path"]
        note_text = note.read_text(encoding="utf-8")
        self.assertIn("Original source: https://www.instagram.com/reel/private-example/", note_text)
        self.assertIn("requested content is not available", note_text)

    def test_fallback_metadata_requires_reason(self) -> None:
        failed = self.failed_command(
            "acquire",
            str(self.video),
            "--slug",
            "fallback-missing-reason",
            "--source-type",
            "video",
            "--fallback-source",
            "https://www.instagram.com/reel/private-example/",
        )

        self.assertEqual(failed["status"], "failed")
        self.assertIn("--fallback-reason is required", failed["error"])
        leftovers = list((self.root / "libraries/swipes/stages/01-save/output/assets").glob(".fallback-missing-reason.tmp-*"))
        self.assertEqual(leftovers, [])


if __name__ == "__main__":
    unittest.main()
