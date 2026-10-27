# Line Matching (Mode B)

How `build_words.py` maps Whisper words back to script lines.

## Why Not a Straight Diff

- Whisper drops or re-spells words.
- Speakers elide contractions.
- People ad-lib or repeat a word.
- A strict diff breaks on all of these. Sequence alignment with fuzzy words does not.

## Steps

1. Take the script lines for the variant, in order.
2. Remove `[audio tags]`. Split into words.
3. Normalize both sides: lower case, drop apostrophes, drop punctuation.
4. Align the full script word list to the full Whisper word list with `difflib.SequenceMatcher`.
5. Equal runs map one to one.
6. Replaced runs map by position. A pair counts as a match if similarity is 0.6 or more.
7. Script words with no partner get time between their matched neighbours.
8. A line is found when at least half its words matched.
9. Found lines take their span from the first and last word.

## Re-spelling

Output words always use the script spelling. Whisper only supplies the time. A pair that differs after normalizing is listed in the report as `script 'Ada' heard 'Aida'`.

## When a Line Is NOT FOUND

Try these in order:

1. Read the notes. A line with few words may just miss the 50 percent bar.
2. Listen to the track near the neighbouring lines. Was it spoken?
3. If the speaker changed the words, update the script to match the take.
4. If the take is missing, record or generate that line again.

Do not hand-enter times for a NOT FOUND line. Downstream scenes trust `words.json`.

## Writing Script Lines That Match Well

- Spell numbers the way they will be spoken, or expect mismatch notes.
- Avoid very short lines made of filler words. They are easy to lose.
- Keep the script in spoken order. The aligner does not reorder lines.
