import { useEffect, useMemo, useRef, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api, ApiError } from '../../lib/api'
import { useAuth } from '../../lib/auth'
import { useConfig } from '../../lib/config'
import { useI18n } from '../../i18n/i18n'
import type { Key } from '../../i18n/en'
import type { Catalog, Job, JobDraft, SupportCatalogue, WordingTip } from '../../types'
import { CEFR, DAYS } from '../../types'
import { ErrorBox, Field, Section, Toggle } from '../../components/ui'
import { employerProgramsFor } from '../../lib/support'

const STEPS = ['title', 'duties', 'where', 'pay', 'hours', 'contract',
               'language', 'conditions', 'apply', 'preview'] as const

interface Form {
  employer_id: string;
  title: string; field: string; duties: string; address: string;
  district: string; work_mode: 'on_site' | 'hybrid' | 'remote';
  pay_amount: string; pay_unit: 'hour' | 'month'; pay_note: string;
  shifts: { day: string; start: string; end: string }[];
  schedule_flexible: boolean; hours_min: string; hours_max: string;
  contract: string; experience: string; experience_note: string;
  qualifications: string; onboarding: string;
  languages: { language: string; level: string; task: string }[];
  lifting: string; apply_question: string; cv_required: boolean;
  positions: number; conditions: Record<string, string>;
}

const EMPTY: Form = {
  employer_id: '',
  title: '', field: '', duties: '', address: '', district: '',
  work_mode: 'on_site', pay_amount: '', pay_unit: 'hour', pay_note: '',
  shifts: [], schedule_flexible: false, hours_min: '', hours_max: '',
  contract: '', experience: '', experience_note: '', qualifications: '',
  onboarding: '', languages: [], lifting: '', apply_question: '',
  cv_required: false, positions: 1, conditions: {},
}

