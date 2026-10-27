#!/usr/bin/env python3
"""Local selected-footage inspection and immutable Whisper analysis cache.

No model downloads, hosted providers, script alignment, or invented word times.
The initial adapter accepts full, zero-origin CFR sources only. CLI stream
selectors use absolute FFprobe stream indexes, including for FFmpeg -map.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import wave
from fractions import Fraction
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
DEFAULT_EVIDENCE = REPO / "remotion/.cache/footage-analysis"


class AnalysisError(ValueError):
    """An actionable local analysis blocker."""


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def canonical_cache_identity(source_sha256, analysis):
    return {"sourceSha256": source_sha256, **{key: value for key, value in analysis.items() if key != "cacheKey"}}


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Replace a complete artifact atomically; never leave half-written JSON.
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def read_json(path):
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle, parse_constant=lambda value: (_ for _ in ()).throw(AnalysisError(f"invalid JSON number {value}")))


def relative(path, artifact):
    return os.path.relpath(Path(path).resolve(), Path(artifact).resolve().parent)


def run(command):
    result = subprocess.run([str(item) for item in command], capture_output=True, text=True)
    if result.returncode:
        raise AnalysisError(f"{Path(command[0]).name} failed: {result.stderr.strip()[-1500:]}")
    return result.stdout


def executable(name):
    found = shutil.which(name)
    if not found:
        raise AnalysisError(f"{name} not found on PATH")
    return found


def require_local_evidence(path):
    """Repository-local bulky evidence must be ignored. External local paths work."""
    path = Path(path).resolve()
    if path.is_relative_to(REPO):
        result = subprocess.run(["git", "check-ignore", "-q", "--", str(path / "raw.json")], cwd=REPO)
        if result.returncode:
            raise AnalysisError(f"bulky evidence/cache directory must be Git-ignored: {path}")
    path.mkdir(parents=True, exist_ok=True)
    return path


def number(value, name, nonnegative=True):
    if isinstance(value, bool):
        raise AnalysisError(f"{name}: finite number required")
    try:
        value = float(value)
    except (TypeError, ValueError):
        raise AnalysisError(f"{name}: finite number required") from None
    if not math.isfinite(value) or (nonnegative and value < 0):
        raise AnalysisError(f"{name}: finite nonnegative number required")
    return value


def positive_int(value, name, zero=False):
    if isinstance(value, bool) or not re.fullmatch(r"\d+", str(value)):
        raise AnalysisError(f"{name}: integer required")
    result = int(value)
    if result < (0 if zero else 1):
        raise AnalysisError(f"{name}: {'nonnegative' if zero else 'positive'} integer required")
    return result


def rate(value, name):
    try:
        result = Fraction(value)
    except (ValueError, ZeroDivisionError, TypeError):
        raise AnalysisError(f"{name}: positive rational required") from None
    if result <= 0:
        raise AnalysisError(f"{name}: positive rational required")
    return result


def selected_stream(streams, kind, explicit, optional=False):
    candidates = [stream for stream in streams if stream.get("codec_type") == kind]
    if explicit is not None:
        candidates = [stream for stream in candidates if stream.get("index") == explicit]
        if len(candidates) != 1:
            raise AnalysisError(f"no {kind} stream with absolute index {explicit}")
    if not candidates and optional:
        return None
    if len(candidates) != 1:
        raise AnalysisError(f"select exactly one {kind} stream with --{kind}-stream-index (found {len(candidates)})")
    return candidates[0]


def probe_frames(source, index):
    return json.loads(run([executable("ffprobe"), "-v", "error", "-select_streams", str(index),
                           "-show_frames", "-show_entries",
                           "frame=stream_index,best_effort_timestamp_time,pts_time,duration_time,pkt_duration_time,nb_samples",
                           "-of", "json", source]))


def frame_time(frame):
    return number(frame.get("best_effort_timestamp_time", frame.get("pts_time")), "decoded frame timestamp", False)


def classify_video(video, frames):
    """Prove a complete CFR grid from decoded timestamps, including the last duration."""
    fps = rate(video.get("r_frame_rate"), "video frame rate")
    time_base = rate(video.get("time_base"), "video time base")
    period = float(1 / fps)
    # Absolute PTS rounds to one half-tick; intervals/durations can differ by
    # one tick. Keep these separate so a coarse time base cannot hide drops.
    tolerance = max(float(time_base) * 0.51, 0.000002)
    interval_tolerance = max(float(time_base) * 1.01, 0.000002)
    if not frames:
        return "unknown", fps, None, "no decoded frame timestamps"
    try:
        timestamps = [frame_time(frame) for frame in frames]
    except AnalysisError:
        return "unknown", fps, None, "missing/invalid decoded frame timestamps"
    if abs(timestamps[0]) > 0.000002:
        raise AnalysisError("nonzero video time origin is unsupported; normalize with an explicit time mapping")
    # Compare each actual adjacent interval. Nominal/average agreement is insufficient.
    if any(right <= left or abs((right - left) - period) > interval_tolerance for left, right in zip(timestamps, timestamps[1:])):
        return "vfr", fps, None, "decoded presentation intervals depart from the declared CFR grid"
    durations = []
    for frame in frames:
        raw = frame.get("duration_time", frame.get("pkt_duration_time"))
        if raw is None:
            durations.append(None)
        else:
            durations.append(number(raw, "decoded frame duration"))
    if durations[-1] is None:
        return "unknown", fps, None, "last decoded frame duration missing"
    if any(duration is not None and (duration <= 0 or abs(duration - period) > interval_tolerance) for duration in durations):
        return "vfr", fps, None, "decoded frame durations depart from the declared CFR grid"
    # Catch accumulated drift that individual time-base tolerances could mask.
    if any(abs(timestamp - index * period) > tolerance for index, timestamp in enumerate(timestamps)):
        return "vfr", fps, None, "decoded timestamps drift from the declared CFR grid"
    end = timestamps[-1] + durations[-1]
    if abs(end - len(frames) * period) > tolerance:
        return "vfr", fps, None, "last frame ends outside the CFR grid"
    return "cfr", fps, len(frames) * period, None


def inspect_audio(stream, frames, source_duration):
    sample_rate = positive_int(stream.get("sample_rate"), "audio sample rate")
    if not frames:
        raise AnalysisError("selected audio has no decoded timestamp/sample evidence")
    tolerance = max(0.000002, 1.01 / sample_rate)
    cursor = 0.0
    for index, frame in enumerate(frames):
        start = frame_time(frame)
        if abs(start - cursor) > (0.000002 if index == 0 else tolerance):
            raise AnalysisError("audio origin/gap is unsupported; normalize with an explicit time mapping")
        cursor += positive_int(frame.get("nb_samples"), "decoded audio sample count") / sample_rate
    if cursor > source_duration + max(tolerance, 0.05):
        raise AnalysisError("audio extends beyond picture; an explicit source mapping is required")
    return {"streamIndex": positive_int(stream["index"], "audio stream index", True),
            "sampleRate": sample_rate, "channels": positive_int(stream.get("channels"), "audio channels")}


def inspect_source(args):
    source = Path(args.source).resolve(strict=True)
    out = Path(args.out).resolve()
    if out == source:
        raise AnalysisError("sources output must not overwrite source media")
    if not source.is_file() or not args.job_id.strip() or not args.source_id.strip():
        raise AnalysisError("readable source and nonempty job/source IDs required")
    runtime = args.runtime_path
    if not re.fullmatch(r"assets/[A-Za-z0-9_./-]+", runtime) or any(part in {"", ".", ".."} for part in runtime.split("/")):
        raise AnalysisError("runtime path must be a safe relative assets/... path")
    if not args.rights_ref.strip() or Path(args.rights_ref).is_absolute():
        raise AnalysisError("rights-ref must be a nonempty path relative to sources.json")
    original_hash = sha256(source)
    evidence_dir = require_local_evidence(Path(args.evidence_dir) if args.evidence_dir else DEFAULT_EVIDENCE / original_hash)
    facts = json.loads(run([executable("ffprobe"), "-v", "error", "-show_streams", "-show_format", "-of", "json", source]))
    streams = facts.get("streams", [])
    video = selected_stream(streams, "video", args.video_stream_index)
    audio = None if args.no_audio else selected_stream(streams, "audio", args.audio_stream_index, True)
    video_frames = probe_frames(source, video["index"])
    audio_frames = probe_frames(source, audio["index"]) if audio else {"frames": []}
    evidence = {"sourceSha256": original_hash, "probe": facts, "videoFrames": video_frames,
                "audioFrames": audio_frames, "selectedVideoStreamIndex": video["index"],
                "selectedAudioStreamIndex": audio["index"] if audio else None,
                "timeOriginPolicy": "require decoded picture/audio to begin at zero; never silently shift"}
    evidence_path = evidence_dir / f"probe-v{video['index']}-a{audio['index'] if audio else 'none'}.json"
    if evidence_path in {source, out}:
        raise AnalysisError("probe evidence must be separate from source media and sources output")
    # Retain the actual probe even when an unsupported origin blocks classification.
    write_json(evidence_path, evidence)
    mode, fps, duration, reason = classify_video(video, video_frames.get("frames", []))
    evidence["classification"] = {"frameRateMode": mode, "reason": reason}
    write_json(evidence_path, evidence)
    if mode != "cfr":
        raise AnalysisError(f"{mode} video: {reason}; normalize before selected-footage compilation (evidence: {evidence_path})")
    for stream in [video] + ([audio] if audio else []):
        if number(stream.get("start_time", 0), "stream start_time", False) != 0:
            raise AnalysisError("nonzero stream origin is unsupported; retain an explicit time mapping before normalization")
    audio_info = [inspect_audio(audio, audio_frames.get("frames", []), duration)] if audio else []
    if sha256(source) != original_hash:
        raise AnalysisError("source changed during inspection; retry with immutable local media")
    result = {"schemaVersion": 1, "artifactType": "sources", "jobId": args.job_id, "sources": [{
        "id": args.source_id, "sha256": original_hash, "localPath": relative(source, out),
        "runtimePath": runtime, "durationSeconds": duration, "kind": "recorded",
        "video": {"streamIndex": positive_int(video["index"], "video stream index", True),
                  "width": positive_int(video.get("width"), "video width"),
                  "height": positive_int(video.get("height"), "video height"),
                  "fpsNumerator": fps.numerator, "fpsDenominator": fps.denominator,
                  "timeBase": video["time_base"], "durationInFrames": len(video_frames["frames"]),
                  "frameRateMode": mode, "timingEvidence": relative(evidence_path, out)},
        "audio": audio_info, "rightsRef": args.rights_ref}]}
    write_json(out, result)
    return result


def find_whisper(explicit=None):
    fallback = Path.home() / ".local/bin/whisper"
    candidate = explicit or shutil.which("whisper") or (str(fallback) if fallback.exists() else None)
    if not candidate:
        raise AnalysisError("whisper CLI not found; install openai-whisper or pass --whisper-bin")
    resolved = Path(candidate).expanduser().resolve(strict=True)
    if not os.access(resolved, os.X_OK):
        raise AnalysisError(f"Whisper executable is not executable: {resolved}")
    return resolved


ENGINE_QUERY = r'''
import ast, hashlib, importlib.metadata, json
dist = importlib.metadata.distribution("openai-whisper")
def literal_defaults(filename, target):
    tree = ast.parse(dist.locate_file("whisper/" + filename).read_text())
    node = next(n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and n.name == target)
    if isinstance(node, ast.ClassDef):
        return {n.target.id: ast.literal_eval(n.value) for n in node.body if isinstance(n, ast.AnnAssign) and n.value is not None}
    return {n.arg: ast.literal_eval(v) for n, v in zip(node.args.kwonlyargs, node.args.kw_defaults) if v is not None}
tree = ast.parse(dist.locate_file("whisper/__init__.py").read_text())
heads = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == "_ALIGNMENT_HEADS" for t in n.targets))
print(json.dumps({"version": dist.version,
    "alignmentHeadsSha256": {key: hashlib.sha256(value).hexdigest() for key, value in heads.items()},
    "decodingDefaults": literal_defaults("decoding.py", "DecodingOptions"),
    "transcribeDefaults": literal_defaults("transcribe.py", "transcribe")}))
'''


def whisper_interpreter(whisper):
    with Path(whisper).open("rb") as handle:
        first = handle.readline().decode("utf-8").strip()
    if not first.startswith("#!"):
        raise AnalysisError("Whisper CLI must expose its Python interpreter in a shebang")
    interpreter = shlex.split(first[2:])
    if not interpreter or Path(interpreter[0]).name == "env":
        raise AnalysisError("Whisper interpreter is ambiguous; use a local Python entry point with an absolute shebang")
    return interpreter


def whisper_metadata(whisper):
    """Query package metadata with the CLI's interpreter, never the system Python."""
    interpreter = whisper_interpreter(whisper)
    metadata = json.loads(run([*interpreter, "-c", ENGINE_QUERY]))
    if not isinstance(metadata.get("version"), str) or not metadata["version"]:
        raise AnalysisError("installed openai-whisper version could not be established")
    return metadata


