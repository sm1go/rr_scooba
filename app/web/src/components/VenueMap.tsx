import { Link } from 'react-router-dom'
import { useI18n } from '../i18n/i18n'

type Booth = {
  id: string; name: string; booth: string | null
  logo_color?: string | null; field?: string | null
}
export type RouteStop = {
  employer_id: string; starts_at: string
}

const ROWS = ['A', 'B', 'C', 'D']
const W = 760
const H = 470
const ROW_Y = [100, 180, 260, 340]
const BOX_W = 140
const BOX_H = 56
const COL_X = [60, 215, 370, 525]

function initials(name: string) {
  const skip = new Set(['oy', 'ab', 'ky', 'oyj', 'tmi'])
  const words = name.split(/\s+/).filter(
    (w) => !skip.has(w.replace(/[.,]/g, '').toLowerCase()))
  return words.slice(0, 2).map((w) => w[0]).join('').toUpperCase() || '·'
}

/** §9.6 venue schematic: entrance at the bottom, info & advisor desk,
 * stage and workshop on the side, booth rows A–D. Booked booths are
 * numbered in time order and joined by a dashed route. */
export default function VenueMap({ booths, route, highlight }: {
  booths: Booth[]
  route?: RouteStop[]
  highlight?: string
}) {
  const { t } = useI18n()
  const byBooth = new Map(booths.filter((b) => b.booth)
    .map((b) => [b.booth as string, b]))
  const stopOf = new Map(route?.map((r, i) => [r.employer_id, i + 1]) ?? [])
  const stops = (route ?? [])
    .map((r) => {
      const b = booths.find((x) => x.id === r.employer_id)
      return b?.booth ? { ...r, booth: b.booth, b } : null
    })
    .filter((x): x is RouteStop & { booth: string; b: Booth } => !!x)

  const center = (booth: string) => {
    const row = ROWS.indexOf(booth[0])
    const col = Number(booth.slice(1)) - 1
    return row < 0 || col < 0 ? null
      : { x: COL_X[col] + BOX_W / 2, y: ROW_Y[row] + BOX_H / 2 }
  }
  const routePts = stops.map((s) => center(s.booth)).filter(
    (p): p is { x: number; y: number } => !!p)

  return (
    <figure className="venue-map m-0">
      <svg viewBox={`0 0 ${W} ${H}`} role="img" className="w-full"
           aria-label={t('map.title')} style={{ height: 'auto' }}>
        <rect x={8} y={8} width={W - 16} height={H - 16}
              fill="var(--color-surface, #fff)"
              stroke="var(--color-border, #999)" rx={10} />
        {/* stage: wide band across the top of the hall */}
        <rect x={60} y={20} width={605} height={52} rx={8}
              fill="none" stroke="var(--color-border, #999)"
              strokeDasharray="4 3" />
        <text x={362} y={52} textAnchor="middle" fontSize={14}
              fill="currentColor">{t('map.stage')}</text>
        {/* workshop room: side box outside the booth grid */}
        <rect x={675} y={ROW_Y[3]} width={70} height={BOX_H} rx={8}
              fill="none" stroke="var(--color-border, #999)"
              strokeDasharray="4 3" />
        <text x={710} y={ROW_Y[3] + BOX_H / 2 + 5} textAnchor="middle"
              fontSize={11} fill="currentColor">{t('map.workshop')}</text>
        {ROWS.map((row, ri) => (
          <g key={row}>
            <text x={30} y={ROW_Y[ri] + BOX_H / 2 + 5} fontSize={15}
                  fontWeight={600} fill="currentColor">{row}</text>
            {COL_X.map((x, ci) => {
              const code = `${row}${ci + 1}`
              const b = byBooth.get(code)
              const n = b ? stopOf.get(b.id) : undefined
              if (!b) {
                return (
                  <rect key={code} x={x} y={ROW_Y[ri]}
                        width={BOX_W} height={BOX_H} rx={8}
                        fill="none"
                        stroke="var(--color-border, #999)"
                        strokeOpacity={0.4} strokeDasharray="4 3" />
                )
              }
              return (
                <g key={code}>
                  <rect x={x} y={ROW_Y[ri]} width={BOX_W} height={BOX_H}
                        rx={8}
                        fill={b.logo_color || '#5a6472'}
                        stroke={n ? 'var(--color-yes, #1a7f37)'
                                 : highlight === code
                                   ? 'var(--color-brand, #005ea8)'
                                   : 'var(--color-border, #999)'}
                        strokeWidth={n || highlight === code ? 4 : 1} />
                  <text x={x + BOX_W / 2} y={ROW_Y[ri] + 24}
                        textAnchor="middle" fontSize={13}
                        fontWeight={600} fill="#fff">
                    {initials(b.name)}
                  </text>
                  <text x={x + BOX_W / 2} y={ROW_Y[ri] + 42}
                        textAnchor="middle" fontSize={12} fill="#fff">
                    {code}
                  </text>
                  {n && (
                    <g>
                      <circle cx={x + BOX_W - 8} cy={ROW_Y[ri] + 8}
                              r={11} fill="var(--color-yes, #1a7f37)" />
                      <text x={x + BOX_W - 8} y={ROW_Y[ri] + 12}
                            textAnchor="middle" fontSize={12}
                            fontWeight={700} fill="#fff">{n}</text>
                    </g>
                  )}
                </g>
              )
            })}
          </g>
        ))}
        {routePts.length > 1 && (
          <polyline
            points={routePts.map((p) => `${p.x},${p.y}`).join(' ')}
            fill="none" stroke="var(--color-yes, #1a7f37)"
            strokeWidth={2.5} strokeDasharray="7 5" />
        )}
        {/* entrance + info desk along the bottom */}
        <rect x={60} y={H - 66} width={180} height={26} rx={8}
              fill="none" stroke="var(--color-border, #999)" />
        <text x={150} y={H - 49} textAnchor="middle" fontSize={12}
              fill="currentColor">{t('map.infodesk')}</text>
        <rect x={W / 2 - 60} y={H - 64} width={120} height={22} rx={4}
              fill="var(--color-brand, #005ea8)" />
        <text x={W / 2} y={H - 49} textAnchor="middle" fontSize={12}
              fill="#fff">{t('map.entrance')}</text>
      </svg>
      {stops.length > 0 && (
        <figcaption>
          <p className="m-0 mt-2 font-medium">{t('map.route')}</p>
          <ol className="m-0 ps-5">
            {stops.map((s, i) => (
              <li key={s.employer_id}>
                {t('map.stop', {
                  n: i + 1, t: s.starts_at.slice(11, 16),
                  b: s.booth, name: s.b.name })}
              </li>
            ))}
          </ol>
        </figcaption>
      )}
      {/* text alternative for screen readers */}
      <ul className="sr-only">
        {booths.map((b) => (
          <li key={b.id}>
            <Link to={`/companies/${b.id}`}>
              {b.name}{b.booth ? ` ${t('ev.booth')} ${b.booth}` : ''}
            </Link>
          </li>
        ))}
      </ul>
    </figure>
  )
}