export default function EmployerJobForm() {
  const { t } = useI18n()
  const { user } = useAuth()
  const cfg = useConfig()
  const { id } = useParams()
  const nav = useNavigate()
  const [cat, setCat] = useState<Catalog | null>(null)
  const [f, setF] = useState<Form>(EMPTY)
  const [step, setStep] = useState(0)
  const [tips, setTips] = useState<WordingTip[]>([])
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)
  const [loaded, setLoaded] = useState(false)
  // v3 photo/text draft flow (§1)
  const [phase, setPhase] = useState<'start' | 'text' | 'form'>(id ? 'form' : 'start')
  const [noticeText, setNoticeText] = useState('')
  const [draftBusy, setDraftBusy] = useState(false)
  const [aiFields, setAiFields] = useState<Set<string>>(new Set())
  const [missing, setMissing] = useState<string[]>([])
  const [quotes, setQuotes] = useState<Record<string, string>>({})
  const [aiWarnings, setAiWarnings] = useState<string[]>([])
  const [supportAsked, setSupportAsked] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    api<Catalog>('/api/catalog').then(setCat).catch(() => {})
  }, [])

  useEffect(() => {
    if (!id) { setLoaded(true); return }
    api<Job>(`/api/jobs/${id}`).then((j) => {
      setF({
        ...EMPTY,
        employer_id: j.employer_id,
        title: j.title, field: j.field, duties: j.duties.join('\n'),
        address: j.address, district: j.district, work_mode: j.work_mode,
        pay_amount: j.pay_amount != null ? String(j.pay_amount) : '',
        pay_unit: j.pay_unit ?? 'hour', pay_note: j.pay_note,
        shifts: j.shifts, schedule_flexible: j.schedule_flexible,
        hours_min: j.hours_min != null ? String(j.hours_min) : '',
        hours_max: j.hours_max != null ? String(j.hours_max) : '',
        contract: j.contract ?? '', experience: j.experience ?? '',
        experience_note: j.experience_note,
        qualifications: j.qualifications.join('\n'),
        onboarding: j.onboarding, languages: j.languages,
        lifting: j.lifting ?? '', apply_question: j.apply_question,
        cv_required: j.cv_required, positions: j.positions,
        conditions: Object.fromEntries(
          j.conditions.filter((c) => c.value !== 'unknown')
            .map((c) => [c.key, c.value])),
      })
      setLoaded(true)
    }).catch((e) => setErr(e instanceof ApiError ? e.message : t('common.error')))
  }, [id, t])

  const checkWording = async () => {
    try {
      const r = await api<{ tips: WordingTip[] }>('/api/jobs/check-wording', {
        body: {
          title: f.title, pay_note: f.pay_note,
          experience_note: f.experience_note, onboarding: f.onboarding,
          apply_question: f.apply_question, lifting: f.lifting || '',
          duties: f.duties.split('\n').filter(Boolean),
          qualifications: f.qualifications.split('\n').filter(Boolean),
          languages: f.languages,
        },
      })
      setTips(r.tips)
    } catch { /* tips are optional */ }
  }

  const save = async (status: 'draft' | 'open') => {
    setBusy(true); setErr('')
    const body = {
      employer_id: f.employer_id || undefined,
      title: f.title, field: f.field,
      duties: f.duties.split('\n').map((s) => s.trim()).filter(Boolean),
      address: f.address, district: f.district, work_mode: f.work_mode,
      pay_amount: f.pay_amount ? +f.pay_amount : null,
      pay_unit: f.pay_amount ? f.pay_unit : null,
      pay_note: f.pay_note, shifts: f.shifts,
      schedule_flexible: f.schedule_flexible,
      hours_min: f.hours_min ? +f.hours_min : null,
      hours_max: f.hours_max ? +f.hours_max : null,
      contract: f.contract || null, experience: f.experience || null,
      experience_note: f.experience_note,
      qualifications: f.qualifications.split('\n').map((s) => s.trim()).filter(Boolean),
      onboarding: f.onboarding, languages: f.languages.filter((l) => l.language),
      lifting: f.lifting || null, apply_question: f.apply_question,
      cv_required: f.cv_required, positions: f.positions, status,
      conditions: f.conditions,
    }
    try {
      if (id) await api(`/api/jobs/${id}`, { method: 'PUT', body })
      else await api('/api/jobs', { body })
      nav(user?.role === 'advisor' ? '/advisor/jobs' : '/employer')
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : t('common.error'))
    } finally {
      setBusy(false)
    }
  }

  const stepIds = useMemo(() => STEPS, [])

  // --- photo / text -> draft (§1) -------------------------------------------

  const applyDraft = (r: JobDraft) => {
    const d = r.draft as Record<string, unknown>
    const filled = new Set<string>()
    const nf: Form = { ...EMPTY, employer_id: f.employer_id }
    const take = (k: keyof Form, src: string, v: unknown) => {
      if (v === null || v === undefined || v === '') return
      ;(nf as unknown as Record<string, unknown>)[k] = v
      filled.add(src)
    }
    take('title', 'title', d.title)
    take('field', 'field', d.field)
    if (Array.isArray(d.duties) && d.duties.length) {
      nf.duties = (d.duties as string[]).join('\n'); filled.add('duties')
    }
    take('address', 'address', d.address)
    take('district', 'district', d.district)
    take('work_mode', 'work_mode', d.work_mode)
    take('pay_amount', 'pay_amount', d.pay_amount != null ? String(d.pay_amount) : null)
    take('pay_unit', 'pay_unit', d.pay_unit)
    take('pay_note', 'pay_note', d.pay_note)
    if (Array.isArray(d.shifts)) {
      nf.shifts = d.shifts as Form['shifts']; if (nf.shifts.length) filled.add('shifts')
    }
    take('schedule_flexible', 'shifts', d.schedule_flexible === true ? true : null)
    take('hours_min', 'hours', d.hours_min != null ? String(d.hours_min) : null)
    take('hours_max', 'hours', d.hours_max != null ? String(d.hours_max) : null)
    take('contract', 'contract', d.contract)
    take('experience', 'experience', d.experience)
    take('experience_note', 'experience_note', d.experience_note)
    take('positions', 'positions', typeof d.positions === 'number' ? d.positions : null)
    if (Array.isArray(d.qualifications) && d.qualifications.length) {
      nf.qualifications = (d.qualifications as string[]).join('\n')
      filled.add('qualifications')
    }
    take('onboarding', 'onboarding', d.onboarding)
    if (Array.isArray(d.languages) && d.languages.length) {
      nf.languages = d.languages as Form['languages']; filled.add('languages')
    }
    take('lifting', 'lifting', d.lifting)
    take('apply_question', 'apply_question', d.apply_question)
    take('cv_required', 'cv_required', d.cv_required === true ? true : null)
    if (d.conditions && typeof d.conditions === 'object') {
      nf.conditions = d.conditions as Record<string, string>
      if (Object.keys(nf.conditions).length) filled.add('conditions')
    }
    setF(nf)
    setAiFields(filled)
    setMissing(r.missing)
    setQuotes(r.source_quotes || {})
    setAiWarnings(r.wording_warnings || [])
    setPhase('form')
    setStep(0)
  }

  const draft = async (body: Record<string, unknown>) => {
    setDraftBusy(true); setErr('')
    try {
      const r = await api<JobDraft>('/api/ai/job-draft', { body })
      applyDraft(r)
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : t('common.error'))
    } finally { setDraftBusy(false) }
  }

  const readPhoto = (file: File) => {
    const img = new Image()
    img.onload = () => {
      const scale = Math.min(1, 1600 / Math.max(img.width, img.height))
      const c = document.createElement('canvas')
      c.width = Math.round(img.width * scale)
      c.height = Math.round(img.height * scale)
      c.getContext('2d')!.drawImage(img, 0, 0, c.width, c.height)
      URL.revokeObjectURL(img.src)
      const mime = 'image/jpeg'
      draft({ image_base64: c.toDataURL(mime, 0.85).split(',')[1], image_mime: mime })
    }
    img.onerror = () => setErr(t('common.error'))
    img.src = URL.createObjectURL(file)
  }

  const mark = (k: string) => aiFields.has(k) ? (
    <p className="text-secondary m-0 mb-2" style={{ fontSize: '1rem' }}>
      {t('employer.fromphoto')}
      {quotes[k] && (
        <details className="mt-1">
          <summary className="cursor-pointer">{t('employer.fromphoto.quote')}</summary>
          <p className="m-0 mt-1">{quotes[k]}</p>
        </details>
      )}
    </p>
  ) : null

  if (!loaded) return <p>{t('common.loading')}</p>
  const cur = stepIds[step]

  // --- start screen: three large tiles (§1) ----------------------------------
  if (phase === 'start') {
    return (
      <div className="max-w-3xl mx-auto">
        <Link to={user?.role === 'advisor' ? '/advisor/jobs' : '/employer'}
              className="text-secondary">{`← ${t('common.back')}`}</Link>
        <h1 data-page-title tabIndex={-1} className="mt-2">
          {t('employer.start.title')}
        </h1>
        {err && <ErrorBox>{err}</ErrorBox>}
        {!cfg.ai && <p className="card p-4">{t('employer.start.ai_off')}</p>}

        <div className="grid gap-3 md:grid-cols-3">
          <button type="button" className="card p-6 text-left start-tile"
                  disabled={draftBusy || !cfg.ai}
                  onClick={() => fileRef.current?.click()}>
            <span className="font-display block" style={{ fontSize: '1.2rem' }}>
              {t('employer.start.photo')}
            </span>
          </button>
          <button type="button" className="card p-6 text-left start-tile"
                  disabled={!cfg.ai}
                  onClick={() => setPhase('text' as 'start')}>
            <span className="font-display block" style={{ fontSize: '1.2rem' }}>
              {t('employer.start.text')}
            </span>
          </button>
          <button type="button" className="card p-6 text-left start-tile"
                  onClick={() => setPhase('form')}>
            <span className="font-display block" style={{ fontSize: '1.2rem' }}>
              {t('employer.start.manual')}
            </span>
          </button>
        </div>
        <input ref={fileRef} type="file" accept="image/*" capture="environment"
               className="hidden" aria-hidden="true" tabIndex={-1}
               onChange={(e) => { const fl = e.target.files?.[0]; if (fl) readPhoto(fl) }} />
        {draftBusy && <p role="status">{t('employer.drafting')}</p>}
        <p className="text-secondary mt-2">{t('employer.notice')}</p>
      </div>
    )
  }
  if (phase === 'text') {
    return (
      <div className="max-w-3xl mx-auto">
        <button type="button" className="btn btn-quiet"
                onClick={() => setPhase('start')}>{`← ${t('employer.start.back')}`}</button>
        <h1 data-page-title tabIndex={-1} className="mt-2">{t('employer.start.text')}</h1>
        {err && <ErrorBox>{err}</ErrorBox>}
        <Field label={t('employer.start.textlabel')} id="notice-text">
          <textarea id="notice-text" rows={10} value={noticeText}
                    onChange={(e) => setNoticeText(e.target.value)} />
        </Field>
        <button type="button" className="btn btn-primary"
                disabled={draftBusy || !noticeText.trim()}
                onClick={() => draft({ text: noticeText })}>
          {draftBusy ? t('employer.drafting') : t('employer.start.read')}
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto">
      <Link to={user?.role === 'advisor' ? '/advisor/jobs' : '/employer'}
            className="text-secondary">{`← ${t('common.back')}`}</Link>
      <h1 data-page-title tabIndex={-1} className="mt-2">
        {id ? t('employer.editjob') : t('employer.newjob')}
      </h1>
      {err && <ErrorBox>{err}</ErrorBox>}

      <div className="mb-5">
        <p className="font-medium mb-2" aria-current="step">
          {t('employer.steps')} {step + 1} / {stepIds.length} — {t(`employer.step.${cur}` as Key)}
        </p>
        <div className="flex gap-1" aria-hidden="true">
          {stepIds.map((s, i) => (
            <div key={s} className="flex-1 rounded-full" style={{
              height: 6,
              background: i <= step ? 'var(--color-ink)' : 'var(--color-hairline)',
            }} />
          ))}
        </div>
        <details className="mt-2">
          <summary className="cursor-pointer text-secondary">
            {t('common.allsteps')}
          </summary>
          <ol className="grid gap-1 list-none p-0 mt-2 md:grid-cols-2">
            {stepIds.map((s, i) => (
              <li key={s}>
                <button type="button"
                        onClick={() => { setStep(i); checkWording() }}
                        className="btn btn-quiet w-full justify-start"
                        style={{ minHeight: 44 }}
                        aria-current={i === step ? 'step' : undefined}>
                  {i + 1}. {t(`employer.step.${s}` as Key)}
                </button>
              </li>
            ))}
          </ol>
        </details>
      </div>

      {cur === 'title' && (
        <Section title={t('employer.step.title')}>
          {mark('title')}{mark('field')}
          {user?.role === 'advisor' && (
            <Field label={t('employer.company')} id="jf-emp">
              <select id="jf-emp" value={f.employer_id} required
                      onChange={(e) => setF({ ...f, employer_id: e.target.value })}>
                <option value="">—</option>
                {cat?.employers.map((e2) => (
                  <option key={e2.id} value={e2.id}>{e2.name}</option>
                ))}
              </select>
            </Field>
          )}
          <Field label={t('employer.jobtitle')} id="jf-title">
            <input id="jf-title" required value={f.title}
                   onChange={(e) => setF({ ...f, title: e.target.value })} />
          </Field>
          <fieldset className="m-0 p-0 border-0">
            <legend className="font-medium mb-2">{t('jobs.kind')}</legend>
            <div className="grid gap-2" role="radiogroup"
                 style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(170px, 1fr))' }}>
              {cat?.fields.map((x) => (
                <Toggle key={x.id} pressed={f.field === x.id}
                        onClick={() => setF({ ...f, field: x.id })}
                        className="justify-start text-left">
                  {x.name}
                </Toggle>
              ))}
            </div>
          </fieldset>
        </Section>
      )}

      {cur === 'duties' && (
        <Section title={t('employer.step.duties')}>
          {mark('duties')}
          <Field label={t('employer.dutieshelp')} id="jf-duties">
            <textarea id="jf-duties" rows={6} value={f.duties}
                      onChange={(e) => setF({ ...f, duties: e.target.value })} />
          </Field>
        </Section>
      )}

      {cur === 'where' && (
        <Section title={t('employer.step.where')}>
          {mark('address')}{mark('district')}{mark('work_mode')}
          <Field label={t('job.where')} id="jf-address">
            <input id="jf-address" value={f.address}
                   onChange={(e) => setF({ ...f, address: e.target.value })} />
          </Field>
          <Field label={t('jobs.area')} id="jf-district">
            <select id="jf-district" value={f.district}
                    onChange={(e) => setF({ ...f, district: e.target.value })}>
              <option value="">—</option>
              {cat?.districts.map((d) => (
                <option key={d.id} value={d.id}>{d.name}</option>
              ))}
            </select>
          </Field>
          <Field label={t('jobs.workmode')} id="jf-mode">
            <select id="jf-mode" value={f.work_mode}
                    onChange={(e) => setF({ ...f, work_mode: e.target.value as Form['work_mode'] })}>
              <option value="on_site">{t('common.onsite')}</option>
              <option value="hybrid">{t('common.hybrid')}</option>
              <option value="remote">{t('common.remote')}</option>
            </select>
          </Field>
        </Section>
      )}

      {cur === 'pay' && (
        <Section title={t('employer.step.pay')}>
          {mark('pay_amount')}{mark('pay_unit')}{mark('pay_note')}
          <div className="flex gap-2">
            <Field label={t('job.pay')} id="jf-pay">
              <input id="jf-pay" type="number" step="0.01" inputMode="decimal"
                     value={f.pay_amount}
                     onChange={(e) => setF({ ...f, pay_amount: e.target.value })} />
            </Field>
            <Field label={t('employer.payunit')} id="jf-unit">
              <select id="jf-unit" value={f.pay_unit}
                      onChange={(e) => setF({ ...f, pay_unit: e.target.value as 'hour' | 'month' })}>
                <option value="hour">{t('common.perhour')}</option>
                <option value="month">{t('common.permonth')}</option>
              </select>
            </Field>
          </div>
          <Field label={t('employer.paynote')} id="jf-paynote">
            <input id="jf-paynote" value={f.pay_note}
                   onChange={(e) => setF({ ...f, pay_note: e.target.value })} />
          </Field>
        </Section>
      )}

      {cur === 'hours' && (
        <Section title={t('employer.step.hours')}>
          {mark('shifts')}{mark('hours')}
          <Toggle pressed={f.schedule_flexible}
                  onClick={() => setF({ ...f, schedule_flexible: !f.schedule_flexible })}>
            {t('common.flexible')}
          </Toggle>
          <div className="flex gap-2 mt-3">
            <Field label={t('employer.hoursmin')} id="jf-hmin">
              <input id="jf-hmin" type="number" inputMode="numeric" value={f.hours_min}
                     onChange={(e) => setF({ ...f, hours_min: e.target.value })} />
            </Field>
            <Field label={t('employer.hoursmax')} id="jf-hmax">
              <input id="jf-hmax" type="number" inputMode="numeric" value={f.hours_max}
                     onChange={(e) => setF({ ...f, hours_max: e.target.value })} />
            </Field>
          </div>
          {!f.schedule_flexible && (
            <div className="mt-3">
              <p className="font-medium">{t('employer.shiftshelp')}</p>
              {f.shifts.map((s, i) => (
                <div key={i} className="flex gap-2 mb-2 items-center">
                  <select value={s.day} aria-label={t('jobs.whenwork')}
                          onChange={(e) => setF({
                            ...f,
                            shifts: f.shifts.map((x, j) =>
                              j === i ? { ...x, day: e.target.value } : x),
                          })}>
                    {DAYS.map((d) => (
                      <option key={d} value={d}>{t(`dayfull.${d}` as Key)}</option>
                    ))}
                  </select>
                  <input type="time" value={s.start} aria-label="start"
                         onChange={(e) => setF({
                           ...f,
                           shifts: f.shifts.map((x, j) =>
                             j === i ? { ...x, start: e.target.value } : x),
                         })} />
                  <input type="time" value={s.end} aria-label="end"
                         onChange={(e) => setF({
                           ...f,
                           shifts: f.shifts.map((x, j) =>
                             j === i ? { ...x, end: e.target.value } : x),
                         })} />
                  <button type="button" className="btn btn-quiet" style={{ minHeight: 40 }}
                          onClick={() => setF({ ...f, shifts: f.shifts.filter((_, j) => j !== i) })}
                          aria-label={t('common.delete')}>✕</button>
                </div>
              ))}
              <button type="button" className="btn btn-secondary"
                      onClick={() => setF({
                        ...f,
                        shifts: [...f.shifts, { day: 'mon', start: '09:00', end: '17:00' }],
                      })}>
                {t('employer.addshift')}
              </button>
            </div>
          )}
        </Section>
      )}

      {cur === 'contract' && (
        <Section title={t('employer.step.contract')}>
          {mark('contract')}{mark('experience')}{mark('experience_note')}
          {mark('positions')}{mark('qualifications')}{mark('onboarding')}
          <Field label={t('jobs.contract')} id="jf-contract">
            <select id="jf-contract" value={f.contract}
                    onChange={(e) => setF({ ...f, contract: e.target.value })}>
              <option value="">—</option>
              {cat?.contract_types.map((c) => (
                <option key={c} value={c}>{t(`contract.${c}` as Key)}</option>
              ))}
            </select>
          </Field>
          <Field label={t('jobs.experience')} id="jf-exp">
            <select id="jf-exp" value={f.experience}
                    onChange={(e) => setF({ ...f, experience: e.target.value })}>
              <option value="">—</option>
              {['none', 'some', 'required'].map((x) => (
                <option key={x} value={x}>{t(`experience.${x}` as Key)}</option>
              ))}
            </select>
          </Field>
          <Field label={t('employer.expnote')} id="jf-expnote">
            <input id="jf-expnote" value={f.experience_note}
                   onChange={(e) => setF({ ...f, experience_note: e.target.value })} />
          </Field>
          <Field label={t('employer.positions')} id="jf-pos">
            <input id="jf-pos" type="number" min="1" inputMode="numeric"
                   value={f.positions}
                   onChange={(e) => setF({ ...f, positions: +e.target.value || 1 })} />
          </Field>
          <Field label={t('job.whatyouneed')} id="jf-quals">
            <textarea id="jf-quals" rows={4} value={f.qualifications}
                      placeholder={t('employer.qualshelp')}
                      onChange={(e) => setF({ ...f, qualifications: e.target.value })} />
          </Field>
          <Field label={t('job.training')} id="jf-onb">
            <input id="jf-onb" value={f.onboarding}
                   onChange={(e) => setF({ ...f, onboarding: e.target.value })} />
          </Field>
        </Section>
      )}

      {cur === 'language' && (
        <Section title={t('employer.step.language')}>
          {mark('languages')}
          {f.languages.map((l, i) => (
            <div key={i} className="flex gap-2 mb-2 items-center flex-wrap">
              <input value={l.language} aria-label={t('jobs.language')}
                     onChange={(e) => setF({
                       ...f,
                       languages: f.languages.map((x, j) =>
                         j === i ? { ...x, language: e.target.value } : x),
                     })} />
              <select value={l.level} aria-label={t('jobs.mylevel')}
                      onChange={(e) => setF({
                        ...f,
                        languages: f.languages.map((x, j) =>
                          j === i ? { ...x, level: e.target.value } : x),
                      })}>
                {CEFR.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
              <input value={l.task} aria-label={t('employer.languagetask')}
                     placeholder={t('employer.languagetask')}
                     onChange={(e) => setF({
                       ...f,
                       languages: f.languages.map((x, j) =>
                         j === i ? { ...x, task: e.target.value } : x),
                     })} />
              <button type="button" className="btn btn-quiet" style={{ minHeight: 40 }}
                      onClick={() => setF({ ...f, languages: f.languages.filter((_, j) => j !== i) })}
                      aria-label={t('common.delete')}>✕</button>
            </div>
          ))}
          <button type="button" className="btn btn-secondary"
                  onClick={() => setF({
                    ...f,
                    languages: [...f.languages, { language: 'Finnish', level: 'B1', task: '' }],
                  })}>
            {t('profile.addlang')}
          </button>
        </Section>
      )}

      {cur === 'conditions' && (
        <Section title={t('employer.step.conditions')}>
          {mark('conditions')}{mark('lifting')}
          <p className="text-secondary mt-0">{t('employer.conditionshelp')}</p>
          {cat?.condition_keys.map((c) => (
            <div key={c.id}
                 className="flex flex-wrap items-center justify-between gap-2 py-2 border-b"
                 style={{ borderColor: 'var(--color-hairline)' }}>
              <span>{t(`cond.${c.id}` as Key)}</span>
              <div className="flex gap-2">
                {(['yes', 'no'] as const).map((v) => (
                  <Toggle key={v}
                          pressed={f.conditions[c.id] === v}
                          onClick={() => setF({
                            ...f,
                            conditions: {
                              ...f.conditions,
                              [c.id]: f.conditions[c.id] === v ? 'unknown' : v,
                            },
                          })}>
                    {v === 'yes' ? t('common.yes') : t('common.no')}
                  </Toggle>
                ))}
              </div>
            </div>
          ))}
          <Field label={t('job.lifting')} id="jf-lift">
            <input id="jf-lift" value={f.lifting}
                   onChange={(e) => setF({ ...f, lifting: e.target.value })} />
          </Field>
        </Section>
      )}

      {cur === 'apply' && (
        <Section title={t('employer.step.apply')}>
          {mark('apply_question')}{mark('cv_required')}
          <Field label={t('employer.applyquestion')} id="jf-q">
            <input id="jf-q" value={f.apply_question}
                   onChange={(e) => setF({ ...f, apply_question: e.target.value })} />
          </Field>
          <Toggle pressed={f.cv_required}
                  onClick={() => setF({ ...f, cv_required: !f.cv_required })}>
            {t('employer.cvrequired')}
          </Toggle>
        </Section>
      )}

      {cur === 'preview' && (
        <Section title={t('employer.step.preview')}>
          {missing.length > 0 && (
            <div className="card p-4 mb-4">
              <h3 className="m-0 mb-2" style={{ fontSize: '1.05rem' }}>
                {t('employer.missing')}
              </h3>
              <ul className="m-0 pl-5">
                {missing.map((k) => <li key={k}>{k}</li>)}
              </ul>
            </div>
          )}
          <h2 className="m-0 font-display">{f.title || '—'}</h2>
          <p className="text-secondary">{f.address} {f.district && `· ${f.district}`}</p>
          <ul className="pl-5">
            {f.duties.split('\n').filter(Boolean).map((d, i) => (
              <li key={i}>{d}</li>
            ))}
          </ul>
          {aiWarnings.length > 0 && (
            <div className="card p-4 mb-4">
              <h3 className="m-0 mb-2" style={{ fontSize: '1.05rem' }}>
                {t('employer.wordingtips')}
              </h3>
              {aiWarnings.map((w, i) => <p key={i} className="m-0 mb-2">{w}</p>)}
            </div>
          )}
          <SupportPanel form={f} asked={supportAsked}
                        onAsk={async () => {
                          try {
                            await api('/api/help-requests', {
                              body: {
                                kind: 'employer_support',
                                message: `${f.title} — ${t('employer.support.title')}`,
                                consent: true,
                              },
                            })
                            setSupportAsked(true)
                          } catch (e) {
                            setErr(e instanceof ApiError ? e.message : t('common.error'))
                          }
                        }} />
          {tips.length > 0 && (
            <div className="card p-4 mb-4" role="region"
                 aria-label={t('employer.wordingtips')}>
              <h3 className="m-0 mb-2" style={{ fontSize: '1.05rem' }}>
                {t('employer.wordingtips')}
              </h3>
              {tips.map((tip) => (
                <p key={tip.id} className="m-0 mb-2">
                  <strong>{tip.trigger}</strong> — {tip.why}
                  {tip.suggestion && (
                    <span className="text-secondary"> → {tip.suggestion}</span>
                  )}
                </p>
              ))}
            </div>
          )}
          <Link to="/help" className="text-secondary">
            {t('employer.askadvisor')}
          </Link>
        </Section>
      )}

      {cur !== 'preview' && tips.length > 0 && (
        <div className="card p-4 mb-4" role="region"
             aria-label={t('employer.wordingtips')}>
          <h3 className="m-0 mb-2" style={{ fontSize: '1.05rem' }}>
            {t('employer.wordingtips')}
          </h3>
          {tips.map((tip) => (
            <p key={tip.id} className="m-0 mb-2">
              <strong>{tip.trigger}</strong> — {tip.why}
            </p>
          ))}
        </div>
      )}

      <div className="flex gap-2 mt-6 flex-wrap">
        {step > 0 && (
          <button type="button" className="btn btn-secondary"
                  onClick={() => setStep((s) => s - 1)}>
            {t('common.back')}
          </button>
        )}
        {step < stepIds.length - 1 && (
          <button type="button" className="btn btn-primary"
                  onClick={() => { setStep((s) => s + 1); checkWording() }}>
            {t('common.next')}
          </button>
        )}
        {cur === 'preview' && (
          <>
            <button type="button" className="btn btn-secondary" disabled={busy}
                    onClick={() => save('draft')}>
              {t('employer.savedraft')}
            </button>
            <button type="button" className="btn btn-primary" disabled={busy}
                    onClick={() => save('open')}>
              {t('employer.publish')}
            </button>
          </>
        )}
      </div>
    </div>
  )
}

