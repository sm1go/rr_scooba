import {
  createContext, useCallback, useContext, useEffect, useState,
  type ReactNode,
} from 'react'
import { api, getToken, setToken, setUnauthorizedHandler } from './api'
import type { User } from '../types'

interface AuthCtx {
  user: User | null
  ready: boolean
  login: (login: string, password: string) => Promise<User>
  register: (body: Record<string, unknown>) => Promise<User>
  logout: () => Promise<void>
  refresh: () => Promise<void>
}

const Ctx = createContext<AuthCtx | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [ready, setReady] = useState(false)

  const refresh = useCallback(async () => {
    if (!getToken()) { setUser(null); setReady(true); return }
    try {
      setUser(await api<User>('/api/me'))
    } catch {
      setUser(null)
    } finally {
      setReady(true)
    }
  }, [])

  useEffect(() => {
    setUnauthorizedHandler(() => setUser(null))
    void refresh()
  }, [refresh])

  const login = useCallback(async (login: string, password: string) => {
    const r = await api<{ token: string; user: User }>('/api/auth/login', {
      body: { login, password },
    })
    setToken(r.token)
    setUser(r.user)
    return r.user
  }, [])

  const register = useCallback(async (body: Record<string, unknown>) => {
    const r = await api<{ token: string; user: User }>('/api/auth/register', {
      body,
    })
    setToken(r.token)
    setUser(r.user)
    return r.user
  }, [])

  const logout = useCallback(async () => {
    try { await api('/api/auth/logout', { method: 'POST' }) } catch { /* ok */ }
    setToken(null)
    setUser(null)
  }, [])

  return (
    <Ctx.Provider value={{ user, ready, login, register, logout, refresh }}>
      {children}
    </Ctx.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useAuth outside provider')
  return ctx
}
