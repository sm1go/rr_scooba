/** Lazy commute loader + plain-words formatting (spec §5).

    Rows ask for a commute when they scroll into view; at most 4 routing
    requests run at once and results are kept in memory per job+district.
    Nothing here depends on being signed in. */

import { api } from './api'
import type { Commute } from '../types'
import type { Key } from '../i18n/en'

type T = (k: Key, vars?: Record<string, string | number>) => string

const MAX_RUNNING = 4
const cache = new Map<string, Commute | null>()
const pending = new Map<string, Promise<Commute | null>>()
const queue: (() => Promise<void>)[] = []
let running = 0

function pump() {
  while (running < MAX_RUNNING && queue.length) {
    const job = queue.shift()!
    running++
    job().finally(() => { running--; pump() })
  }
}

/** Fetch (or recall) the commute for job+district. Never rejects. */
export function getCommute(jobId: string, district: string)
    : Promise<Commute | null> {
  const key = `${jobId}|${district}`
  if (cache.has(key)) return Promise.resolve(cache.get(key)!)
  let p = pending.get(key)
  if (!p) {
    p = new Promise<Commute | null>((resolve) => {
      queue.push(async () => {
        try {
          const c = await api<Commute>(
            `/api/commute?job_id=${jobId}&district=${district}`)
          cache.set(key, c)
          resolve(c)
        } catch {
          cache.set(key, null)
          resolve(null)
        }
      })
    })
    pending.set(key, p)
    pump()
  }
  return p
}

export function commuteCached(jobId: string, district: string) {
  return cache.get(`${jobId}|${district}`)
}

// ---- plain-words rendering ------------------------------------------------

const MODE_KEY: Record<string, string> = {
  BUS: 'bus', SUBWAY: 'metro', RAIL: 'train', TRAM: 'tram', FERRY: 'ferry',
}

function modeWord(mode: string, t: T): string {
  return t(`commute.mode.${MODE_KEY[mode] ?? 'bus'}` as Key)
}

function modeWordCap(mode: string, t: T): string {
  return t(`commute.M.${MODE_KEY[mode] ?? 'bus'}` as Key)
}

/** 'About 37 min by bus from Leppävaara' / 'A few minutes on foot from…'. */
export function commuteLine(c: Commute, districtName: string, t: T): string {
  const transit = [...new Set(
    c.legs.filter((l) => l.mode !== 'WALK').map((l) => modeWord(l.mode, t)))]
  if (!transit.length) {
    return c.minutes <= 3
      ? t('commute.walkfew', { district: districtName })
      : t('commute.walkmin', { m: c.minutes, district: districtName })
  }
  return t('commute.line', {
    m: c.minutes,
    modes: transit.join(` ${t('commute.and')} `),
    district: districtName,
  })
}

/** One leg in plain words: 'Walk 9 min to Leppävaaran asema',
    'Bus 520, 25 min to Matinkylä (M)'. Origin -> district name,
    Destination -> 'the workplace' (dropped for a bare final walk). */
export function legText(l: Commute['legs'][number], districtName: string,
                       t: T): string {
  const place = (s: string) =>
    s === 'Origin' ? districtName
      : s === 'Destination' ? t('commute.workplace') : s
  const to = place(l.to)
  if (l.mode === 'WALK') {
    return l.to === 'Destination'
      ? t('commute.leg.walkend', { m: l.minutes })
      : t('commute.leg.walk', { m: l.minutes, to })
  }
  return l.route
    ? t('commute.leg.ride', {
      mode: modeWordCap(l.mode, t), route: l.route, m: l.minutes, to })
    : t('commute.leg.plain', {
      mode: modeWordCap(l.mode, t), m: l.minutes, to })
}
