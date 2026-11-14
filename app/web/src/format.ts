const fmt = new Intl.DateTimeFormat('en-GB', {
  timeZone: 'Europe/Helsinki',
  weekday: 'short',
  day: 'numeric',
  month: 'short',
  hour: '2-digit',
  minute: '2-digit',
})

/** Human date in Europe/Helsinki; falls back to the raw string. */
export function when(iso: string) {
  const d = new Date(iso)
  return Number.isNaN(d.getTime()) ? iso : fmt.format(d)
}

const LANG_NAMES: Record<string, string> = { ar: 'Arabic', en: 'English', fi: 'Finnish', sv: 'Swedish', uk: 'Ukrainian', ru: 'Russian', so: 'Somali', et: 'Estonian' }

/** "ar" -> "Arabic"; full names pass through. */
export const langName = (code: string) => LANG_NAMES[code.toLowerCase()] ?? code
