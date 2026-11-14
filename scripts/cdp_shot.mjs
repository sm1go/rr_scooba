// Drive headless Chrome via CDP: set localStorage (token/lang/a11y),
// optional JS step, screenshot each page.
import { spawn } from 'node:child_process'
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
const SHOTS = join(tmpdir(), 'ewm-shots')
const BASE = 'http://127.0.0.1:5173'
const PORT = 9223
const rd = (f) => readFileSync(join(tmpdir(), f), 'utf8').trim()
const tokAino = rd('tok_aino.txt'), tokSanna = rd('tok_sanna.txt'),
  tokLeena = rd('tok_advisor.txt'), jobId = rd('jobid.txt')

mkdirSync(SHOTS, { recursive: true })
const chrome = spawn(CHROME, [
  '--headless=new', '--disable-gpu', `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${join(tmpdir(), 'ewm-cdp-profile')}`,
  '--window-size=1440,900', 'about:blank',
])
await new Promise((r) => setTimeout(r, 2500))
const targets = await (await fetch(`http://127.0.0.1:${PORT}/json`)).json()
const ws = new WebSocket(targets.find((t) => t.type === 'page').webSocketDebuggerUrl)
await new Promise((r, j) => { ws.onopen = r; ws.onerror = j })
let idSeq = 0
const pending = new Map()
ws.onmessage = (e) => {
  const m = JSON.parse(e.data)
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id) }
}
const send = (method, params = {}) => new Promise((res) => {
  const id = ++idSeq
  pending.set(id, res)
  ws.send(JSON.stringify({ id, method, params }))
})
const sleep = (ms) => new Promise((r) => setTimeout(r, ms))
const js = (expression) => send('Runtime.evaluate', { expression, awaitPromise: true })

async function shot(file, url, {
  width = 1440, height = 900, token, lang, a11y, run, wait = 2600,
} = {}) {
  await send('Emulation.setDeviceMetricsOverride',
    { width, height, deviceScaleFactor: 1, mobile: width < 500 })
  await send('Page.enable')
  await send('Page.navigate', { url: BASE + '/' })
  await sleep(1100)
  const store = ['localStorage.clear()']
  if (token) store.push(`localStorage.setItem('ewm.token', ${JSON.stringify(token)})`)
  if (lang) store.push(`localStorage.setItem('ewm.lang', ${JSON.stringify(lang)})`)
  if (a11y) store.push(`localStorage.setItem('ewm.a11y', ${JSON.stringify(JSON.stringify(a11y))})`)
  if (store.length) await js(store.join(';'))
  await send('Page.navigate', { url: BASE + url })
  await sleep(wait)
  if (run) { await js(run); await sleep(900) }
  const r = await send('Page.captureScreenshot', { format: 'png' })
  writeFileSync(join(SHOTS, file), Buffer.from(r.result.data, 'base64'))
  console.log('wrote', file)
}

await shot('home-wide.png', '/')
await shot('home-360.png', '/', { width: 360, height: 780 })
await shot('home-360-xlarge.png', '/', {
  width: 360, height: 780,
  a11y: { textSize: 'xlarge', contrast: false, easierReading: false, reduceMotion: false, listen: true },
})
await shot('job-detail.png', `/jobs/${jobId}`)
await shot('job-detail-conditions.png', `/jobs/${jobId}`, {
  run: `document.getElementById('job-conditions').scrollIntoView()`,
})
await shot('apply.png', `/jobs/${jobId}/apply`, { token: tokAino })
await shot('applications.png', '/applications', { token: tokAino })
await shot('profile.png', '/profile', { token: tokAino })
await shot('employer-jobs.png', '/employer', { token: tokSanna })
await shot('employer-form-conditions.png', '/employer/jobs/new', {
  token: tokSanna,
  run: `document.querySelector('summary').click();
        [...document.querySelectorAll('ol li button')]
          .find(b => b.textContent.startsWith('8.')).click()`,
  wait: 3200,
})
await shot('employer-applications.png', '/employer/applications', { token: tokSanna })
await shot('advisor-queue.png', '/advisor', { token: tokLeena })
await shot('advisor-followup.png', '/advisor/follow-up', { token: tokLeena })
await shot('sign-in.png', '/sign-in')
await shot('home-fi-contrast.png', '/', {
  lang: 'fi',
  a11y: { textSize: 'normal', contrast: true, easierReading: false, reduceMotion: false, listen: true },
})

ws.close()
chrome.kill()
console.log('done ->', SHOTS)
