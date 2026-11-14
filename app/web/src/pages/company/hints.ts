// Where a lint hint belongs on the card, and what "Use suggestion" changes.
import { CEFR_LEVELS } from '../../types'
import type { Cefr, ChallengeCard, LanguageNeed, LintHint } from '../../types'

export type HintPlace = { kind: 'req'; id: string } | { kind: 'nice'; index: number } | { kind: 'lang' } | { kind: 'card' }

const LANG_NAMES = ['finnish', 'swedish', 'english']
const has = (text: string, trigger: string) => text.toLowerCase().includes(trigger.toLowerCase())

export function locateHint(card: ChallengeCard, h: LintHint): HintPlace {
  if (h.requirement_id && card.must_haves.some((r) => r.id === h.requirement_id)) return { kind: 'req', id: h.requirement_id }
  const t = h.trigger.toLowerCase()
  if (h.rule.includes('language') || LANG_NAMES.some((l) => t.startsWith(l))) return { kind: 'lang' }
  const req = card.must_haves.find((r) => has(r.text, h.trigger) || has(r.how_we_check, h.trigger))
  if (req) return { kind: 'req', id: req.id }
  const index = card.nice_to_haves.findIndex((n) => has(n, h.trigger))
  if (index >= 0) return { kind: 'nice', index }
  return { kind: 'card' }
}

/** "…set Finnish at B1 for customer calls by month 6 (course paid)." -> a language row. */
function parseLanguage(s: string): LanguageNeed | null {
  const m = s.match(/\b([A-Z][a-z]+)\s+(?:at\s+)?(A1|A2|B1|B2|C1|C2)\s+for\s+(.+?)\s+((?:by|from)\s+[^.;(]+?)\s*(?:[.;(]|$)/)
  if (!m || !CEFR_LEVELS.includes(m[2] as Cefr)) return null
  return { language: m[1], level: m[2] as Cefr, task: m[3], from_when: m[4] }
}

/** The concrete example inside a suggestion, e.g. "… e.g. 'a small team that ships weekly'." */
function example(s: string): string | null {
  const m = s.match(/['‘“"]([^'’”"]{3,})['’”"]/)
  return m ? m[1] : null
}

function applyLanguage(card: ChallengeCard, h: LintHint): ChallengeCard {
  const lang = parseLanguage(h.suggestion)
  if (!lang) return card
  const same = (l: LanguageNeed) => l.language.toLowerCase() === lang.language.toLowerCase()
  let languages = card.languages.some(same) ? card.languages.map((l) => (same(l) ? lang : l)) : [...card.languages, lang]
  if (/english[- ]speaking|english team/i.test(h.suggestion) && !languages.some((l) => l.language.toLowerCase() === 'english'))
    languages = [...languages, { language: 'English', level: 'B2', task: 'daily team work', from_when: 'from day one' }]
  return { ...card, languages }
}

export function applyHint(card: ChallengeCard, h: LintHint): ChallengeCard {
  const place = locateHint(card, h)
  const ex = example(h.suggestion)
  switch (place.kind) {
    case 'lang':
      return applyLanguage(card, h)
    case 'req':
      return {
        ...applyLanguage(card, h),
        must_haves: card.must_haves.map((r) => (r.id === place.id && has(r.text, h.trigger) ? { ...r, text: ex ?? h.suggestion } : r)),
      }
    case 'nice': {
      const nice = [...card.nice_to_haves]
      if (ex) nice[place.index] = ex
      else nice.splice(place.index, 1)
      return { ...card, nice_to_haves: nice }
    }
    default:
      return card
  }
}

export const hintKey = (h: LintHint) => `${h.rule}|${h.trigger}`
