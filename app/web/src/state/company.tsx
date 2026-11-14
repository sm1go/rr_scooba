import { createContext, useContext, useState } from 'react'
import type { ReactNode } from 'react'
import type { DraftResponse } from '../types'

export const COMPANY_ID = 'co-lumo'
export const TALENT_ID = 'ta-0427'

type Ctx = { draft: DraftResponse | null; setDraft: (d: DraftResponse | null) => void }
const DraftCtx = createContext<Ctx>({ draft: null, setDraft: () => {} })

export function DraftProvider({ children }: { children: ReactNode }) {
  const [draft, setDraft] = useState<DraftResponse | null>(null)
  return <DraftCtx.Provider value={{ draft, setDraft }}>{children}</DraftCtx.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export const useDraft = () => useContext(DraftCtx)
