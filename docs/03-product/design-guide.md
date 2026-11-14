# Design guide — Finnish public-service style

Goal: calm, plain, trustworthy — like a good Finnish public service (Suomi.fi, HSL, Espoo.fi), not a startup dashboard.

- **Simplicity first:** one main action per screen, big clear buttons, max ~3 choices visible at once. A first-time user finishes a step without help.
- **Plain language:** short sentences, verbs on buttons ("Send Spark", "Accept"), no jargon, no AI hype words. Every AI output labelled "Suggested — you decide".
- **Palette:** white `#FFFFFF` and snow `#F5F7FA` surfaces; ink `#1B1F24` text; Nordic blue `#0050B5` primary (hover `#003E8C`); lake `#E8F0FB` tint; birch `#E6E1D6` neutral; moss `#2F7D4F` success; lingonberry `#B3261E` warning/error. No gradients, no dark glassmorphism, no emojis.
- **Type:** Inter (fallback system sans), 16 px base, 1.5 line height, headings semibold not black; generous whitespace (8-px grid, 24–32 px between sections).
- **Shapes:** 8 px radius, 1 px `#D9DEE5` borders, almost no shadows. Simple line icons (lucide).
- **Accessibility (WCAG 2.2 AA):** contrast ≥ 4.5:1, visible focus ring, full keyboard use, tap/click instead of drag, text alternative for every voice step, `lang` attributes, labels on all inputs.
- **Privacy visible:** pool numbers always as bands; a small "Why am I seeing this?" link next to AI suggestions; names appear only after accept, shown with a quiet "Revealed after mutual yes" note.
- **Layout:** top bar with "TalentMatch Signal · City of Espoo (demo)" and a role switcher (Company · Talent · Organiser); content width ≤ 960 px; mobile-first for the talent side.
