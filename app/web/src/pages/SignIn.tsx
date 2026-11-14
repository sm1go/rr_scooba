import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { ApiError } from '../lib/api'
import { useAuth } from '../lib/auth'
import { useI18n } from '../i18n/i18n'
import { ErrorBox, Field } from '../components/ui'

const DEMOS: { email: string; label: string }[] = [
  { email: 'aino@example.com', label: 'Aino' },
  { email: 'pekka@example.com', label: 'Pekka' },
  { email: 'amira@example.com', label: 'Amira' },
  { email: 'sanna@example.com', label: 'Sanna' },
  { email: 'advisor@example.com', label: 'Leena' },
]

export default function SignIn() {
  const { t } = useI18n()
  const { login } = useAuth()
  const nav = useNavigate()
  const [params] = useSearchParams()
  const back = params.get('back') || '/'
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)

  const signIn = async (em: string, pw: string) => {
    setBusy(true); setErr('')
    try {
      const u = await login(em, pw)
      nav(u.role === 'employer' ? '/employer'
        : u.role === 'advisor' ? '/advisor' : back)
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : t('auth.wrong'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="max-w-xl mx-auto">
      <h1 data-page-title tabIndex={-1}>{t('auth.signin')}</h1>
      {err && <ErrorBox>{err}</ErrorBox>}
      <form onSubmit={(e) => { e.preventDefault(); signIn(email, password) }}
            className="card p-5">
        <Field label={t('auth.email')} id="si-email">
          <input id="si-email" type="email" required value={email}
                 onChange={(e) => setEmail(e.target.value)} />
        </Field>
        <Field label={t('auth.password')} id="si-pw">
          <input id="si-pw" type="password" required value={password}
                 onChange={(e) => setPassword(e.target.value)} />
        </Field>
        <button className="btn btn-primary w-full" disabled={busy}>
          {t('auth.signin')}
        </button>
        <p className="text-center mt-3 mb-0">
          <Link to="/sign-up">{t('auth.needaccount')}</Link>
        </p>
      </form>

      <div className="card p-5 mt-5" role="region" aria-label="Demo accounts">
        <h2 className="m-0 mb-1" style={{ fontSize: '1.1rem' }}>{t('auth.demo')}</h2>
        <p className="text-secondary mt-0">{t('auth.demohint')}</p>
        <div className="flex flex-wrap gap-2">
          {DEMOS.map((d) => (
            <button key={d.email} type="button" className="btn btn-secondary"
                    disabled={busy}
                    onClick={() => signIn(d.email, 'demo1234')}>
              {d.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