# Loading by local file never enters Whisper's download branch. Apply the same
# installed alignment-head mask as loading by model name, then execute the
# discovered official CLI. Otherwise a local-path model silently gets a different
# default word-alignment mask. No hosted endpoint or model acquisition is used.
WHISPER_LOCAL_RUNNER = r'''
import hashlib, pathlib, runpy, sys, whisper
model_name, heads_sha256, cli = sys.argv[1:4]
args = sys.argv[4:]
weights = pathlib.Path(args[args.index("--model") + 1]).resolve(strict=True)
heads = whisper._ALIGNMENT_HEADS[model_name]
if hashlib.sha256(heads).hexdigest() != heads_sha256:
    raise RuntimeError("alignment configuration changed")
original_load_model = whisper.load_model
def load_local(name, device=None, download_root=None, in_memory=False):
    if pathlib.Path(name).resolve() != weights:
        raise RuntimeError("only explicit local model loading is allowed")
    model = original_load_model(str(weights), device=device, download_root=download_root, in_memory=in_memory)
    model.set_alignment_heads(heads)
    return model
whisper.load_model = load_local
sys.argv = [cli, *args]
runpy.run_path(cli, run_name="__main__")
'''


# Every supported CLI decoding/transcription option is explicit. Intrinsic API
# defaults are also read from the installed package and included in identity.
CLI_SETTINGS = {
    "device": "cpu", "task": "transcribe", "temperature": 0.0, "best_of": 5,
    "beam_size": 5, "patience": 1.0, "length_penalty": None,
    "suppress_tokens": "-1", "initial_prompt": None, "carry_initial_prompt": False,
    "condition_on_previous_text": True, "fp16": False,
    "temperature_increment_on_fallback": 0.2, "compression_ratio_threshold": 2.4,
    "logprob_threshold": -1.0, "no_speech_threshold": 0.6, "word_timestamps": True,
    "prepend_punctuations": "\"'“¿([{-", "append_punctuations": "\"'.。,，!！?？:：”)]}、",
    "highlight_words": False, "max_line_width": None, "max_line_count": None,
    "max_words_per_line": None, "threads": 1, "clip_timestamps": "0",
    "hallucination_silence_threshold": None, "verbose": False,
}



