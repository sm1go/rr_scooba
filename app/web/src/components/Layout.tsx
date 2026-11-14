import { useEffect, useState, type ReactNode } from 'react'
import {
  Link, NavLink, Outlet, useLocation, useNavigate,
} from 'react-router-dom'
import {
  Bookmark, FileText, Home, Menu as MenuIcon, User as UserIcon,
  Briefcase, Inbox, ClipboardList, Building2, ListChecks, CalendarDays, X,
} from 'lucide-react'
import { useAuth } from '../lib/auth'
import { useA11y } from '../lib/a11y'
import { useDialog } from '../lib/useDialog'
import { useI18n, LANGS, type Lang } from '../i18n/i18n'
import type { Key } from '../i18n/en'

const NAV: Record<string, { to: string; key: Key; short: Key; icon: typeof Home; wideOnly?: boolean }[]> = {
  resident: [
    { to: '/', key: 'nav.jobs', short: 'nav.jobs', icon: Home },
    { to: '/saved', key: 'nav.saved', short: 'nav.saved', icon: Bookmark },
    { to: '/applications', key: 'nav.applications', short: 'nav.applied', icon: FileText },
    { to: '/profile', key: 'nav.profile', short: 'nav.profile', icon: UserIcon },
    { to: '/event', key: 'nav.event', short: 'nav.event', icon: CalendarDays, wideOnly: true },
  ],
  employer: [
    { to: '/employer', key: 'nav.myjobs', short: 'nav.jobs', icon: Briefcase },
    { to: '/employer/applications', key: 'emp.applications', short: 'nav.applied', icon: Inbox },
    { to: '/employer/company', key: 'nav.company', short: 'nav.company', icon: Building2 },
    { to: '/employer/event', key: 'nav.event', short: 'nav.event', icon: CalendarDays, wideOnly: true },
  ],
  advisor: [
    { to: '/advisor', key: 'nav.requests', short: 'nav.requests', icon: Inbox },
    { to: '/advisor/jobs', key: 'nav.advisorjobs', short: 'nav.jobs', icon: ClipboardList },
    { to: '/advisor/follow-up', key: 'nav.followup', short: 'nav.followup', icon: ListChecks },
    { to: '/advisor/support', key: 'advisor.support', short: 'nav.support', icon: Building2, wideOnly: true },
  ],
  anon: [
    { to: '/', key: 'nav.jobs', short: 'nav.jobs', icon: Home },
    { to: '/saved', key: 'nav.saved', short: 'nav.saved', icon: Bookmark },
    { to: '/applications', key: 'nav.applications', short: 'nav.applied', icon: FileText },
    { to: '/profile', key: 'nav.profile', short: 'nav.profile', icon: UserIcon },
    { to: '/event', key: 'nav.event', short: 'nav.event', icon: CalendarDays, wideOnly: true },
  ],
}

function A11yPanel() {
  const { settings, set, setOpen } = useA11y()
  const { t } = useI18n()
  const ref = useDialog<HTMLDivElement>(() => setOpen(false))
  const sizeBtn = (v: 'normal' | 'large' | 'xlarge', label: string) => (
    <button type="button" className={`btn ${settings.textSize === v ? 'btn-primary' : 'btn-quiet'}`}
            aria-pressed={settings.textSize === v}
            onClick={() => set('textSize', v)}>{label}</button>
  )
  const toggle = (k: 'contrast' | 'easierReading' | 'reduceMotion' | 'listen',
                  label: string) => (
    <button type="button" className={`btn ${settings[k] ? 'btn-primary' : 'btn-quiet'}`}
            aria-pressed={settings[k]}
            onClick={() => set(k, !settings[k])}>{label}</button>
  )
  return (
    <div role="dialog" aria-modal="true" aria-label={t('a11y.title')}
         className="fixed inset-0 z-[80] flex items-center justify-center p-4"
         style={{ background: 'rgba(23,23,23,0.4)' }}
         onClick={(e) => { if (e.target === e.currentTarget) setOpen(false) }}>
      <div ref={ref} className="card p-6 w-full max-w-lg"
           style={{ maxHeight: '90vh', overflow: 'auto' }}>
        <div className="flex items-start justify-between gap-3 mb-4">
          <h2 className="m-0">{t('a11y.title')}</h2>
          <CloseButton onClick={() => setOpen(false)} />
        </div>
        <p className="font-medium mb-2">{t('a11y.textsize')}</p>
        <div className="flex gap-2 mb-4 flex-wrap">
          {sizeBtn('normal', t('a11y.normal'))}
          {sizeBtn('large', t('a11y.large'))}
          {sizeBtn('xlarge', t('a11y.xlarge'))}
        </div>
        <div className="flex flex-col gap-2 mb-6">
          {toggle('contrast', t('a11y.contrast'))}
          {toggle('easierReading', t('a11y.reading'))}
          {toggle('reduceMotion', t('a11y.motion'))}
          {toggle('listen', t('a11y.listen'))}
        </div>
        <button type="button" className="btn btn-primary w-full"
                onClick={() => setOpen(false)}>{t('a11y.done')}</button>
      </div>
    </div>
  )
}

