import { useSyncExternalStore } from 'react'
import { NavLink, Link, Outlet, useLocation } from 'react-router-dom'
import { WifiOff } from 'lucide-react'
import { offlineStore } from '../api'

const roles = [
  { to: '/company', label: 'Company' },
  { to: '/talent', label: 'Talent' },
  { to: '/organiser', label: 'Organiser' },
]

function OfflineBadge() {
  const offline = useSyncExternalStore(offlineStore.subscribe, offlineStore.get)
  if (!offline) return null
  return (
    <span className="inline-flex items-center gap-1 rounded border border-line bg-snow px-2 py-0.5 text-xs text-muted" role="status">
      <WifiOff aria-hidden className="h-3.5 w-3.5" /> Demo data (offline)
    </span>
  )
}

export function SubNav({ items }: { items: { to: string; label: string }[] }) {
  return (
    <nav aria-label="Steps" className="mb-6 flex flex-wrap gap-1 border-b border-line">
      {items.map((i) => (
        <NavLink
          key={i.to}
          to={i.to}
          end
          className={({ isActive }) =>
            `-mb-px border-b-2 px-3 py-2 text-sm font-medium ${isActive ? 'border-nordic text-nordic' : 'border-transparent text-muted hover:text-ink'}`
          }
        >
          {i.label}
        </NavLink>
      ))}
    </nav>
  )
}

export default function Layout() {
  const { pathname } = useLocation()
  return (
    <div className="flex min-h-screen flex-col">
      <a href="#main" className="skip-link">
        Skip to content
      </a>
      <header className="border-b border-line bg-white">
        <div className="mx-auto flex max-w-[960px] flex-wrap items-center justify-between gap-3 px-4 py-3">
          <div className="flex flex-wrap items-center gap-3">
            <Link to="/" className="font-semibold text-ink no-underline">
              TalentMatch Signal <span className="font-normal text-muted">· City of Espoo (demo)</span>
            </Link>
            <OfflineBadge />
          </div>
          <nav aria-label="Choose your role">
            <ul className="flex rounded-lg border border-line p-0.5">
              {roles.map((r) => {
                const active = pathname.startsWith(r.to)
                return (
                  <li key={r.to}>
                    <NavLink
                      to={r.to}
                      aria-current={active ? 'page' : undefined}
                      className={`block rounded-md px-3 py-1.5 text-sm font-medium ${active ? 'bg-nordic text-white' : 'text-ink hover:bg-lake'}`}
                    >
                      {r.label}
                    </NavLink>
                  </li>
                )
              })}
            </ul>
          </nav>
        </div>
      </header>
      <main id="main" className="mx-auto w-full max-w-[960px] flex-1 px-4 py-8">
        <Outlet />
      </main>
      <footer className="border-t border-line bg-white">
        <p className="mx-auto max-w-[960px] px-4 py-4 text-sm text-muted">
          Synthetic data only · No scores or rankings of people · Humans decide
        </p>
      </footer>
    </div>
  )
}
