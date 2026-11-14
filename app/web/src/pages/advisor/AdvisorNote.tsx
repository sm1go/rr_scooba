import { useState } from 'react'
import { api, ApiError } from '../../lib/api'
import { useConfig } from '../../lib/config'
import { useI18n } from '../../i18n/i18n'
import type { Key } from '../../i18n/en'
import type { AdvisorNote } from '../../types'
import { Chip, ErrorBox, Section } from '../../components/ui'

/** /advisor/note — turn a free-text note into a draft record (§4).
    Nothing is saved automatically; the note text never leaves the page
    except to the assistant endpoint. */
export default function AdvisorNotePage() {
  const { t } = useI18n()
  const cfg = useConfig()
  const [text, setText] = useState('')
  const [note, setNote] = useState<AdvisorNote | null>(null)
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)

  const make = async () => {
    setBusy(true); setErr('')
    try {
      const r = await api<AdvisorNote>('/api/ai/advisor/note', { body: { text } })
      setNote(r)
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : t('advisor.note.err'))
      setNote(null)
    } finally { setBusy(false) }
  }

  return (
    <div className="max-w-3xl mx-auto">
      <h1 data-page-title tabIndex={-1}>{t('advisor.note.title')}</h1>
      {!cfg.ai && <p className="card p-4">{t('ai.off')}</p>}

      <Section title={t('advisor.note.hint')}>
        <textarea rows={8} className="w-full" value={text}
                  onChange={(e) => setText(e.target.value)} />
        <button type="button" className="btn btn-primary mt-2"
                disabled={busy || !text.trim() || !cfg.ai} onClick={make}>
          {t('advisor.note.make')}
        </button>
        {err && <ErrorBox>{err}</ErrorBox>}
      </Section>

      {note && (
        <Section title={t(`advisor.note.type.${note.type}` as Key)}>
          <dl className="m-0">
            {([
              ['profile.name', note.person_name],
              ['help.contact', note.contact_method
                ? `${t(`apply.${note.contact_method}` as Key)}: ${note.contact_value ?? ''}`
                : null],
              ['advisor.note.pick', note.job_hint],
              ['help.what', note.kind ? t(`help.kind.${note.kind}` as Key) : null],
              ['help.message', note.message],
              ['apply.availability', note.availability_note],
              ['apps.reply', note.answer],
            ] as [Key, string | null][]).map(([k, v]) =>
              v ? (
                <div key={k} className="py-2 border-b"
                     style={{ borderColor: 'var(--color-hairline)' }}>
                  <dt className="text-secondary">{t(k)}</dt>
                  <dd className="m-0">{v}</dd>
                </div>
              ) : null)}
            {note.needs.length > 0 && (
              <div className="py-2 border-b" style={{ borderColor: 'var(--color-hairline)' }}>
                <dt className="text-secondary">{t('jobs.needs')}</dt>
                <dd className="m-0">
                  {note.needs.map((n) => (
                    <Chip key={n}>{t(`cond.${n}` as Key)}</Chip>
                  ))}
                </dd>
              </div>
            )}
            {note.conditions.length > 0 && (
              <div className="py-2 border-b" style={{ borderColor: 'var(--color-hairline)' }}>
                <dt className="text-secondary">{t('job.conditions')}</dt>
                <dd className="m-0">
                  {note.conditions.map((c) => (
                    <div key={c.key}>
                      {t(`cond.${c.key}` as Key)}: {t(c.value === 'yes' ? 'common.yes' : 'common.no')}
                      {c.note ? ` — ${c.note}` : ''}
                    </div>
                  ))}
                </dd>
              </div>
            )}
            <div className="py-2">
              <dt className="text-secondary">{t('advisor.note.consent')}</dt>
              <dd className="m-0">
                {note.consent_mentioned ? t('common.yes') : t('common.no')}
              </dd>
            </div>
          </dl>
          {note.left_out.length > 0 && (
            <div className="card p-4 mt-3">
              <p className="m-0 font-medium">{t('advisor.note.leftout')}</p>
              <ul className="m-0 mt-1 pl-5 text-secondary">
                {note.left_out.map((x, i) => <li key={i}>{x}</li>)}
              </ul>
            </div>
          )}
          <p className="text-secondary mt-3">
            Draft only — copy what you need into the right form. Nothing was saved.
          </p>
        </Section>
      )}
    </div>
  )
}
