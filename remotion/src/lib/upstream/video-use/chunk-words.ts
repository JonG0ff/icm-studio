// Port of Browser Use video-use helpers/render.py:chunk_words at
// 43cfc566833548093455c9d4a46bd69913b7e552. MIT; see LICENSE and upstream.json.

export const CHUNK_WORDS = 2;
export const CHUNK_MAX_WORDS = 3;
export const CHUNK_MIN_S = 0.35;
export const CHUNK_PAUSE_S = 0.3;
export const PUNCT_BREAK = new Set(".,!?;:");

export interface CaptionWord {
  text?: string | null;
  start: number;
  end: number;
}

/** Group only: original words, case, IDs, timing and object references survive. */
export function chunkWords<T extends CaptionWord>(input: readonly T[]): T[][] {
  const words = input.filter((word) => (word.text || "").trim());
  const chunks: T[][] = [];
  let current: T[] = [];
  for (let i = 0; i < words.length; i++) {
    const word = words[i];
    if (!Number.isFinite(word.start) || !Number.isFinite(word.end) || word.start < 0 || word.end <= word.start) {
      throw new Error("caption words require finite ordered nonnegative source seconds");
    }
    current.push(word);
    const text = word.text!.trim();
    const next = words[i + 1];
    const gap = next ? next.start - word.end : 0;
    const duration = word.end - current[0].start;
    if (!next || PUNCT_BREAK.has(text[text.length - 1]) || gap >= CHUNK_PAUSE_S
      || current.length >= CHUNK_MAX_WORDS
      || (current.length >= CHUNK_WORDS && duration >= CHUNK_MIN_S)) {
      chunks.push(current);
      current = [];
    }
  }
  return chunks;
}
