import { useEffect, useMemo, useRef, type RefObject } from 'react'
import { MapContainer, Marker, Popup, TileLayer, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { Link } from 'react-router-dom'
import type { Job } from '../types'
import { useI18n } from '../i18n/i18n'
import { jobLine } from '../lib/format'

function markerIcon(selected: boolean) {
  return L.divIcon({
    className: '',
    html: `<div class="job-marker${selected ? ' selected' : ''}" aria-hidden="true"></div>`,
    iconSize: [34, 34],
    iconAnchor: [17, 34],
  })
}

function FitBounds({ jobs }: { jobs: Job[] }) {
  const map = useMap()
  const key = jobs.map((j) => j.id).join(',')
  const bounds = useMemo(() => {
    const pts = jobs
      .filter((j) => j.lat != null && j.lon != null)
      .map((j) => [j.lat!, j.lon!] as [number, number])
    return pts.length ? L.latLngBounds(pts) : null
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key])
  // fit only when the set of jobs changes, not on every render
  useEffect(() => {
    if (bounds) map.fitBounds(bounds.pad(0.15))
  }, [map, bounds])
  return null
}

/** "Show on the map": zoom to the chosen job and open its popup. */
function FocusSelected({ job, markers }: {
  job: Job | undefined
  markers: RefObject<Record<string, L.Marker>>
}) {
  const map = useMap()
  useEffect(() => {
    if (!job || job.lat == null || job.lon == null) return
    // the map may have just been unhidden (phone list/map switch)
    map.invalidateSize()
    map.setView([job.lat, job.lon], Math.max(map.getZoom(), 15), { animate: true })
    const m = markers.current?.[job.id]
    const id = window.setTimeout(() => m?.openPopup(), 300)
    return () => window.clearTimeout(id)
  }, [map, job, markers])
  return null
}

/** One keyboard-focusable marker per on-site/hybrid job (custom divIcon —
    the default Leaflet marker images break under Vite). The list below is
    the full equivalent for keyboard users. */
export default function JobMap({
  jobs, selectedId, onSelect, height = 420,
}: {
  jobs: Job[]
  selectedId?: string | null
  onSelect?: (id: string) => void
  height?: number
}) {
  const { t } = useI18n()
  const markers = jobs.filter(
    (j) => j.lat != null && j.lon != null && j.work_mode !== 'remote')
  const refs = useRef<Record<string, L.Marker>>({})

  return (
    <MapContainer center={[60.205, 24.755]} zoom={12}
                  style={{ height, width: '100%' }} scrollWheelZoom>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <FitBounds jobs={markers} />
      <FocusSelected job={markers.find((j) => j.id === selectedId)} markers={refs} />
      {markers.map((j) => (
        <Marker key={j.id} position={[j.lat!, j.lon!]}
                icon={markerIcon(j.id === selectedId)}
                title={j.title}
                ref={(m) => { if (m) refs.current[j.id] = m; else delete refs.current[j.id] }}
                eventHandlers={{ click: () => onSelect?.(j.id) }}>
          <Popup>
            <div style={{ minWidth: 180 }}>
              <strong>{j.title}</strong>
              <div>{j.employer?.name}</div>
              <div>{jobLine(j, t)}</div>
              <Link to={`/jobs/${j.id}`}>{t('jobs.opendetails')}</Link>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  )
}