function CloseButton({ onClick }: { onClick: () => void }) {
  const { t } = useI18n()
  return (
    <button type="button" className="btn btn-quiet shrink-0" onClick={onClick}
            style={{ minHeight: 44, padding: '6px 12px' }}>
      <X size={20} aria-hidden="true" /> {t('common.close')}
    </button>
  )
}

function MobileMenu({ onClose, children }: { onClose: () => void; children: ReactNode }) {
  const { t } = useI18n()
  const ref = useDialog<HTMLDivElement>(onClose)
  return (
    <div role="dialog" aria-modal="true" aria-label={t('nav.menu')}
         className="fixed inset-0 z-[70] p-4 flex justify-end"
         style={{ background: 'rgba(23,23,23,0.35)' }}
         onClick={(e) => { if (e.target === e.currentTarget) onClose() }}>
      <div ref={ref} className="card p-5 w-full max-w-xs self-start mt-2"
           style={{ maxHeight: '85vh', overflow: 'auto' }}>
        <div className="flex justify-end mb-2"><CloseButton onClick={onClose} /></div>
        {children}
      </div>
    </div>
  )
}

function LangSwitch() {
  const { lang, setLang } = useI18n()
  return (
    <select aria-label="Language" value={lang}
            onChange={(e) => setLang(e.target.value as Lang)}
            style={{ minHeight: 44, width: 'auto' }}>
      {LANGS.map((l) => (
        <option key={l.id} value={l.id}>{l.name}</option>
      ))}
    </select>
  )
}

