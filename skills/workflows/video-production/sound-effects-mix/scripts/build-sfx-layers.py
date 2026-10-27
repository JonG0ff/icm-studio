#!/usr/bin/env python3
"""Build deliverable SFX stems for a run without any manual download step.

The Pixabay packet script (``source-pixabay-sfx.py``) is human-in-the-loop by
design: Pixabay's sound-effects downloads are tokenised per browser session, so
it can only emit search links and a selection template. That leaves a run with
markdown and no audio.

This script closes that gap. It resolves every layer in an SFX config to an
actual WAV stem using, in order of preference:

1. ``library`` sources  - real audio already in the local media library.
2. ``synth`` sources    - deterministic ffmpeg synthesis, for beds like room
                          tone where synthesis is standard practice anyway.

Every stem is written at the config's sample rate / bit depth and normalised to
a single reference peak, so the editor sets the mix with faders rather than
inheriting whatever level the source happened to have. A provenance report
records exactly where each stem came from and which ones are placeholder-grade.

Usage:
    python3 build-sfx-layers.py --config layers.json --out ./audio/sfx
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MAX_VOLUME_PATTERN = re.compile(r"max_volume:\s*(-?\d+(?:\.\d+)?)\s*dB")


class BuildError(Exception):
    """Raised when a layer cannot be produced."""


@dataclass(frozen=True)
class AudioFormat:
    sample_rate: int
    bit_depth: int
    target_peak_dbfs: float

    @property
    def codec(self) -> str:
        codecs = {16: "pcm_s16le", 24: "pcm_s24le", 32: "pcm_s32le"}
        if self.bit_depth not in codecs:
            raise BuildError(f"Unsupported bit depth: {self.bit_depth}")
        return codecs[self.bit_depth]


def run_ffmpeg(args: list[str]) -> str:
    """Run ffmpeg and return stderr. Raises BuildError on a non-zero exit."""
    completed = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostdin", "-y", *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        tail = "\n".join(completed.stderr.strip().splitlines()[-8:])
        raise BuildError(f"ffmpeg failed:\n{tail}")
    return completed.stderr


def measure_peak_dbfs(path: Path) -> float:
    stderr = run_ffmpeg(["-i", str(path), "-af", "volumedetect", "-f", "null", "-"])
    match = MAX_VOLUME_PATTERN.search(stderr)
    if not match:
        raise BuildError(f"Could not read peak level from {path.name}")
    return float(match.group(1))


def fade_filter(duration: float, fade: float) -> str:
    """Symmetric fade in/out, clamped so short one-shots are not swallowed."""
    fade = min(fade, duration / 3)
    return f"afade=t=in:st=0:d={fade:.3f},afade=t=out:st={duration - fade:.3f}:d={fade:.3f}"


def build_library_layer(spec: dict[str, Any], library: Path, duration: float) -> list[str]:
    """Input + filter args for a layer sourced from a real library file."""
    source = library / str(spec["file"])
    if not source.exists():
        raise BuildError(f"Library file not found: {source}")

    mode = spec.get("mode", "loop")
    filters: list[str] = []

    if highpass := spec.get("highpass"):
        filters.append(f"highpass=f={highpass}")
    if lowpass := spec.get("lowpass"):
        filters.append(f"lowpass=f={lowpass}")

    if mode == "loop":
        inputs = ["-stream_loop", "-1", "-i", str(source), "-t", f"{duration:.3f}"]
    elif mode == "oneshot":
        # Pad rather than truncate: a one-shot shorter than its cue window still
        # has to fill the window so the declared fade-out lands on real samples.
        inputs = ["-i", str(source), "-t", f"{duration:.3f}"]
        filters.append("apad")
    elif mode == "pattern":
        # Repeated short hits at explicit offsets — used to build UI-swipe beds
        # out of a single real whoosh rather than faking the texture entirely.
        offsets = [float(value) for value in spec["offsets"]]
        hit_length = float(spec.get("hit_length", 0.3))
        inputs = []
        legs = []
        for index, offset in enumerate(offsets):
            inputs += ["-i", str(source)]
            chain = f"atrim=0:{hit_length:.3f},asetpts=PTS-STARTPTS"
            if highpass := spec.get("highpass"):
                chain += f",highpass=f={highpass}"
            chain += f",{fade_filter(hit_length, 0.04)}"
            chain += f",adelay={int(offset * 1000)}|{int(offset * 1000)}"
            legs.append(f"[{index}:a]{chain}[h{index}]")
        mix = "".join(f"[h{i}]" for i in range(len(offsets)))
        # amix ends with its longest input, which leaves the stem short of the
        # cue window; apad holds it out to the declared duration so the file
        # drops onto the timeline aligned.
        graph = (
            ";".join(legs)
            + f";{mix}amix=inputs={len(offsets)}:normalize=0,apad,"
            f"aformat=channel_layouts=stereo[out]"
        )
        return inputs + ["-filter_complex", graph, "-map", "[out]", "-t", f"{duration:.3f}"]
    else:
        raise BuildError(f"Unknown library mode: {mode}")

    filters.append("aformat=channel_layouts=stereo")
    return inputs + ["-af", ",".join(filters)]


def build_synth_layer(spec: dict[str, Any], duration: float) -> list[str]:
    """Input + filter args for a deterministically synthesised layer."""
    recipe = spec["recipe"]
    seed = int(spec.get("seed", 42))

    if recipe == "room_tone":
        # Brown noise rolled off hard, plus a faint mains-adjacent hum. This is
        # how room tone is built for real when no clean recording exists.
        cutoff = float(spec.get("cutoff", 420))
        hum_hz = float(spec.get("hum_hz", 62))
        graph = (
            f"anoisesrc=color=brown:seed={seed}:duration={duration:.3f}:sample_rate=48000[n];"
            f"sine=frequency={hum_hz}:duration={duration:.3f}:sample_rate=48000[h];"
            f"[n]lowpass=f={cutoff},highpass=f=28[nf];"
            f"[h]volume=0.05[hf];"
            f"[nf][hf]amix=inputs=2:normalize=0,"
            f"aformat=channel_layouts=stereo[out]"
        )
    elif recipe == "paper_foley":
        # Bandpassed noise gated by an irregular tremolo reads as pencil/paper
        # movement. Placeholder-grade: swap for a real recording when possible.
        graph = (
            f"anoisesrc=color=white:seed={seed}:duration={duration:.3f}:sample_rate=48000[n];"
            f"[n]bandpass=f=2600:width_type=o:w=2.2,"
            f"tremolo=f=7.3:d=0.92,"
            f"tremolo=f=1.7:d=0.75,"
            f"aformat=channel_layouts=stereo[out]"
        )
    else:
        raise BuildError(f"Unknown synth recipe: {recipe}")

    return ["-filter_complex", graph, "-map", "[out]"]


def build_layer(
    layer: dict[str, Any],
    library: Path,
    out_dir: Path,
    audio: AudioFormat,
) -> dict[str, Any]:
    layer_id = str(layer["id"])
    duration = float(layer["duration"])
    spec = layer["source"]
    kind = spec["type"]

    if kind == "library":
        args = build_library_layer(spec, library, duration)
        provenance = f"library:{spec['file']}"
    elif kind == "synth":
        args = build_synth_layer(spec, duration)
        provenance = f"synth:{spec['recipe']}"
    else:
        raise BuildError(f"Unknown source type: {kind}")

    raw = out_dir / f".{layer_id}.raw.wav"
    final = out_dir / f"{layer_id}.wav"

    run_ffmpeg([*args, "-ar", str(audio.sample_rate), "-c:a", audio.codec, str(raw)])

    # One reference peak across every stem: the timeline's dB values are fader
    # positions, not baked-in levels.
    peak = measure_peak_dbfs(raw)
    gain = audio.target_peak_dbfs - peak
    post = f"volume={gain:.2f}dB,{fade_filter(duration, float(layer.get('fade', 0.2)))}"

    run_ffmpeg(
        ["-i", str(raw), "-af", post, "-ar", str(audio.sample_rate), "-c:a", audio.codec, str(final)]
    )
    raw.unlink()

    return {
        "id": layer_id,
        "scene": layer.get("scene", ""),
        "file": final.name,
        "duration_s": duration,
        "provenance": provenance,
        "mix_db": layer.get("mix_db"),
        "grade": spec.get("grade", "delivery"),
        "rights": layer.get("rights", "unrecorded"),
        "note": layer.get("note", ""),
    }


def write_report(records: list[dict[str, Any]], out_dir: Path, project: str) -> Path:
    lines = [
        f"# SFX Stems - {project}",
        "",
        "Built by `build-sfx-layers.py`. Levels are normalised to a single",
        "reference peak; apply the mix column as a fader value in the NLE.",
        "",
        "| Layer | Scene | File | Length | Mix | Source | Rights | Grade |",
        "|-------|-------|------|--------|-----|--------|--------|-------|",
    ]
    for record in records:
        mix = f"{record['mix_db']}dB" if record["mix_db"] is not None else "—"
        lines.append(
            f"| `{record['id']}` | {record['scene']} | `{record['file']}` "
            f"| {record['duration_s']:.1f}s | {mix} | {record['provenance']} "
            f"| {record['rights']} | {record['grade']} |"
        )

    placeholders = [record for record in records if record["grade"] == "placeholder"]
    if placeholders:
        lines += ["", "## Replace before final mix", ""]
        for record in placeholders:
            lines.append(f"- `{record['id']}` — {record['note']}")

    unconfirmed = [
        record
        for record in records
        if "confirm" in str(record["rights"]).lower() or record["rights"] == "unrecorded"
    ]
    if unconfirmed:
        lines += ["", "## Confirm licence before publishing", ""]
        for record in unconfirmed:
            lines.append(f"- `{record['id']}` — {record['rights']}")

    report = out_dir / "sfx-stems.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Build SFX stems from local library audio and synthesis.")
    parser.add_argument("--config", required=True, help="Layer config JSON")
    parser.add_argument("--out", required=True, help="Output directory for stems")
    parser.add_argument("--library", required=True, help="Local media library root for library sources")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: config not found: {config_path}", file=sys.stderr)
        raise SystemExit(1)

    config = json.loads(config_path.read_text(encoding="utf-8"))
    library = Path(args.library)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    audio = AudioFormat(
        sample_rate=int(config.get("sample_rate", 48000)),
        bit_depth=int(config.get("bit_depth", 24)),
        target_peak_dbfs=float(config.get("target_peak_dbfs", -6.0)),
    )

    records: list[dict[str, Any]] = []
    failures: list[str] = []

    for layer in config["layers"]:
        layer_id = layer.get("id", "<unnamed>")
        try:
            records.append(build_layer(layer, library, out_dir, audio))
            print(f"  built {layer_id}")
        except BuildError as error:
            failures.append(f"{layer_id}: {error}")
            print(f"  FAILED {layer_id}: {error}", file=sys.stderr)

    if records:
        report = write_report(records, out_dir, str(config.get("project", "untitled")))
        print(f"\n{len(records)} stem(s) -> {out_dir}")
        print(f"report -> {report}")

    if failures:
        print(f"\n{len(failures)} layer(s) failed.", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
