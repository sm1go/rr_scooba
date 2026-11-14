import { Languages, Quote } from 'lucide-react'
import { langName } from '../format'
import type { Claim, PublicClaim } from '../types'
import { Chip } from './ui'

export function EvidenceChip({ level }: { level: Claim['evidence_level'] }) {
  return <Chip tone={level === 'own words' ? 'neutral' : 'green'}>Evidence: {level}</Chip>
}

/** A claim with its exact quote. Never shows a score. */
export default function ClaimView({ claim }: { claim: Claim | PublicClaim }) {
  return (
    <div>
      <p className="font-medium">{claim.text}</p>
      <blockquote className="mt-1 flex gap-2 border-l-2 border-line pl-3 text-sm text-muted">
        <Quote aria-hidden className="mt-0.5 h-3.5 w-3.5 shrink-0" />
        <span>“{claim.quote}”</span>
      </blockquote>
      <div className="mt-2 flex flex-wrap gap-2">
        <EvidenceChip level={claim.evidence_level} />
        {claim.esco_label && <Chip tone="blue">{claim.esco_label}</Chip>}
        {'translated' in claim && claim.translated && claim.original_language && (
          <Chip>
            <Languages aria-hidden className="h-3 w-3" /> Translated from {langName(claim.original_language)}
          </Chip>
        )}
      </div>
    </div>
  )
}
