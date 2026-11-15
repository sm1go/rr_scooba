---
name: pitch-deck
description: Build or update the Espoo Work Map pitch deck (HTML -> 16:9 PDF) from real app screens captured by playing the demo story
argument-hint: "[what to change, e.g. 'refresh screenshots' or 'add a slide about the online event']"
allowed-tools:
  - read
  - grep
  - glob
triggers:
  - user
  - model
---

# Espoo Work Map pitch deck

The deck lives in `docs/04-pitch/`:

| File | What |
|---|---|
| `presentation.html` | Source. 1920x1080 slides, app fonts and colours, keyboard navigation |
| `presentation.pdf` | **The deliverable.** One page per slide |
| `assets/*.png` | Real app screens used by the slides; `assets/fonts/` holds the app fonts |

Tools in this skill (`.devin/skills/pitch-deck/scripts/`):

| Script | What |
|---|---|
| `shoot.py <plan.json> <out_dir>` | Plays a story through the running app (demo reset, demo clock, API calls as demo users) and captures screens |
| `story.json` | The deck's story: Sanna (employer) → Aino (jobseeker) → match → event day → answer → Leena (organiser) → online event |
| `assets.py <shots_dir>` | Copies captures into `docs/04-pitch/assets/` under the names the HTML uses and crops wide cards |
| `preview.py <pdf> <out_dir>` | Renders the PDF into contact sheets (4 slides each) for visual QA |

PDF export: `bash scripts/export-pdfs.sh` (headless Chrome; set `CHROME=` if it isn't at the default Windows path).

## What the user asked for

$ARGUMENTS

If nothing specific was asked, refresh the screenshots, re-export the PDF and run QA.

## Workflow

1. **Tools** (once per machine; keep them out of the repo):
   ```bash
   python -m pip install --target "$TEMP/pitch-tools" playwright pymupdf pillow
   export PYTHONPATH="$TEMP/pitch-tools"
   ```
   Playwright uses the installed Google Chrome (`channel="chrome"`), so no browser download is needed.

2. **App running.** Check `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5173` and `http://127.0.0.1:8000/api/health`. If they aren't running, start them as in `README.md` ("Run the demo locally") in background shells. Always use `127.0.0.1`: `localhost` hits a different server on this machine.

3. **Tell the user before capturing.** `story.json` starts and ends with `POST /api/demo/reset` and moves the demo clock, so it rebuilds the local demo DB. The data is synthetic, but any manual demo state they had is lost. Then run:
   ```bash
   python .devin/skills/pitch-deck/scripts/shoot.py .devin/skills/pitch-deck/scripts/story.json "$TEMP/pitch-shots"
   ```
   Fix every `MISSING part` or `API FAILED` line. Usually UI text changed, so update the `text` in `story.json` (the English strings are in `app/web/src/i18n/en.ts`).

4. **Look at every capture** with the read tool before using it. Check for empty forms, overlapping bottom nav, odd seed data (e.g. a role description that doesn't match the company), and cards cut off at the edge.

5. **Assets:** `python .devin/skills/pitch-deck/scripts/assets.py "$TEMP/pitch-shots"`. New screens: add a step in `story.json`, a name in `NAMES` in `assets.py`, and an `<img>` in the HTML.

6. **Edit `presentation.html`** following the design rules below. Reuse the existing classes: `.s` slide, `.ink`/`.green` backgrounds, `.steps` journey pills, `.shot` screenshot, `.phone` phone frame, `.points`, `.tile`, `.three`, `.chips`, `.loop`.

7. **Export and QA:**
   ```bash
   bash scripts/export-pdfs.sh
   python .devin/skills/pitch-deck/scripts/preview.py docs/04-pitch/presentation.pdf "$TEMP/pitch-preview"
   ```
   Read **every** sheet. The page count must equal the slide count. No text clipped or overflowing, no half-empty slides, screenshot text readable. If a screenshot is tiny because of white space, crop it (`CROP` in `assets.py`). Repeat until clean.

8. **Commit** the HTML, PDF and assets (`docs: ...`, Conventional Commits) and push to `origin/main` (see `AGENTS.md`).

## Design rules (learned the hard way: text-only card decks were rejected)

- **Show the product.** Every story slide carries a real screen from the app. Never mock UI in HTML.
- **One story, real names.** Follow Sanna, Aino and Leena through the five steps (need card → register → choose → event day → answer). Keep the step pills on top of story slides.
- **One idea per slide.** A big serif headline that states the point (a sentence, not a label), at most 3 short points, and the screenshot. Body text at least 26px on the 1920 canvas.
- **Look like the app.** Hedvig Letters Serif for headlines, Geist for text, canvas `#faf9f7`, brand green `#0f7a58`, ink `#171717`. Use ink and green slides only for rhythm (challenge, bet, responsible, ask).
- **Honest numbers only.** Every figure must be traceable to `docs/01-research/` or to the code (e.g. count tests and languages in the repo). Don't invent ages, percentages or outcomes. Unverified figures go to the user as a caveat in your final message.
- **Speak to the judging criteria** (`docs/00-challenge/challenge-brief.md`): impact 45%, innovation and UX 35%, responsible and feasible 20%.
- English on slides (international jury). Talk to the owner in Polish.

## Final message to the user

Link the PDF, list what changed, and say plainly that the demo DB was reset and which numbers you couldn't verify.
