# Whisper Model and CPU Fallback (Mode B)

`build_words.py` calls the `whisper` CLI with `--word_timestamps True --fp16 False`. English-only models also get `--language en`.

## Default

- `medium.en` on CPU.
- It has not crashed on any setup we have used.
- About 1 minute of audio per 1 minute of wall clock on a modern laptop.
- Needs about 4 GB of free RAM.
- First run downloads about 1.5 GB to `~/.cache/whisper`.

## Faster Options

- `small.en` is quicker and usually fine for clean studio voice.
- `large-v3` is more accurate but slow on CPU.
- Avoid `tiny.en` and `base.en` for final timing. Word edges get noisy.

## GPU

The CLI picks CUDA when it can. `large-v3` on GPU has crashed on some driver combos. Signs:

- Process exits with no stack trace.
- `cudaErrorIllegalAddress` on the first batch.
- Process hangs after the model loads.

If any of these happen, rerun with `--whisper-model medium.en`. Do not fight the driver on a deadline.

## Memory

| Model | Approx size |
|---|---|
| `tiny.en` | 500 MB |
| `base.en` | 600 MB |
| `small.en` | 1 GB |
| `medium.en` | 2.5 GB |
| `large-v3` | 5 GB plus GPU VRAM |
