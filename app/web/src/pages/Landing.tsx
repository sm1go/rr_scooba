import { Link } from 'react-router-dom'
import { Building2, UserRound, LayoutGrid, ArrowRight } from 'lucide-react'

const roles = [
  {
    to: '/company',
    icon: Building2,
    title: 'Company',
    who: 'Sanna, Lumo Systems Oy',
    text: 'Describe a real problem you need solved in 90 days, and see how many people could help — before you ask anyone.',
  },
  {
    to: '/talent',
    icon: UserRound,
    title: 'Talent',
    who: 'Amira, backend engineer',
    text: 'Tell a work story in your own words, keep only what you can show, and send a few Sparks to companies.',
  },
  {
    to: '/organiser',
    icon: LayoutGrid,
    title: 'Organiser',
    who: 'City of Espoo event team',
    text: 'See how the event is going and check that the assistant treats everyone the same.',
  },
]

export default function Landing() {
  return (
    <div>
      <h1 className="text-3xl sm:text-4xl">Proof, not prose.</h1>
      <p className="mt-3 max-w-2xl text-lg text-muted">
        Companies bring a problem, talent brings proof, Espoo sets the table. A demo for the TalentMatch Espoo · Tech &amp; ICT
        event on 26 November 2026.
      </p>
      <h2 className="mt-10 mb-4 text-xl">Choose your role</h2>
      <ul className="grid gap-4 sm:grid-cols-3">
        {roles.map((r) => (
          <li key={r.to}>
            <Link
              to={r.to}
              className="flex h-full flex-col rounded-lg border border-line bg-white p-5 text-ink no-underline hover:border-nordic"
            >
              <r.icon aria-hidden className="h-6 w-6 text-nordic" />
              <span className="mt-3 text-lg font-semibold">{r.title}</span>
              <span className="text-sm text-muted">{r.who}</span>
              <span className="mt-3 flex-1">{r.text}</span>
              <span className="mt-4 inline-flex items-center gap-1 font-medium text-nordic">
                Start <ArrowRight aria-hidden className="h-4 w-4" />
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}
