import type { Job, SupportProgram } from '../types'

/** Browser-side job_rule evaluator — mirrors app/api/support.py so the
 *  "may fit this job" panel agrees with the server (§7). */
export function jobRuleMatches(rule: string | null, job: Job): boolean {
  if (!rule) return false
  for (const clause of rule.split('and').map((c) => c.trim())) {
    if (clause === 'always') continue
    let m = /^contract in \(([^)]+)\)$/.exec(clause)
    if (m) {
      const allowed = m[1].split(',').map((v) => v.trim())
      if (!job.contract || !allowed.includes(job.contract)) return false
      continue
    }
    m = /^hours_(min|max) >= (\d+)$/.exec(clause)
    if (m) {
      const val = m[1] === 'min' ? job.hours_min : job.hours_max
      if (val === null || val < Number(m[2])) return false
      continue
    }
    return false                              // unknown clause -> no match
  }
  return true
}

/** Employer-side programmes that may fit this job (quiet line on job page). */
export function employerProgramsFor(job: Job, programs: SupportProgram[]): SupportProgram[] {
  return programs.filter((p) => p.job_rule && jobRuleMatches(p.job_rule, job) && p.for_employer)
}

/** Resident matching: ticks stay in component state (§7 privacy). */
export function programsFor(ticks: Set<string>, programs: SupportProgram[]): SupportProgram[] {
  return programs.filter((p) => {
    const all = p.resident_when_all || []
    const any = p.resident_when_any || []
    if (!all.length && !any.length) return false
    if (!all.every((s) => ticks.has(s))) return false
    if (any.length && !any.some((s) => ticks.has(s))) return false
    return true
  })
}
