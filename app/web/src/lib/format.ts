import type { Job, Shift } from '../types'
import type { Key } from '../i18n/en'
import { DAYS, PARTS } from '../types'

type T = (k: Key) => string

export function payLine(j: Job, t: T): string {
  if (j.pay_amount == null) return j.pay_note || t('common.toagreed')
  const unit = j.pay_unit === 'month' ? t('common.permonth') : t('common.perhour')
  return `€${j.pay_amount.toFixed(2)} ${unit}${j.pay_note ? ` · ${j.pay_note}` : ''}`
}

export function hoursLine(j: Job, t: T): string {
  if (j.hours_min == null && j.hours_max == null) return ''
  if (j.hours_min === j.hours_max) return `${j.hours_max} ${t('common.hweek')}`
  return `${j.hours_min ?? '–'}–${j.hours_max ?? '–'} ${t('common.hweek')}`
}

export function shiftsLine(j: Job, t: T): string {
  if (!j.shifts.length) return j.schedule_flexible ? t('common.flexible') : ''
  const byDay = new Map<string, Shift[]>()
  for (const s of j.shifts) {
    byDay.set(s.day, [...(byDay.get(s.day) ?? []), s])
  }
  const parts = [...byDay.entries()]
    .sort(([a], [b]) => DAYS.indexOf(a as (typeof DAYS)[number])
                        - DAYS.indexOf(b as (typeof DAYS)[number]))
    .map(([day, ss]) => {
      const times = ss.map((s) => `${s.start.slice(0, 5)}–${s.end.slice(0, 5)}`).join(', ')
      return `${t(`day.${day}` as Key)} ${times}`
    })
  return parts.join(' · ')
}

export function jobLine(j: Job, t: T): string {
  const bits = [payLine(j, t), hoursLine(j, t), shiftsLine(j, t)].filter(Boolean)
  return bits.join(' · ')
}

/** "Confirmed today" / "Confirmed yesterday" / "Confirmed 4 days ago" /
    "Not confirmed recently" is handled by the caller via job.stale. */
export function daysAgoText(days: number | null, t: T): string {
  if (days == null) return ''
  if (days === 0) return t('jobs.confirmedtoday')
  if (days === 1) return t('jobs.confirmedyesterday')
  return `${t('jobs.confirmed')} ${days} ${t('common.daysago')}`
}

/** Turn stored slot ids (['mon-evening','sat-morning',...]) into human text:
    "Mon evening; Sat all day; Sun all day". Never shows raw ids. */
export function slotsText(slots: string[], t: T): string {
  const byDay = new Map<string, string[]>()
  for (const s of slots) {
    const [day, part] = s.split('-')
    if (!day || !part) continue
    byDay.set(day, [...(byDay.get(day) ?? []), part])
  }
  const out = [...byDay.entries()]
    .sort(([a], [b]) => DAYS.indexOf(a as (typeof DAYS)[number])
                        - DAYS.indexOf(b as (typeof DAYS)[number]))
    .map(([day, parts]) => {
      const name = t(`day.${day}` as Key)
      return parts.length === PARTS.length
        ? `${name} ${t('common.allday')}`
        : `${name} ${parts
          .sort((a, b) => PARTS.indexOf(a as (typeof PARTS)[number])
                          - PARTS.indexOf(b as (typeof PARTS)[number]))
          .map((p) => t(`part.${p}` as Key)).join(', ')}`
    })
  return out.join('; ')
}

/** "13 Nov 2026" (locale-aware). */
export function fmtDate(iso: string | null | undefined, lang: 'en' | 'fi' = 'en'): string {
  if (!iso) return ''
  const d = new Date(iso.length === 10 ? `${iso}T00:00:00` : iso)
  if (Number.isNaN(d.getTime())) return iso
  return d.toLocaleDateString(lang === 'fi' ? 'fi-FI' : 'en-GB',
    { day: 'numeric', month: 'short', year: 'numeric' })
}

export function districtName(id: string, districts: { id: string; name: string }[]): string {
  return districts.find((d) => d.id === id)?.name ?? id
}

export function fieldName(id: string, t: T): string {
  const key = `field.${id}` as Key
  return t(key)
}
