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
  tokLeena = rd('tok_advisor.txt'), jobId = 'job-market-till'

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
  postWait = 1200,
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
  if (run) { await js(run); await sleep(postWait) }
  const r = await send('Page.captureScreenshot', { format: 'png' })
  writeFileSync(join(SHOTS, file), Buffer.from(r.result.data, 'base64'))
  console.log('wrote', file)
}

const typeInto = (id, text) => `
  const inp = document.getElementById(${JSON.stringify(id)});
  const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
  setter.call(inp, ${JSON.stringify(text)});
  inp.dispatchEvent(new Event('input', { bubbles: true }));`
const clickText = (sel, text) =>
  `[...document.querySelectorAll(${JSON.stringify(sel)})]
     .find(b => b.textContent.trim() === ${JSON.stringify(text)})?.click()`
const clickContains = (sel, text) =>
  `[...document.querySelectorAll(${JSON.stringify(sel)})]
     .find(b => b.textContent.includes(${JSON.stringify(text)}))?.click()`

// v3 §2: free-text filter -> "This is what we set"
await shot('home-looking.png', '/', {
  run: `${typeInto('ask-filters', 'two mornings a week near Matinkylä')};
        ${clickText('button', 'Find jobs')}`,
  postWait: 2500,
})
// v3 §3+5: job page station line + simpler-version controls (no key)
await shot('job-v3.png', `/jobs/${jobId}`)
await shot('job-print.png', `/jobs/${jobId}/print`)
// v3 §7: support wizard
await shot('support-1.png', '/support', {
  run: `${clickContains('label', '3 months')}; ${clickContains('label', 'under 30')}`,
})
await shot('support-2.png', '/support', {
  run: `${clickContains('label', '3 months')}; ${clickContains('label', 'under 30')};
        setTimeout(() => ${clickContains('button', 'Show')}, 300)`,
  postWait: 1500,
})
// v3 §1: employer start tiles
await shot('employer-form-start.png', '/employer/jobs/new', { token: tokSanna })
// review step with support panel: manual tile -> all steps -> 10. Preview
await shot('employer-form-review.png', '/employer/jobs/new', {
  token: tokSanna, wait: 3000,
  run: `${clickContains('button', 'myself')};
        setTimeout(() => {
          document.querySelector('details summary')?.click();
          ${clickContains('ol li button', '10.')};
        }, 700)`,
  postWait: 2200,
})
// v3 §4: advisor call script + note (no-key state)
await shot('advisor-call.png', `/advisor/jobs/${jobId}/call`, { token: tokLeena })
await shot('advisor-note.png', '/advisor/note', { token: tokLeena })
// v3 §8: event pages
await shot('event.png', '/event', { token: tokAino, wait: 3200 })
await shot('employer-event.png', '/employer/event', { token: tokSanna, wait: 3200 })
// v3 §6: Arabic RTL
await shot('home-ar-360.png', '/', { lang: 'ar', width: 360, height: 780 })
await shot('home-ar-wide.png', '/', { lang: 'ar' })

ws.close()
chrome.kill()
console.log('done ->', SHOTS)
