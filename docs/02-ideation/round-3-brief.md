# Round 3 brief — final vote (all roles)

Round 2 is finished. The 58 raw ideas are merged into **20 consolidated features F01–F20**, ranked by
peer score, with the reviewers' consensus, red flags and gaps. Now each role casts a final vote and
proposes the MVP cut for the demo.

**Time context:** Saturday 14 Nov, ~02:00. About 20 build hours for a very small team with AI coding
agents; final submission Sunday 15 Nov 10:00; the City of Espoo mentors are available on Saturday from 09:00.

## Read (in this order)

1. `docs/03-product/feature-catalog.md` — F01–F20, the Round 2 ranking and consensus.
2. `docs/00-challenge/tech-challenges.md` and `docs/01-research/05-junction-2026-tech-partners.md` —
   tech challenges we can stack on the Espoo track (core candidates: Nemotron 3.5 Super VL, Modal,
   Gemma; Codex for the build).
3. `docs/01-research/06-prior-art-open-source.md` — what already exists.
4. Your own Round 2 review in `docs/02-ideation/round-2-reviews/`.

Optional: `docs/03-product/scoring/summary.md` (all scores), `docs/00-challenge/challenge-brief.md`.

## Rules

- Allocate **exactly 100 points** across F-IDs, **max 25 per F-ID**. Features now merge ideas from all
  roles, so you may vote for any of them.
- Vote for what wins **Espoo's** judging: impact & relevance for real events (45%), innovation & UX in
  a three-minute demo (35%), responsible & feasible execution (20%). Tech-challenge fit is a tie-breaker,
  not the goal.
- Be concrete and brief: ≤ 700 words in total. Write in English. Do not modify other files; no git.

## Output

Write `docs/02-ideation/round-3-votes/<PREFIX>-vote.md` with exactly this structure
(`scripts/aggregate_scores.py` parses the "Points allocation" table):

```markdown
# Round 3 vote — <PREFIX> (<role title>)

## Points allocation
| F-ID | Points | Why (≤ 20 words) |
|---|---|---|
| F06 | 20 | ... |
(only rows with points > 0; total exactly 100; max 25 per row)

## MVP cut (what we build by Sunday 10:00)
- **Build for real** (max 6 F-IDs, in build order): ...
- **Clickable mock or slide only:** ...
- **Not now:** ...

## Tech-challenge fit
One line each for Nemotron 3.5 Super VL, Modal and Gemma: which F-ID it powers and the visible demo
moment, or "does not fit".

## Three ideas for the Espoo mentors at 09:00
Three F-IDs to put to the mentors as "which would you pilot first, and why?" — one line each on what we
want to learn.

## Biggest risk and mitigation
≤ 80 words.
```

When done, reply with your top 3 F-IDs by points and your "build for real" list.