export default function Layout() {
  const { user, logout } = useAuth()
  const { open, setOpen } = useA11y()
  const { t } = useI18n()
  const nav = useNavigate()
  const loc = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)

  // move focus to the page heading + set document.title on navigation
  useEffect(() => {
    setMenuOpen(false)
    const h = document.querySelector('h1[data-page-title]') as HTMLElement | null
    const base = t('app.name')
    document.title = h?.textContent ? `${h.textContent} — ${base}` : base
    h?.focus()
  }, [loc.pathname, t])

  const role = user?.role ?? 'anon'
  const links = NAV[role] ?? NAV.anon
  const signInTo = `/sign-in?back=${encodeURIComponent(loc.pathname + loc.search)}`

  return (
    <div className="min-h-screen flex flex-col">
      <a href="#main" className="skip-link">{t('nav.skiptocontent')}</a>
      <header className="border-b"
              style={{ borderColor: 'var(--color-hairline)', background: 'var(--color-card)' }}>
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center gap-3">
          <Link to="/" className="no-underline" style={{ color: 'var(--color-ink)' }}>
            <span className="font-display" style={{ fontSize: '1.4rem' }}>{t('app.name')}</span>
          </Link>
          <nav className="top-nav-links flex items-center gap-1 ml-4" aria-label="Main">
            {links.map((l) => (
              <NavLink key={l.to} to={l.to} end={l.to === '/'}
                       className={({ isActive }) =>
                         `px-4 py-2 rounded-xl no-underline ${isActive ? 'font-semibold' : ''}`}
                       style={({ isActive }) => ({
                         color: 'var(--color-ink)',
                         background: isActive ? 'var(--color-canvas)' : 'transparent',
                       })}>
                {t(l.key)}
              </NavLink>
            ))}
          </nav>
          <div className="ml-auto flex items-center gap-2">
            <div className="top-nav-links flex items-center gap-2">
              <button type="button" className="btn btn-quiet" style={{ minHeight: 44 }}
                      onClick={() => setOpen(true)}>
                {t('nav.accessibility')}
              </button>
              <LangSwitch />
              {user ? (
                <div className="flex items-center gap-2">
                  <span className="text-secondary truncate hidden 2xl:block" style={{ maxWidth: 200 }} title={user.name}>{user.name}</span>
                  <button type="button" className="btn btn-secondary" style={{ minHeight: 44 }}
                          onClick={async () => { await logout(); nav('/') }}>
                    {t('nav.signout')}
                  </button>
                </div>
              ) : (
                <Link to={signInTo} className="btn btn-primary" style={{ minHeight: 44 }}>
                  {t('nav.signin')}
                </Link>
              )}
            </div>
            <button type="button" className="btn btn-quiet menu-btn"
                    style={{ minHeight: 44 }}
                    aria-expanded={menuOpen} aria-haspopup="dialog"
                    onClick={() => setMenuOpen((o) => !o)}>
              <MenuIcon size={20} aria-hidden="true" /> {t('nav.menu')}
            </button>
          </div>
        </div>
      </header>

      {menuOpen && (
        <MobileMenu onClose={() => setMenuOpen(false)}>
          {user && <p className="text-secondary mt-0">{user.name}</p>}
          <div className="flex flex-col gap-2 mb-4">
            <button type="button" className="btn btn-quiet justify-start"
                    onClick={() => { setMenuOpen(false); setOpen(true) }}>
              {t('nav.accessibility')}
            </button>
            <LangSwitch />
            {user ? (
              <button type="button" className="btn btn-secondary"
                      onClick={async () => { await logout(); setMenuOpen(false); nav('/') }}>
                {t('nav.signout')}
              </button>
            ) : (
              <Link to={signInTo} className="btn btn-primary"
                    onClick={() => setMenuOpen(false)}>
                {t('nav.signin')}
              </Link>
            )}
          </div>
          <nav aria-label="Main" className="flex flex-col gap-1">
            {links.map((l) => (
              <NavLink key={l.to} to={l.to} end={l.to === '/'}
                       className={({ isActive }) =>
                         `px-4 py-3 rounded-xl no-underline ${isActive ? 'font-semibold' : ''}`}
                       style={({ isActive }) => ({
                         color: 'var(--color-ink)',
                         background: isActive ? 'var(--color-canvas)' : 'transparent',
                       })}
                       onClick={() => setMenuOpen(false)}>
                {t(l.key)}
              </NavLink>
            ))}
          </nav>
        </MobileMenu>
      )}

      <main id="main" className="flex-1 w-full max-w-6xl mx-auto px-4 py-6">
        <Outlet />
      </main>

      <nav className="bottom-nav" aria-label="Main">
        {links.filter((l) => !l.wideOnly).map((l) => {
          const Icon = l.icon
          return (
            <NavLink key={l.to} to={l.to} end={l.to === '/'}
                     className={({ isActive }) => isActive ? 'active' : ''}>
              <Icon size={20} aria-hidden="true" />
              <span>{t(l.short)}</span>
            </NavLink>
          )
        })}
      </nav>

      <footer className="border-t py-6" style={{ borderColor: 'var(--color-hairline)' }}>
        <div className="max-w-6xl mx-auto px-4 text-secondary">
          <p className="mb-2"><strong>{t('footer.accessibility')}</strong> · <strong>{t('footer.data')}</strong></p>
          <p className="m-0 max-w-3xl">{t('footer.datatext')}</p>
        </div>
      </footer>

      {open && <A11yPanel />}
    </div>
  )
}
