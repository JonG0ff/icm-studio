# OpenEdit pure utilities

`speech-probe.ts` adopts `envelopeOf`, `percentile`, `analyse`, their result types and `MIN_DYNAMIC_RANGE_DB`. `edl.ts` adopts `snapToFrames` and its range types. There are no CLI, provider, decoder, filesystem or mapper imports.

The PCM adapter must supply mono signed 16-bit PCM and pass the actual window duration to `analyse`: `windowSamples * 1000 / sampleRate`, after rounding the requested window to whole samples. It must preserve the source range offset. Trailing partial windows remain omitted.

Gap results are energy-based candidates. They do not prove silence or a safe semantic cut. Flat and empty inputs return no speech onset, decay or gaps. Listening review remains necessary.

Local changes:

- Reject nonfinite values and invalid positive window/gap/frame settings. PCM windows must be positive safe integers to prevent nonadvancing loops.
- Reject negative source offsets and invalid ranges.
- Replace `findLastIndex` with an equivalent reverse scan for the runtime's ES2015 library declarations.
- Label gaps as candidates in the result documentation.
- Reconcile one upstream flat-signal test with the implementation. Its original `Math.abs(onset - 0)` passed with null through JavaScript coercion. The port explicitly requires null and `speechFound: false`.

Run from `remotion/`:

```sh
node --test src/lib/upstream/open-edit/regression.test.mjs
```

The adopted tests cover pure analysis and frame snapping, plus CMP invalid-input and long-envelope regressions. Upstream CLI/FFmpeg and full suites were not run. The complete upstream LICENSE and NOTICE are retained; this subset includes no fonts or hosted service integration. See `upstream.json` for hashes and verification.