/** "City support that may fit this job" on the review step (§7). */
function SupportPanel({ form, asked, onAsk }: {
  form: Form; asked: boolean; onAsk: () => void
}) {
  const { t } = useI18n()
  const [matches, setMatches] = useState<{ name: string; amount: string }[]>([])
  useEffect(() => {
    api<SupportCatalogue>('/api/support').then((c) => {
      const pseudo = {
        contract: form.contract || null,
        hours_min: form.hours_min ? +form.hours_min : null,
        hours_max: form.hours_max ? +form.hours_max : null,
      } as Job
      setMatches(employerProgramsFor(pseudo, c.programs)
        .map((p) => ({ name: p.name, amount: p.amount })))
    }).catch(() => undefined)
  }, [form.contract, form.hours_min, form.hours_max])

  if (!matches.length) return null
  return (
    <div className="card p-4 mb-4">
      <h3 className="m-0 mb-2" style={{ fontSize: '1.05rem' }}>
        {t('employer.support.title')}
      </h3>
      <ul className="m-0 pl-5 mb-3">
        {matches.map((m, i) => <li key={i}>{m.name} — {m.amount}</li>)}
      </ul>
      {asked ? (
        <p className="m-0">{t('employer.support.sent')}</p>
      ) : (
        <button type="button" className="btn btn-secondary" onClick={onAsk}>
          {t('employer.support.call')}
        </button>
      )}
    </div>
  )
}
