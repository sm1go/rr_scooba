# Round 2 brief — cross-review (all roles)

You are one of six role agents in a virtual startup team working on the City of Espoo challenge
"Rethinking Recruitment" at **Junction 2026** (Hype Areena, Espoo, 13–15 Nov 2026). Round 1
(independent ideation) is finished: **58 raw feature ideas** from six roles. Your job now is to review
the other five roles' ideas critically and honestly, through your own role's lens.

**Time context:** final submission is Sunday 15 Nov 10:00. The prototype will be built by a very small
team with AI coding agents in roughly 20 working hours, then pitched. Feasibility of a convincing demo
matters for J3, but judge J1 and J2 on the idea's merit for Espoo's real events.

## Read first (in this order)

1. `docs/00-challenge/challenge-brief.md` — stable IDs S1–S3, P1–P10, C1–C6, J1–J3.
2. `docs/02-ideation/README.md` — the scoring rubric (integers 1–5).
3. `docs/02-ideation/round-1-digest.md` — one-line view of all 58 ideas plus each role's top 3 and hero concept.
4. Every file in `docs/02-ideation/round-1-proposals/` **except your own** — read the full feature
   descriptions before scoring.

Optional: `docs/01-research/*.md`. Use web research only to verify a specific red flag (max 3 searches).

## Rules

- Score **every** feature of the other five roles. Do not score your own role's features.
- Integers 1–5 for J1, J2 and J3, per the rubric. **Use the full range**: expect few 5s and few 1s.
  A review where everything is a 4 carries no information.
- Judge the idea, not the prose. Do not reward length or buzzwords.
- Comments ≤ 25 words and specific, e.g. "duplicates UX-05 but lacks essay-free pairing".
- Hard constraints: a feature that relies on automated decisions or profiling about individuals without
  human involvement, on real personal data, or on detecting "AI-written" text as a gate gets **J3 ≤ 2**
  and a red flag (C1–C6).
- Your top 10 must **not** include your own role's features.
- Write in English, max ~3,000 words. Do not modify any other file.

## Output

Write `docs/02-ideation/round-2-reviews/<PREFIX>-review.md` with exactly this structure
(`scripts/aggregate_scores.py` parses sections 3 and 4):

```markdown
# Round 2 review — <PREFIX> (<role title>)

## 1. Overall read
≤ 200 words: what the strongest ideas have in common, what is over-engineered, what the jury will love.

## 2. Duplicate clusters
Groups of raw IDs (across all six roles, including yours) that are essentially the same idea:
- **<proposed merged name>**: STR-04, UX-05, TECH-08 — what the merged version should keep from each.

## 3. Scores
| ID | J1 | J2 | J3 | Comment |
|---|---|---|---|---|
| PM-01 | 4 | 3 | 5 | ... |
(one row per feature of the other five roles: ID in the first column, then three integers)

## 4. My top 10
1. UX-05 — why (≤ 25 words)
...
10. ...

## 5. Red flags
- ID — the risk (legal, ethical, bias, feasibility, adoption) and its mitigation, or "drop".

## 6. Recommended winning concept
Name; the 4–7 raw IDs it combines (any roles, including yours); a 120–200-word demo story;
what to cut explicitly; the single biggest risk.

## 7. Gaps
Up to 5 important things nobody proposed (or everyone underweighted).
```

When done, reply with five lines: your top 3 IDs and the name of your recommended concept.
