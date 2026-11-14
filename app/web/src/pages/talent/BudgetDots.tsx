export default function BudgetDots({ budget, used }: { budget: number; used: number }) {
  const left = Math.max(0, budget - used)
  return (
    <p className="inline-flex items-center gap-2 text-sm font-medium" aria-label={`${left} of ${budget} Sparks left`}>
      <span className="flex gap-1" aria-hidden>
        {Array.from({ length: budget }, (_, i) => (
          <span key={i} className={`h-3 w-3 rounded-full border border-nordic ${i < left ? 'bg-nordic' : 'bg-white'}`} />
        ))}
      </span>
      {left} of {budget} left
    </p>
  )
}
