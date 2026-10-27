# SOP: Instagram Publishing Safety

Standard process for publishing many similar reels without getting throttled as spam.

## When To Use

- Any run that publishes more than one variant of the same idea.
- Always paired with `reel-split-test.md`. Test design and publishing safety are one job.
- Called at QA, before a cell ships.

## Know Which Risk You Have

Two different Instagram rules get confused. Only one applies here.

| Rule | What it targets | Applies to us? |
|---|---|---|
| Unoriginal content / aggregator penalty | Reposting other people's content with minor edits | **No.** Every asset we publish is generated or produced by us. |
| Near-duplicate throttling | Uploading videos that closely resemble your own earlier uploads | **Yes.** This is the whole risk of split testing. |

Do not let fear of the aggregator penalty drive decisions. It is loud in the press and irrelevant to original creative. The near-duplicate throttle is quieter, less documented, and the one that will actually hit a split-test account.

## Trial Reels Are The Sanctioned Lane

Trial Reels are Instagram's own A/B mechanism. Using them is the difference between testing and spamming.

Confirmed by Meta:

- A trial reel is shown to non-followers first.
- Followers can still stumble on one through a direct message, or a page showing reels with the same audio, location, or filter.
- Results arrive after about 24 hours: views, likes, comments, shares, plus a comparison against previous trials.
- A trial can be shared with everyone manually, or automatically if it performs well within the first 72 hours.

Publish every test package as a trial reel. Publish the winner to everyone. Never publish two versions of the same creative to the main feed.

## The Interleave Rule

Never publish two packages from the same cell on consecutive days.

Keep two cells in flight and alternate:

```text
Mon  Cell A, package 1
Tue  Cell B, package 1
Wed  Cell A, package 2
Thu  Cell B, package 2
```

Every package in a cell shares an identical body and CTA. Back-to-back publishing is the closest thing to a duplicate this system can produce. Interleaving means consecutive uploads never share a spine.

The buffer that makes daily publishing possible falls out of this for free.

## The Differentiation Layer

Variants must differ. The extra difference must not track the thing being tested.

- **Rotate, do not correlate.** Assign music, cover frame, B-roll order, and caption independently of which package it is. Rotated changes add noise. Correlated changes add bias and destroy the result.
- Never assign "the good music" to the package you expect to win.
- Record the delta per package in the variant matrix so bias is visible at the Stage 02 checkpoint.

Because a screening package changes both the visual hook and the text hook, the opening seconds are already substantially different on every upload. The test design does most of the differentiation work. The layer below is insurance.

## Differentiation Checklist

Run before a cell ships. Every package must clear every row.

| Check | Pass Condition |
|---|---|
| Opening visual | The first 3 seconds use a different visual hook clip, not a recrop of another package |
| Opening text | The text hook is different wording, not moved or restyled |
| Cover frame | Each package has its own cover |
| Audio bed | Music differs across packages, assigned by rotation |
| Caption | Written per package, not copy-pasted |
| Body order | B-roll order varies where the beat map allows it |
| Interleave | No two consecutive publish slots share a spine |
| Rotation | No visual/text pairing repeats an earlier cell |

A package that only changes the caption, the cover, or the audio has not been differentiated. Those are the changes the classifier is least likely to weigh.

## If Reach Drops

Symptoms worth acting on:

- A package gets far fewer views than every earlier trial in the same niche.
- Several consecutive packages flatten at once.
- Trial results stop arriving at the usual 24-hour mark.

Response, in order:

1. Stop publishing the affected cell. Do not push more variants into a throttle.
2. Check whether the last packages actually cleared the differentiation checklist.
3. Publish original non-test content for several days. Give the account a clean signal.
4. Resume with a new spine and new hook packages, not the same cell.
5. Log the event on the cell ledger so the pattern is visible later.

Do not delete the posts. Deleting is not a known remedy and it destroys the data.

## Research Confidence

Treat these as separate tiers. Do not harden the bottom tier into policy.

| Claim | Confidence |
|---|---|
| Trial reel mechanics, audience, timing, and promotion | **Confirmed by Meta** |
| Accounts primarily posting unoriginal content lose recommendation eligibility | **Confirmed by Meta**, and not our risk |
| Adding unique text, creative edits, or voiceover makes a work original | **Confirmed by Meta** |
| The first 3 to 7 seconds are compared most closely | Third-party heuristic |
| A ~70 percent visual or audio overlap triggers matching | Third-party heuristic |
| Penalties run 24 hours to 30 days | Third-party heuristic |
| A safe ceiling is about one trial reel per day | Third-party heuristic |
| Caption, cover, and audio changes alone are insufficient | Third-party heuristic |

The heuristics are consistent across independent creator sources, which makes them worth designing around. They are not published policy. Revisit this table when Meta documents the near-duplicate behavior.

## Daily Cadence Note

If every post is a trial, followers see nothing unless a winner is promoted. Because every post is a trial, followers see nothing unless a winner is promoted. Follower-facing volume equals the win rate. If fewer than two winners are promoted to everyone in any rolling two-week window, publish approved non-test content directly so the main feed does not go quiet.

## Output Contract

The calling workspace decides the output path.

The safety output should include:
- the differentiation checklist result per package
- the interleave check across live cells
- the rotation check result
- any throttle event and the response taken

## Not Adopted

- **Deleting posts that underperform.** Named as a risk in the source guide and confirmed here. Losing packages stay up.
- **Spamming identical captions or hashtags across variants.** Captions are written per package.
- **Satellite test accounts.** The source guide recommends testing on secondary accounts and republishing winners to the brand account. Not adopted for now. Trial reels give the same cold-audience read without splitting effort or building an audience twice. Revisit if daily volume ever exceeds what one account can carry.

## Source

Adapted from a third-party Instagram split-testing guide, the Instagram for Creators trial reels documentation, and 2026 reporting on Meta's originality rules.

Third-party reporting is cited, not authoritative. Only the confirmed tier above is treated as policy.