def cli_setting_args(settings):
    """Every null setting is that option's CLI default. Some options parse as
    plain float/str, so omit them rather than pass the literal string None."""
    return [part for name, value in settings.items() if value is not None
            for part in (f"--{name}", str(value))]

def normalize_words(raw, source_id, duration):
    if not isinstance(raw, dict) or not isinstance(raw.get("segments"), list):
        raise AnalysisError("raw Whisper result requires segments[]")
    words, previous_end = [], 0.0
    for segment_index, segment in enumerate(raw["segments"]):
        if not isinstance(segment, dict) or not isinstance(segment.get("words"), list):
            raise AnalysisError(f"segment {segment_index}: missing word timestamps; raw output retained")
        if segment.get("text", "").strip() and not segment["words"]:
            raise AnalysisError(f"segment {segment_index}: speech has no word timestamps; raw output retained")
        for word_index, word in enumerate(segment["words"]):
            if not isinstance(word, dict) or not isinstance(word.get("word"), str) or not word["word"].strip():
                raise AnalysisError("every raw word needs nonempty text; raw output retained")
            if any(isinstance(word.get(key), bool) or not isinstance(word.get(key), (int, float)) for key in ("start", "end")):
                raise AnalysisError("raw word timestamps must be JSON numbers; raw output retained")
            start = number(word.get("start"), "word start", False)
            end = number(word.get("end"), "word end", False)
            probability = word.get("probability")
            if probability is not None:
                probability = number(probability, "word probability")
                if probability > 1:
                    raise AnalysisError("word probability outside [0, 1]")
            record = {"id": f"{source_id}:w{len(words):06d}", "rawSegmentIndex": segment_index,
                      "rawWordIndex": word_index, "text": word["word"],
                      "startSeconds": start, "endSeconds": end, "confidence": probability}
            # Keep the recognized word and its ID, but never invent timing. A
            # listening correction must supply bounds before it can be selected.
            issue = ("out-of-source" if start < 0 or end > duration else "zero-length" if end <= start
                     else "overlap" if start < previous_end else None)
            if issue:
                record.update(startSeconds=None, endSeconds=None, timingIssue=issue)
            else:
                previous_end = end
            words.append(record)
    if not words and isinstance(raw.get("text"), str) and raw["text"].strip():
        raise AnalysisError("raw speech has no word timestamps; raw output retained")
    return words


