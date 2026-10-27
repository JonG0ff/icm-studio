"""Local regression and synthetic FFmpeg smoke checks; no hosted services."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image, ImageDraw

import pack_transcripts as pack
import timeline_view as timeline


def word(text, start, end, speaker="speaker_0"):
    return {"type": "word", "text": text, "start": start, "end": end, "speaker_id": speaker}


class PackingTests(unittest.TestCase):
    def test_pause_speaker_punctuation_and_span(self):
        words = [word("Hi", 10, 10.2), word(",", 10.2, 10.3),
                 word("there", 10.3, 10.6), word("Next", 11.1, 11.4),
                 word("speaker", 11.4, 11.8, "speaker_1")]
        phrases = pack.group_into_phrases(words)
        self.assertEqual([p["text"] for p in phrases], ["Hi, there", "Next", "speaker"])
        self.assertEqual(phrases[0]["start"], 10)
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "take.json"
            source.write_text(json.dumps({"words": words}))
            entry = pack.pack_one_file(source, 0.5)
            self.assertAlmostEqual(entry[1], 1.8)
            markdown = pack.render_markdown([entry], 0.5)
            self.assertIn("speech span: 1.8s", markdown)
            self.assertIn("full media duration is unknown", markdown)
            self.assertNotIn("total runtime", markdown)

    def test_spacing_events_and_empty(self):
        words = [word("Hi", 0, .2), {"type": "spacing", "start": .2, "end": 1},
                 {"type": "audio_event", "text": "laugh", "start": 1, "end": 1.2}]
        self.assertEqual([p["text"] for p in pack.group_into_phrases(words)], ["Hi", "(laugh)"])
        self.assertEqual(pack.group_into_phrases([]), [])

    def test_invalid_words_and_thresholds(self):
        for token in [{"text": "implicit", "start": 0, "end": 1},
                      word("nan", float("nan"), 1), word("infinity", 0, float("inf")),
                      word("reversed", 1, 0), word("negative", -1, 0),
                      word("zero", 1, 1),
                      {"type": "word", "text": "missing", "start": 0}]:
            with self.subTest(token=token), self.assertRaises(ValueError):
                pack.group_into_phrases([token])
        with self.assertRaisesRegex(ValueError, "nonoverlapping"):
            pack.group_into_phrases([word("one", 0, 1), word("two", .5, 1.5)])
        for threshold in [0, -1, float("nan")]:
            with self.assertRaises(ValueError):
                pack.group_into_phrases([], threshold)

    def test_edl_rejected(self):
        result = subprocess.run([sys.executable, str(Path(timeline.__file__)), "--edl", "unused.json"], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--edl mode is not implemented", result.stderr)


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg tools required")
class TimelineSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.video = cls.root / "fixture.mkv"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=320x180:rate=10:duration=2",
                        "-f", "lavfi", "-i", "anullsrc=r=16000:cl=mono:d=2",
                        "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=16000:duration=2",
                        "-map", "0:v", "-map", "1:a", "-map", "2:a", "-c:v", "mpeg4", "-c:a", "pcm_s16le", str(cls.video)], check=True)
        cls.transcript = cls.root / "transcript.json"
        cls.transcript.write_text(json.dumps({"words": [word("Hello", .3, .6), word("world", 1.2, 1.6)]}))
        cls.one_second = cls.root / "one-second-30fps.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=320x180:rate=30:duration=1",
                        "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=16000:duration=1",
                        "-map", "0:v", "-map", "1:a", "-c:v", "mpeg4", "-c:a", "aac", str(cls.one_second)], check=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_selected_audio_and_full_range_envelope(self):
        silent = timeline.compute_envelope(self.video, 0, 2, samples=20, audio_track=0)
        tone = timeline.compute_envelope(self.video, 0, 2, samples=20, audio_track=1)
        np.testing.assert_array_equal(silent, np.zeros(20))
        self.assertEqual(len(tone), 20)
        self.assertTrue(np.all(np.isfinite(tone)))
        self.assertTrue(np.all(tone > .9))

    def test_final_frame_covers_bin_center_after_its_presentation_timestamp(self):
        # The final .975s center belongs to frame 29 at 29/30s; seeking .975s
        # directly discards that frame and previously produced no JPEG.
        samples = timeline.sample_frames(self.one_second, .5, 1, 10, self.root / "final-half-second")
        self.assertEqual(len(samples), 10)
        self.assertAlmostEqual(samples[-1][1], 29 / 30)
        self.assertTrue(all(.5 <= pts < 1 for _, pts in samples))
        reference = self.root / "known-frame-29.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(self.one_second), "-map", "0:v:0",
                        "-frames:v", "1", "-q:v", "4", "-vf", "select=eq(n\\,29),scale=320:-2", str(reference)], check=True)
        self.assertEqual(samples[-1][0].read_bytes(), reference.read_bytes())
        labels = []
        original = ImageDraw.ImageDraw.text

        def record(draw, xy, text, *args, **kwargs):
            labels.append(text)
            return original(draw, xy, text, *args, **kwargs)

        with patch.object(ImageDraw.ImageDraw, "text", record), contextlib.redirect_stdout(io.StringIO()):
            timeline.render_timeline(self.one_second, .5, 1, self.root / "final-half-second.png", 10, None)
        self.assertIn("PTS 0.966667s", labels)
        self.assertTrue(any("0.50s → 1.00s" in text for text in labels))

    def test_b_frame_reorder_cannot_hide_frames_before_a_mid_file_range_end(self):
        # H.264 B-frames reorder output; a probe that stops reading packets at
        # the range end drops the final in-range frames (seen on a real
        # 24000/1001 clip with has_b_frames=2).
        video = self.root / "bframes-ntsc.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=320x180:rate=24000/1001:duration=3",
                        "-c:v", "libx264", "-bf", "2", "-pix_fmt", "yuv420p", str(video)], check=True)
        fps = 24000 / 1001
        samples = timeline.sample_frames(video, 0, 44 / fps, 44, self.root / "bframes")
        self.assertEqual(len(samples), 44)
        for index, (path, pts) in enumerate(samples):
            self.assertTrue(path.is_file())
            self.assertAlmostEqual(pts, index / fps)
        self.assertTrue(all(0 <= pts < 44 / fps for _, pts in samples))

    def test_one_frame_range_repeats_the_covering_frame_with_actual_timestamp(self):
        samples = timeline.sample_frames(self.one_second, 29 / 30, 1, 10, self.root / "one-frame")
        self.assertEqual(len(samples), 10)
        self.assertEqual(len({path for path, _ in samples}), 1)
        for path, pts in samples:
            self.assertTrue(path.is_file())
            self.assertAlmostEqual(pts, 29 / 30)
        # A subframe request still uses its covering frame, whose actual PTS is
        # shown explicitly; the requested ruler/waveform range stays .99..1.
        subframe = timeline.sample_frames(self.one_second, .99, 1, 1, self.root / "subframe")
        self.assertAlmostEqual(subframe[0][1], 29 / 30)

    def test_filmstrip_waveform_and_word_labels(self):
        output = self.root / "range.png"
        labels = []
        original = ImageDraw.ImageDraw.text

        def record(draw, xy, text, *args, **kwargs):
            labels.append(text)
            return original(draw, xy, text, *args, **kwargs)

        with patch.object(ImageDraw.ImageDraw, "text", record), contextlib.redirect_stdout(io.StringIO()):
            timeline.render_timeline(self.video, 0, 2, output, 3, self.transcript, audio_track=1)
        with Image.open(output) as image:
            self.assertEqual(image.size, (1920, 540))
            self.assertGreater(np.asarray(image.crop((50, 50, 300, 200))).std(), 10)
            wave = np.asarray(image.crop((50, 250, 900, 470)))
            self.assertGreater(wave.std(), 10)
        self.assertIn("Hello", labels)
        self.assertIn("world", labels)
        self.assertTrue(any("audio 1" in text for text in labels))
        self.assertTrue(any("not verified silence" in text for text in labels))

    def test_invalid_ranges_tracks_counts_and_transcript(self):
        for start, end in [(-1, 1), (1, 1), (2, 1), (0, 3), (float("nan"), 1), (0, float("inf"))]:
            with self.subTest(start=start, end=end), self.assertRaises(ValueError):
                timeline.validate_media(self.video, start, end)
        for track in [-1, 2, True]:
            with self.assertRaises(ValueError):
                timeline.compute_envelope(self.video, 0, 1, audio_track=track)
        with self.assertRaises(ValueError):
            timeline.render_timeline(self.video, 0, 1, self.root / "bad.png", 0, None)
        with self.assertRaises(FileNotFoundError):
            timeline.words_in_range(self.root / "missing.json", 0, 1)

    def test_no_audio_and_empty_decoded_audio_fail(self):
        video_only = self.root / "video-only.mkv"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(self.video), "-map", "0:v", "-c", "copy", str(video_only)], check=True)
        with self.assertRaisesRegex(ValueError, "0 audio tracks"):
            timeline.compute_envelope(video_only, 0, 1)
        # An empty decoded segment must not masquerade as a silent waveform.
        with patch("wave.Wave_read.readframes", return_value=b""), self.assertRaisesRegex(ValueError, "no PCM samples"):
            timeline.compute_envelope(self.video, 0, 1)


if __name__ == "__main__":
    unittest.main()
