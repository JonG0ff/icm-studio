#!/usr/bin/env python3
"""Contract, immutable-cache, and real FFprobe coverage; no model is run/downloaded."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
import subprocess
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

import footage_analysis as analysis


def frame(timestamp, duration="0.033333"):
    return {"best_effort_timestamp_time": str(timestamp), "pkt_duration_time": duration}


class NormalizationTests(unittest.TestCase):
    def test_raw_spacing_case_indexes_and_ids_are_preserved(self):
        raw = {"segments": [{"text": "Hello.", "words": [{"word": " Hello.", "start": 0.1, "end": 0.3, "probability": 0.8}]},
                            {"text": "WORLD!", "words": [{"word": " WORLD!", "start": 0.5, "end": 0.7}]}]}
        before = copy.deepcopy(raw)
        words = analysis.normalize_words(raw, "take", 1)
        self.assertEqual(raw, before)
        self.assertEqual(words[0]["text"], " Hello.")
        self.assertEqual(words[1]["text"], " WORLD!")
        self.assertEqual(words[1]["id"], "take:w000001")
        self.assertEqual(words[1]["rawSegmentIndex"], 1)
        self.assertEqual(words[1]["rawWordIndex"], 0)
        self.assertIsNone(words[1]["confidence"])

    def test_malformed_raw_word_times_block_instead_of_interpolating(self):
        for word in ({"word": " a", "end": 0.2}, {"word": " a", "start": "0.1", "end": 0.2},
                     {"word": " a", "start": False, "end": 0.2}, {"word": " a", "start": float("nan"), "end": 0.2}):
            with self.subTest(word=word), self.assertRaises(analysis.AnalysisError):
                analysis.normalize_words({"segments": [{"words": [word]}]}, "take", 1)

    def test_missing_word_timestamps_block(self):
        for raw in ({}, {"segments": [{}]}, {"segments": [{"text": "Speech", "words": []}]}):
            with self.subTest(raw=raw), self.assertRaises(analysis.AnalysisError):
                analysis.normalize_words(raw, "take", 1)

    def test_invalid_numeric_word_times_become_untimed_correction_tasks(self):
        cases = (({"word": " a", "start": 0.1, "end": 0.1}, "zero-length"),
                 ({"word": " a", "start": 0.3, "end": 0.2}, "zero-length"),
                 ({"word": " a", "start": -0.1, "end": 0.2}, "out-of-source"),
                 ({"word": " a", "start": 0.1, "end": 2}, "out-of-source"))
        for word, issue in cases:
            with self.subTest(word=word):
                [result] = analysis.normalize_words({"segments": [{"words": [word]}]}, "take", 1)
                self.assertEqual((result["startSeconds"], result["endSeconds"], result["timingIssue"]), (None, None, issue))
                self.assertEqual(result["text"], " a")

    def test_untimed_words_keep_ids_and_never_shift_neighbors(self):
        raw = {"segments": [{"words": [{"word": " one", "start": 0, "end": 0.5},
                                       {"word": " two", "start": 0.4, "end": 0.6},
                                       {"word": " three", "start": 0.5, "end": 0.7}]},
                            {"words": [{"word": " It", "start": 0.8, "end": 0.8},
                                       {"word": " was", "start": 0.8, "end": 0.9}]}]}
        before = copy.deepcopy(raw)
        words = analysis.normalize_words(raw, "take", 1)
        self.assertEqual(raw, before)
        self.assertEqual([w["id"] for w in words], [f"take:w{i:06d}" for i in range(5)])
        self.assertEqual([w.get("timingIssue") for w in words], [None, "overlap", None, "zero-length", None])
        # Overlap is judged against the previous timed word; the untimed word does not move it.
        self.assertEqual((words[2]["startSeconds"], words[4]["startSeconds"]), (0.5, 0.8))
        self.assertNotIn("timingIssue", words[0])
        self.assertEqual((words[3]["rawSegmentIndex"], words[3]["rawWordIndex"]), (1, 0))

    def test_explicit_no_speech_raw_is_empty(self):
        self.assertEqual(analysis.normalize_words({"segments": []}, "take", 1), [])

    def test_bridge_has_explicit_token_type_and_no_fictional_speaker(self):
        words = analysis.normalize_words({"segments": [{"words": [{"word": " A", "start": 0, "end": 1}]}]}, "take", 1)
        self.assertEqual(analysis.bridge_words({"words": words, "corrections": []}),
                         {"words": [{"type": "word", "text": " A", "start": 0, "end": 1}]})

    def test_bridge_lists_untimed_words_instead_of_inventing_times(self):
        words = analysis.normalize_words({"segments": [{"words": [{"word": " A", "start": 0, "end": 0.4},
                                                                  {"word": " B", "start": 0.5, "end": 0.5}]}]}, "take", 1)
        self.assertEqual(analysis.bridge_words({"words": words, "corrections": []}),
                         {"words": [{"type": "word", "text": " A", "start": 0, "end": 0.4}],
                          "untimedWordIds": ["take:w000001"]})

    def test_canonical_identity_ignores_object_insertion_order_and_cache_key(self):
        left = analysis.canonical_cache_identity("a", {"settings": {"b": 2, "a": 1}, "cacheKey": "ignored", "model": "m"})
        right = analysis.canonical_cache_identity("a", {"model": "m", "settings": {"a": 1, "b": 2}})
        self.assertEqual(analysis.canonical_json(left), analysis.canonical_json(right))

    def test_local_runner_applies_named_alignment_heads_without_named_model_download(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            weights = directory / "medium.en.pt"
            weights.write_bytes(b"not loaded")
            cli = directory / "whisper"
            cli.write_text("import whisper, sys\nwhisper.load_model(sys.argv[sys.argv.index('--model') + 1], device='cpu')\n")
            heads = b"installed named model alignment mask"
            loads, applied = [], []
            fake = types.ModuleType("whisper")
            fake._ALIGNMENT_HEADS = {"medium.en": heads}
            def load_local(name, **kwargs):
                loads.append((name, kwargs))
                if name == "medium.en":
                    raise AssertionError("named loading could download and is forbidden")
                return types.SimpleNamespace(set_alignment_heads=applied.append)
            fake.load_model = load_local
            with mock.patch.dict("sys.modules", {"whisper": fake}), mock.patch("sys.argv", ["runner", "medium.en",
                    hashlib.sha256(heads).hexdigest(), str(cli), "audio.wav", "--model", str(weights)]):
                exec(analysis.WHISPER_LOCAL_RUNNER, {})
            self.assertEqual(loads[0][0], str(weights.resolve()))
            self.assertEqual(applied, [heads])


    def test_cli_setting_args_omit_null_defaults_instead_of_passing_none(self):
        args = analysis.cli_setting_args(analysis.CLI_SETTINGS)
        self.assertNotIn("None", args)
        for name, value in analysis.CLI_SETTINGS.items():
            self.assertEqual(f"--{name}" in args, value is not None, name)
        self.assertEqual(args[args.index("--word_timestamps") + 1], "True")

    @unittest.skipUnless(shutil.which("whisper") or (Path.home() / ".local/bin/whisper").exists(), "installed Whisper CLI required")
    def test_installed_whisper_cli_accepts_setting_args(self):
        # Unloadable local weights fail after argument parsing; nothing downloads.
        whisper = analysis.find_whisper()
        with tempfile.TemporaryDirectory() as temporary:
            weights = Path(temporary) / "not-weights.pt"
            weights.write_bytes(b"not a checkpoint")
            result = subprocess.run([str(whisper), str(Path(temporary) / "missing.wav"), "--model", str(weights),
                                     "--model_dir", temporary, "--output_dir", temporary,
                                     *analysis.cli_setting_args(analysis.CLI_SETTINGS)],
                                    capture_output=True, text=True, timeout=120)
        self.assertNotEqual(result.returncode, 2, result.stderr[-500:])
        self.assertNotIn("error: argument", result.stderr)


class TimingEvidenceTests(unittest.TestCase):
    video = {"r_frame_rate": "30/1", "time_base": "1/15360"}

    def test_cfr_needs_actual_timestamps_not_nominal_rates(self):
        mode, fps, duration, reason = analysis.classify_video(self.video, [frame(0), frame(1 / 30), frame(2 / 30)])
        self.assertEqual(mode, "cfr")
        self.assertAlmostEqual(duration, 0.1)
        self.assertIsNone(reason)
        self.assertEqual(analysis.classify_video(self.video, [frame(0), frame(1 / 30), frame(0.1)])[0], "vfr")

    def test_missing_final_duration_or_timestamp_is_unknown(self):
        self.assertEqual(analysis.classify_video(self.video, [{"pts_time": "0"}])[0], "unknown")
        self.assertEqual(analysis.classify_video(self.video, [{"pkt_duration_time": "0.033333"}])[0], "unknown")

    def test_nonzero_video_origin_blocked(self):
        with self.assertRaisesRegex(analysis.AnalysisError, "origin"):
            analysis.classify_video(self.video, [frame(1), frame(1 + 1 / 30)])

    def test_coarse_time_base_cannot_hide_a_dropped_frame(self):
        video = {"r_frame_rate": "30/1", "time_base": "1/30"}
        self.assertEqual(analysis.classify_video(video, [frame(0), frame(2 / 30), frame(3 / 30)])[0], "vfr")

    def test_audio_origins_and_internal_gaps_are_not_silently_shifted(self):
        audio = {"index": 3, "sample_rate": "48000", "channels": 2}
        frames = [{"pts_time": "0", "nb_samples": 480}, {"pts_time": "0.01", "nb_samples": 480}]
        self.assertEqual(analysis.inspect_audio(audio, frames, 1)["streamIndex"], 3)
        for timestamp in (0.05, -0.01):
            frames[0]["pts_time"] = str(timestamp)
            with self.assertRaisesRegex(analysis.AnalysisError, "origin/gap"):
                analysis.inspect_audio(audio, frames, 1)

    def test_multiple_streams_need_explicit_absolute_index(self):
        streams = [{"index": 0, "codec_type": "video"}, {"index": 2, "codec_type": "audio"},
                   {"index": 4, "codec_type": "audio"}]
        with self.assertRaises(analysis.AnalysisError):
            analysis.selected_stream(streams, "audio", None)
        self.assertEqual(analysis.selected_stream(streams, "audio", 4)["index"], 4)
        with self.assertRaises(analysis.AnalysisError):
            analysis.selected_stream(streams, "audio", 1)


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "local FFmpeg/FFprobe required")
class RealMediaCacheTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.library = tempfile.TemporaryDirectory(prefix="footage-analysis-tests-")
        cls.library_path = Path(cls.library.name)
        cls.media = cls.library_path / "fixture.mp4"
        subprocess.run([shutil.which("ffmpeg"), "-v", "error", "-nostdin", "-f", "lavfi", "-i",
                        "testsrc2=size=160x90:rate=30:duration=1", "-f", "lavfi", "-i",
                        "sine=frequency=440:sample_rate=48000:duration=1", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-shortest", str(cls.media)], check=True)

    @classmethod
    def tearDownClass(cls):
        cls.library.cleanup()

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="footage-analysis-case-")
        self.path = Path(self.directory.name)
        self.source = self.path / "source.mp4"
        shutil.copyfile(self.media, self.source)
        self.sources_path = self.path / "sources.json"
        self.inspect_args = argparse.Namespace(source=str(self.source), out=str(self.sources_path), job_id="test",
            source_id="take-1", runtime_path="assets/test/source.mp4", rights_ref="rights.md",
            video_stream_index=None, audio_stream_index=None, no_audio=False, evidence_dir=str(self.path / "evidence"))
        self.models = self.path / "models"
        self.models.mkdir()
        (self.models / "medium.en.pt").write_bytes(b"mock local weights, never loaded")
        self.transcribe_args = argparse.Namespace(sources=str(self.sources_path), out=str(self.path / "transcript.json"),
            cache_dir=str(self.path / "cache"), model="medium.en", language="en", whisper_bin=None,
            model_dir=str(self.models), bridge_out=str(self.path / "bridge.json"), packed_out=str(self.path / "packed.md"))
        self.raw = b'{ "segments": [{"text":"Hello.","words":[{"word":" Hello.","start":0.1,"end":0.5}]}] }\n'
        self.whisper_calls = []

    def tearDown(self):
        self.directory.cleanup()

    def fake_run(self, command):
        if "/mock/whisper" in command:
            self.whisper_calls.append(command)
            out = Path(command[command.index("--output_dir") + 1])
            (out / "source.json").write_bytes(self.raw)
            return ""
        return self.real_run(command)

    def transcribe(self):
        self.real_run = analysis.run
        with mock.patch.object(analysis, "run", side_effect=self.fake_run), \
             mock.patch.object(analysis, "find_whisper", return_value=Path("/mock/whisper")), \
             mock.patch.object(analysis, "whisper_interpreter", return_value=["/mock/python"]), \
             mock.patch.object(analysis, "whisper_metadata", return_value={"version": "test-version",
                 "alignmentHeadsSha256": {"medium.en": "a" * 64},
                 "decodingDefaults": {"suppress_blank": True}, "transcribeDefaults": {"temperature": [0, 0.2]}}):
            return analysis.transcribe_source(self.transcribe_args)

    def test_real_cfr_probe_and_audio_selection(self):
        result = analysis.inspect_source(self.inspect_args)
        source = result["sources"][0]
        self.assertEqual(source["sha256"], analysis.sha256(self.source))
        self.assertEqual(source["video"]["frameRateMode"], "cfr")
        self.assertEqual(source["video"]["durationInFrames"], 30)
        self.assertEqual(source["audio"][0]["streamIndex"], 1)
        evidence = analysis.read_json(self.sources_path.parent / source["video"]["timingEvidence"])
        self.assertEqual(len(evidence["videoFrames"]["frames"]), 30)
        self.assertTrue(evidence["audioFrames"]["frames"])

    def test_outputs_cannot_overwrite_original_inputs_or_each_other(self):
        self.inspect_args.out = str(self.source)
        with self.assertRaisesRegex(analysis.AnalysisError, "overwrite source"):
            analysis.inspect_source(self.inspect_args)
        self.inspect_args.out = str(self.sources_path)
        analysis.inspect_source(self.inspect_args)
        self.transcribe_args.out = str(self.source)
        with self.assertRaisesRegex(analysis.AnalysisError, "distinct"):
            self.transcribe()
        self.transcribe_args.out = str(self.path / "transcript.json")
        self.transcribe_args.bridge_out = self.transcribe_args.out
        with self.assertRaisesRegex(analysis.AnalysisError, "distinct"):
            self.transcribe()

    def test_transcription_is_local_cache_hit_is_immutable_and_packer_connected(self):
        analysis.inspect_source(self.inspect_args)
        first = self.transcribe()
        raw = Path(self.transcribe_args.out).parent / first["rawResult"]["path"]
        self.assertEqual(raw.read_bytes(), self.raw)
        before = raw.stat().st_mtime_ns
        second = self.transcribe()
        self.assertEqual(first, second)
        self.assertEqual(len(self.whisper_calls), 1)
        self.assertEqual(raw.stat().st_mtime_ns, before)
        self.assertEqual(first["words"][0]["text"], " Hello.")
        self.assertEqual(first["verification"], {"status": "automatic"})
        command = self.whisper_calls[0]
        self.assertEqual(command[command.index("--model") + 1], str((self.models / "medium.en.pt").resolve()))
        self.assertIn("--word_timestamps", command)
        self.assertEqual(analysis.read_json(self.path / "bridge.json")["words"][0]["type"], "word")
        self.assertIn("Full media duration: 1.000000s", (self.path / "packed.md").read_text())
        self.assertIn("speech span:", (self.path / "packed.md").read_text())
        self.assertEqual(first["analysis"]["cacheKey"], hashlib.sha256(analysis.canonical_json(
            analysis.canonical_cache_identity(first["sourceSha256"], first["analysis"])).encode()).hexdigest())

    def test_cache_raw_tamper_is_blocked(self):
        analysis.inspect_source(self.inspect_args)
        result = self.transcribe()
        raw = self.path / result["rawResult"]["path"]
        raw.write_bytes(b"{}")
        with self.assertRaisesRegex(analysis.AnalysisError, "SHA-256 mismatch"):
            self.transcribe()
        self.assertEqual(len(self.whisper_calls), 1)

    def test_reviewed_transcript_is_never_overwritten_on_cache_hit(self):
        analysis.inspect_source(self.inspect_args)
        transcript = self.transcribe()
        for reviewed in ({**transcript, "corrections": [{"wordId": "take-1:w000000", "text": " Hi."}]},
                         {**transcript, "verification": {"status": "partial"}},
                         {**transcript, "verification": {"status": "verified"}}):
            analysis.write_json(self.transcribe_args.out, reviewed)
            before = Path(self.transcribe_args.out).read_bytes()
            with self.assertRaisesRegex(analysis.AnalysisError, "reviewed decisions"):
                self.transcribe()
            self.assertEqual(Path(self.transcribe_args.out).read_bytes(), before)
        self.assertEqual(len(self.whisper_calls), 1)

    def test_cache_pcm_tamper_is_blocked(self):
        analysis.inspect_source(self.inspect_args)
        result = self.transcribe()
        raw = self.path / result["rawResult"]["path"]
        (raw.parent / "source.wav").write_bytes(b"tampered")
        with self.assertRaisesRegex(analysis.AnalysisError, "PCM SHA-256 mismatch"):
            self.transcribe()

    def test_different_model_weights_create_new_analysis_identity(self):
        analysis.inspect_source(self.inspect_args)
        first = self.transcribe()
        (self.models / "medium.en.pt").write_bytes(b"changed weights")
        second = self.transcribe()
        self.assertNotEqual(first["analysis"]["cacheKey"], second["analysis"]["cacheKey"])
        self.assertEqual(len(self.whisper_calls), 2)

    def test_missing_model_does_not_run_or_download(self):
        analysis.inspect_source(self.inspect_args)
        (self.models / "medium.en.pt").unlink()
        with self.assertRaisesRegex(analysis.AnalysisError, "downloads are disabled"):
            self.transcribe()
        self.assertFalse(self.whisper_calls)

    def test_changed_source_is_blocked_before_running_whisper(self):
        analysis.inspect_source(self.inspect_args)
        self.source.write_bytes(b"changed")
        with self.assertRaisesRegex(analysis.AnalysisError, "SHA-256 mismatch"):
            self.transcribe()
        self.assertFalse(self.whisper_calls)

    def test_invalid_recognition_raw_is_preserved_and_never_interpolated(self):
        analysis.inspect_source(self.inspect_args)
        self.raw = b'{"segments":[{"text":"x","words":[{"word":" x","start":0.1}]}]}\n'
        with self.assertRaises(analysis.AnalysisError):
            self.transcribe()
        raws = list((self.path / "cache").glob("*/raw.json"))
        self.assertEqual(len(raws), 1)
        self.assertEqual(raws[0].read_bytes(), self.raw)
        self.assertFalse((self.path / "transcript.json").exists())
        with self.assertRaises(analysis.AnalysisError):
            self.transcribe()
        self.assertEqual(len(self.whisper_calls), 1)

    def test_no_audio_selection_blocks_transcription(self):
        self.inspect_args.no_audio = True
        analysis.inspect_source(self.inspect_args)
        with self.assertRaisesRegex(analysis.AnalysisError, "exactly one selected audio stream"):
            self.transcribe()

    def test_real_vfr_timestamps_are_rejected_with_probe_evidence(self):
        vfr = self.path / "vfr.mp4"
        subprocess.run([shutil.which("ffmpeg"), "-v", "error", "-nostdin", "-i", str(self.source),
                        "-vf", "setpts='if(lt(N,15),N/(30*TB),(15+(N-15)*2)/(30*TB))'",
                        "-fps_mode", "vfr", "-an", "-c:v", "libx264", str(vfr)], check=True)
        self.inspect_args.source = str(vfr)
        with self.assertRaisesRegex(analysis.AnalysisError, "vfr"):
            analysis.inspect_source(self.inspect_args)
        evidence = list((self.path / "evidence").glob("probe*.json"))
        self.assertTrue(evidence)
        self.assertEqual(analysis.read_json(evidence[0])["classification"]["frameRateMode"], "vfr")

    def test_real_multiple_audio_tracks_require_absolute_selection_and_map(self):
        multiple = self.path / "two-audio.mp4"
        subprocess.run([shutil.which("ffmpeg"), "-v", "error", "-nostdin", "-i", str(self.source),
                        "-f", "lavfi", "-i", "sine=frequency=900:sample_rate=48000:duration=1",
                        "-map", "0:v", "-map", "0:a", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", str(multiple)], check=True)
        self.inspect_args.source = str(multiple)
        with self.assertRaisesRegex(analysis.AnalysisError, "absolute|select exactly"):
            analysis.inspect_source(self.inspect_args)
        self.inspect_args.audio_stream_index = 2
        result = analysis.inspect_source(self.inspect_args)
        self.assertEqual(result["sources"][0]["audio"][0]["streamIndex"], 2)
        transcript = self.transcribe()
        self.assertEqual(transcript["analysis"]["audioStreamIndex"], 2)


if __name__ == "__main__":
    unittest.main()
