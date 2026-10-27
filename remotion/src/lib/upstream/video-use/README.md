# video-use caption grouping port

`chunk-words.ts` ports only `chunk_words` and its constants. It groups objects by punctuation, pauses and duration. It preserves each retained object, raw text, case, IDs and timing. Blank words are omitted, as upstream does. No SRT writer or renderer is included.

Times are original source seconds with exclusive ends. CMP adapters own IDs, corrections, cut boundaries and output mapping. Nonblank words require finite nonnegative start times and end times after start times. This is the only added behavior for invalid timings.

Run from `remotion/`:

```sh
node --test src/lib/upstream/video-use/regression.test.mjs
```

The six upstream grouping cases are ported, including the real TAKE timing fixture. Two CMP cases cover immutable object identity, exact text and invalid timing. Upstream SRT, path and renderer tests are outside this import. See `upstream.json` for pinned source hashes and verification.
