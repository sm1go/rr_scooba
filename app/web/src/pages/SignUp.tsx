import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { ApiError } from '../lib/api'
import { useAuth } from '../lib/auth'
import { useI18n } from '../i18n/i18n'
import { ErrorBox, Field, Toggle } from '../components/ui'

export default function SignUp() {
  const { t } = useI18n()
  const { register } = useAuth()
  const nav = useNavigate()
  const [params] = useSearchParams()
  const back = params.get('back') || '/'
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState<'resident' | 'employer'>('resident')
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setBusy(true); setErr('')
    try {
      const u = await register({ name, email, password, role })
      nav(u.role === 'employer' ? '/employer' : back)
    } catch (e2) {
      setErr(e2 instanceof ApiError ? e2.message : t('common.error'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="max-w-xl mx-auto">
      <h1 data-page-title tabIndex={-1}>{t('auth.signup')}</h1>
      {err && <ErrorBox>{err}</ErrorBox>}
      <form onSubmit={submit} className="card p-5">
        <div className="flex gap-2 mb-4">
          <Toggle pressed={role === 'resident'} onClick={() => setRole('resident')}>
            {t('auth.resident')}
          </Toggle>
          <Toggle pressed={role === 'employer'} onClick={() => setRole('employer')}>
            {t('auth.employer')}
          </Toggle>
        </div>
        <Field label={t('auth.name')} id="su-name">
          <input id="su-name" required value={name}
                 onChange={(e) => setName(e.target.value)} />
        </Field>
        <Field label={t('auth.email')} id="su-email">
          <input id="su-email" type="email" required value={email}
                 onChange={(e) => setEmail(e.target.value)} />
        </Field>
        <Field label={t('auth.password')} id="su-pw">
          <input id="su-pw" type="password" required minLength={8}
                 value={password}
                 onChange={(e) => setPassword(e.target.value)} />
        </Field>
        <button className="btn btn-primary w-full" disabled={busy}>
          {t('auth.signup')}
        </button>
        <p className="text-center mt-3 mb-0">
          <Link to={`/sign-in?back=${encodeURIComponent(back)}`}>
            {t('auth.haveaccount')}
          </Link>
        </p>
      </form>
    </div>
  )
}