def bridge_words(transcript):
    """Derive the imported helper view; corrections require the contract validator."""
    if transcript.get("corrections"):
        raise AnalysisError("apply and validate reviewed corrections before deriving the helper view")
    result = {"words": [{"type": "word", "text": word["text"], "start": word["startSeconds"],
                         "end": word["endSeconds"]} for word in transcript["words"] if "timingIssue" not in word]}
    untimed = [word["id"] for word in transcript["words"] if "timingIssue" in word]
    return {**result, "untimedWordIds": untimed} if untimed else result


def transcribe_source(args):
    sources_path = Path(args.sources).resolve(strict=True)
    sources = read_json(sources_path)
    if (not isinstance(sources, dict) or type(sources.get("schemaVersion")) is not int or sources["schemaVersion"] != 1
            or sources.get("artifactType") != "sources" or not isinstance(sources.get("jobId"), str)
            or not sources["jobId"].strip()):
        raise AnalysisError("expected sources artifact schemaVersion 1 with a jobId")
    if not isinstance(sources.get("sources"), list) or len(sources["sources"]) != 1:
        raise AnalysisError("initial transcription adapter requires one selected source")
    source = sources["sources"][0]
    if not isinstance(source.get("id"), str) or not source["id"].strip():
        raise AnalysisError("source requires a stable nonempty id")
    source_path = (sources_path.parent / source["localPath"]).resolve(strict=True)
    outputs = [Path(path).resolve() for path in (args.out, args.bridge_out, args.packed_out) if path]
    cache_root_path = Path(args.cache_dir).resolve()
    if len(set(outputs)) != len(outputs) or any(path in {source_path, sources_path} or path.is_relative_to(cache_root_path) for path in outputs):
        raise AnalysisError("transcript/bridge/packed outputs must be distinct, outside the immutable cache, and separate from source inputs")
    if Path(args.out).exists():
        existing = read_json(args.out)
        if (not isinstance(existing, dict) or existing.get("artifactType") != "transcript"
                or existing.get("corrections") or not isinstance(existing.get("verification"), dict)
                or existing["verification"].get("status") != "automatic"):
            raise AnalysisError("output contains reviewed decisions; use the existing transcript directly or choose a new --out path")
    if sha256(source_path) != source.get("sha256"):
        raise AnalysisError("source SHA-256 mismatch; inspect the current bytes before transcription")
    duration = number(source.get("durationSeconds"), "source duration")
    if duration <= 0 or source.get("video", {}).get("frameRateMode") != "cfr":
        raise AnalysisError("full-source transcription requires a positive-duration inspected CFR source")
    if not isinstance(source.get("audio"), list) or len(source["audio"]) != 1:
        raise AnalysisError("transcription requires exactly one selected audio stream; no-audio/no-speech branches are explicit")
    audio_index = positive_int(source["audio"][0]["streamIndex"], "audio stream index", True)
    if not isinstance(args.language, str) or not args.language.strip():
        raise AnalysisError("make language explicit (for example --language en)")
    if args.model.endswith(".en") and args.language != "en":
        raise AnalysisError("English-only models require --language en")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", args.model):
        raise AnalysisError("model must be an installed model name; choose its local directory with --model-dir")
    model_dir = Path(args.model_dir).expanduser() if args.model_dir else Path(os.getenv("XDG_CACHE_HOME", Path.home() / ".cache")) / "whisper"
    weights = (model_dir / f"{args.model}.pt").resolve()
    if not weights.is_file():
        raise AnalysisError(f"local model weights missing: {weights}; downloads are disabled")
    if weights in outputs:
        raise AnalysisError("analysis outputs must not overwrite model weights")
    whisper = find_whisper(args.whisper_bin)
    metadata = whisper_metadata(whisper)
    alignment_hash = metadata.get("alignmentHeadsSha256", {}).get(args.model)
    if not alignment_hash:
        raise AnalysisError(f"installed Whisper has no named alignment configuration for {args.model}")
    settings = {**CLI_SETTINGS, "decodingDefaults": metadata["decodingDefaults"],
                "transcribeDefaults": metadata["transcribeDefaults"],
                "modelLoading": {"mode": "local-file-with-installed-named-alignment-heads",
                                 "alignmentHeadsSha256": alignment_hash,
                                 "runnerSha256": hashlib.sha256(WHISPER_LOCAL_RUNNER.encode()).hexdigest()},
                "audioExtraction": {"codec": "pcm_s16le", "sampleRate": 16000, "channels": 1,
                                    "origin": "source-zero", "ffmpegVersion": run([executable("ffmpeg"), "-version"]).splitlines()[0]}}
    analysis = {"engine": "openai-whisper", "engineVersion": metadata["version"], "model": args.model,
                "modelWeightSha256": sha256(weights), "language": args.language, "settings": settings,
                "audioStreamIndex": audio_index, "rangeStartSeconds": 0, "rangeEndSeconds": duration}
    identity = canonical_cache_identity(source["sha256"], analysis)
    cache_key = hashlib.sha256(canonical_json(identity).encode("utf-8")).hexdigest()
    cache_root = require_local_evidence(args.cache_dir)
    entry = cache_root / cache_key
    raw_path, manifest_path = entry / "raw.json", entry / "cache.json"
    if entry.exists():
        if not manifest_path.is_file() or not raw_path.is_file():
            raise AnalysisError(f"incomplete immutable cache entry: {entry}; inspect it before retrying")
        cache = read_json(manifest_path)
        if cache.get("identity") != identity or cache.get("rawSha256") != sha256(raw_path):
            raise AnalysisError(f"cache identity/raw SHA-256 mismatch: {entry}")
        if not (entry / "source.wav").is_file() or cache.get("pcmSha256") != sha256(entry / "source.wav"):
            raise AnalysisError(f"cache PCM SHA-256 mismatch: {entry}")
    else:
        # Work separately, then publish a complete immutable entry. Raw is copied
        # byte-for-byte before any normalization, including invalid recognition.
        with tempfile.TemporaryDirectory(prefix=".analysis-", dir=cache_root) as temporary:
            temporary = Path(temporary)
            pcm = temporary / "source.wav"
            facts = json.loads(run([executable("ffprobe"), "-v", "error", "-show_streams", "-of", "json", source_path]))
            selected = selected_stream(facts.get("streams", []), "audio", audio_index)
            if number(selected.get("start_time", 0), "audio start_time", False) != 0:
                raise AnalysisError("nonzero audio origin is unsupported; no silent timestamp reset")
            audio_frames = probe_frames(source_path, audio_index)
            inspect_audio(selected, audio_frames.get("frames", []), duration)
            run([executable("ffmpeg"), "-v", "error", "-nostdin", "-i", source_path, "-map", f"0:{audio_index}",
                 "-vn", "-t", str(duration), "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", pcm])
            with wave.open(str(pcm), "rb") as handle:
                pcm_samples, pcm_rate = handle.getnframes(), handle.getframerate()
            if pcm_rate != 16000 or pcm_samples <= 0 or pcm_samples / pcm_rate > duration + 0.05:
                raise AnalysisError("decoded PCM duration is unsupported; retain source mapping before transcription")
            command = [str(whisper), str(pcm), "--model", str(weights), "--model_dir", str(model_dir),
                       "--language", args.language, "--output_format", "json", "--output_dir", str(temporary)]
            command.extend(cli_setting_args(CLI_SETTINGS))
            run([*whisper_interpreter(whisper), "-c", WHISPER_LOCAL_RUNNER, args.model, alignment_hash, *command])
            produced = temporary / "source.json"
            if not produced.is_file():
                raise AnalysisError("Whisper did not write its expected JSON result")
            if sha256(source_path) != source["sha256"] or sha256(weights) != analysis["modelWeightSha256"]:
                raise AnalysisError("source/model changed during transcription; result is not reusable")
            published = temporary / "publish"
            published.mkdir()
            shutil.copyfile(produced, published / "raw.json")
            shutil.copyfile(pcm, published / "source.wav")
            write_json(published / "audio-evidence.json", {"sourceOffsetSeconds": 0,
                       "sampleRate": pcm_rate, "sampleCount": pcm_samples,
                       "actualDurationSeconds": pcm_samples / pcm_rate,
                       "sourceSha256": source["sha256"], "audioStreamIndex": audio_index,
                       "decodedAudioFrames": audio_frames})
            write_json(published / "cache.json", {"identity": identity, "rawSha256": sha256(published / "raw.json"),
                       "pcmSha256": sha256(published / "source.wav")})
            try:
                published.rename(entry)
            except OSError as exc:
                raise AnalysisError(f"cache entry changed concurrently; retry after checking {entry}") from exc
    raw = read_json(raw_path)
    words = normalize_words(raw, source["id"], duration)
    if sha256(source_path) != source["sha256"]:
        raise AnalysisError("source changed while loading analysis; retry with immutable local media")
    out = Path(args.out).resolve()
    result = {"schemaVersion": 1, "artifactType": "transcript", "jobId": sources["jobId"],
              "sourceId": source["id"], "sourceSha256": source["sha256"],
              "analysis": {**analysis, "cacheKey": cache_key},
              "rawResult": {"path": relative(raw_path, out), "sha256": sha256(raw_path)},
              "verification": {"status": "automatic"}, "words": words, "corrections": []}
    write_json(out, result)
    bridge = bridge_words(result)
    if args.bridge_out:
        write_json(args.bridge_out, bridge)
    if args.packed_out:
        spec = importlib.util.spec_from_file_location("adopted_transcript_packer", Path(__file__).parent / "vendor/video-use/pack_transcripts.py")
        packer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(packer)
        phrases = packer.group_into_phrases(bridge["words"], 0.5)
        timed = bridge["words"]
        span = timed[-1]["end"] - timed[0]["start"] if timed else 0
        markdown = packer.render_markdown([(source["id"], span, phrases)], 0.5)
        markdown += f"\nFull media duration: {duration:.6f}s. Recognition is automatic; listening review is required.\n"
        if bridge.get("untimedWordIds"):
            markdown += f"Untimed recognized words (omitted above; correction required): {', '.join(bridge['untimedWordIds'])}.\n"
        Path(args.packed_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.packed_out).write_text(markdown, encoding="utf-8")
    return result


def parser():
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="operation", required=True)
    inspect = commands.add_parser("inspect", help="inspect one zero-origin CFR source")
    for field in ("source", "job-id", "source-id", "runtime-path", "rights-ref", "out"):
        inspect.add_argument(f"--{field}", required=True)
    inspect.add_argument("--video-stream-index", type=int)
    audio = inspect.add_mutually_exclusive_group()
    audio.add_argument("--audio-stream-index", type=int)
    audio.add_argument("--no-audio", action="store_true")
    inspect.add_argument("--evidence-dir")
    transcribe = commands.add_parser("transcribe", help="transcribe one source using local installed Whisper weights")
    for field in ("sources", "out", "cache-dir", "model", "language"):
        transcribe.add_argument(f"--{field}", required=True)
    for field in ("whisper-bin", "model-dir", "bridge-out", "packed-out"):
        transcribe.add_argument(f"--{field}")
    return root


def main():
    root = parser()
    args = root.parse_args()
    try:
        result = inspect_source(args) if args.operation == "inspect" else transcribe_source(args)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        root.exit(2, f"analysis blocked: {exc}\n")
    print(json.dumps({"artifactType": result["artifactType"], "out": str(Path(args.out).resolve())}))


if __name__ == "__main__":
    main()
