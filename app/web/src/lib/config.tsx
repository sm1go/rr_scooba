import { createContext, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { api } from './api'

export interface FeatureConfig {
  ai: boolean
  commute: boolean
  demo?: boolean
}

const Ctx = createContext<FeatureConfig>({ ai: false, commute: false })

export function ConfigProvider({ children }: { children: ReactNode }) {
  const [cfg, setCfg] = useState<FeatureConfig>({ ai: false, commute: false })
  useEffect(() => {
    api<FeatureConfig>('/api/config').then(setCfg).catch(() => undefined)
  }, [])
  return <Ctx.Provider value={cfg}>{children}</Ctx.Provider>
}

export function useConfig() {
  return useContext(Ctx)
}
