import { Wrench, Car, Utensils, Heart, Building2,
         ShoppingCart, Briefcase, Headset, BookOpen, Hammer,
         Cpu, Leaf, Factory, Stethoscope, Brush } from 'lucide-react'

const FIELD_ICON: Record<string, typeof Brush> = {
  cleaning: Brush, retail: ShoppingCart, restaurant: Utensils,
  care: Heart, logistics: Car, office: Briefcase,
  customer_service: Headset, education: BookOpen,
  construction: Hammer, tech: Cpu, seasonal: Leaf,
  manufacturing: Factory, health: Stethoscope,
  maintenance: Wrench, office_work: Building2,
}

const LEGAL = new Set(['oy', 'ab', 'ky', 'oyj', 'tmi', 'ry'])

function monogram(name: string): string {
  const words = name.split(/\s+/)
    .filter((w) => !LEGAL.has(w.toLowerCase().replace(/[.,]/g, '')))
  return words.slice(0, 2).map((w) => w[0]).join('').toUpperCase() || '?'
}

/** SVG logo: coloured rounded square + monogram + field icon. */
export default function CompanyLogo({ employer, size = 48 }: {
  employer: { name: string; logo_color?: string; field?: string }
  size?: number
}) {
  const color = employer.logo_color || '#3f3f46'
  const Icon = FIELD_ICON[employer.field ?? ''] ?? Building2
  const ic = Math.round(size * 0.42)
  return (
    <span role="img" aria-label={`${employer.name} logo`}
          style={{ width: size, height: size, flexShrink: 0,
                   display: 'inline-block', position: 'relative' }}>
      <svg width={size} height={size} viewBox="0 0 48 48"
           aria-hidden="true">
        <rect width="48" height="48" rx="10" fill={color} />
        <text x="24" y="30" textAnchor="middle" fontSize="18"
              fontWeight="700" fill="#fff"
              fontFamily="system-ui, sans-serif">
          {monogram(employer.name)}
        </text>
      </svg>
      <span style={{ position: 'absolute', right: -4, bottom: -4,
                     background: 'var(--color-card, #fff)',
                     borderRadius: 6, padding: 1, lineHeight: 0 }}>
        <Icon size={ic} aria-hidden="true" />
      </span>
    </span>
  )
}
