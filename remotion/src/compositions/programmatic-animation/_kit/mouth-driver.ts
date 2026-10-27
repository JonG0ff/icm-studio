/**
 * Shared mouth driver: turns word timings (from ElevenLabs alignment) into
 * one of the 8 shared mouth shapes for any frame. Every character uses the
 * same shape names; see rig-conventions.md.
 */
export type MouthShape = "rest" | "mbp" | "ee" | "ah" | "oh" | "oo" | "fv" | "l";

export type WordTiming = {
  text: string;
  /** Seconds from the start of the line or scene. */
  start: number;
  end: number;
};

/** Fallback flap when a word has no readable letters. */
const FLAP: readonly MouthShape[] = ["ah", "ee", "mbp", "oh"];

/** Letter clusters checked longest first. */
const CLUSTERS: ReadonlyArray<readonly [string, MouthShape]> = [
  ["th", "l"],
  ["oo", "oo"],
  ["ou", "oh"],
  ["ee", "ee"],
  ["m", "mbp"],
  ["b", "mbp"],
  ["p", "mbp"],
  ["f", "fv"],
  ["v", "fv"],
  ["l", "l"],
  ["o", "oh"],
  ["u", "oo"],
  ["w", "oo"],
  ["a", "ah"],
  ["e", "ee"],
  ["i", "ee"],
  ["y", "ee"],
];

/** Visible shapes for one word, consecutive duplicates collapsed. */
export const visemesForWord = (text: string): MouthShape[] => {
  const letters = text.toLowerCase().replace(/[^a-z]/g, "");
  const shapes: MouthShape[] = [];
  let i = 0;
  while (i < letters.length) {
    const match = CLUSTERS.find(([cluster]) => letters.startsWith(cluster, i));
    if (match) {
      if (shapes[shapes.length - 1] !== match[1]) shapes.push(match[1]);
      i += match[0].length;
    } else {
      i += 1;
    }
  }
  return shapes.length > 0 ? shapes : [...FLAP];
};

/** Seconds of speech allowed per letter before the rest is treated as silence. */
const SECONDS_PER_LETTER = 0.09;
const WORD_TAIL_SECONDS = 0.25;

/**
 * Alignment often stretches a line's last word across the silence after it.
 * Cap each word to a plausible spoken length so the mouth closes in time.
 */
const spokenEnd = (word: WordTiming): number => {
  const letters = word.text.replace(/[^a-zA-Z]/g, "").length;
  return Math.min(word.end, word.start + letters * SECONDS_PER_LETTER + WORD_TAIL_SECONDS);
};

/** Mouth shape at a time in seconds. Silence between words is `rest`. */
export const mouthAtTime = (words: readonly WordTiming[], time: number): MouthShape => {
  const word = words.find((w) => time >= w.start && time < spokenEnd(w));
  if (!word) return "rest";
  const shapes = visemesForWord(word.text);
  const progress = (time - word.start) / Math.max(spokenEnd(word) - word.start, 1e-3);
  return shapes[Math.min(shapes.length - 1, Math.floor(progress * shapes.length))];
};

/**
 * Mouth shape at a frame, held on `step` frames so the mouth animates on
 * twos with the rest of the look.
 */
export const mouthAtFrame = (words: readonly WordTiming[], frame: number, fps: number, step = 2): MouthShape =>
  mouthAtTime(words, (Math.floor(frame / step) * step) / fps);
