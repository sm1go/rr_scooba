import { useMemo } from 'react'
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
  const bounds = useMemo(() => {
    const pts = jobs
      .filter((j) => j.lat != null && j.lon != null)
      .map((j) => [j.lat!, j.lon!] as [number, number])
    return pts.length ? L.latLngBounds(pts) : null
  }, [jobs])
  if (bounds) map.fitBounds(bounds.pad(0.15))
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

  return (
    <MapContainer center={[60.205, 24.755]} zoom={12}
                  style={{ height, width: '100%' }} scrollWheelZoom>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <FitBounds jobs={markers} />
      {markers.map((j) => (
        <Marker key={j.id} position={[j.lat!, j.lon!]}
                icon={markerIcon(j.id === selectedId)}
                title={j.title}
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
