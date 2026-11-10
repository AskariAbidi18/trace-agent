import type { Health, RunResponse } from './types'
export const API_BASE = ((import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://127.0.0.1:8000').replace(/\/$/, '')

export class ApiError extends Error { constructor(msg: string, public kind: 'network' | 'http' | 'invalid' | 'timeout') { super(msg) } }

async function request(path: string, init: RequestInit, timeoutMs: number): Promise<unknown> {
  const ctrl = new AbortController()
  const timer = setTimeout(() => ctrl.abort(), timeoutMs)
  try {
    const res = await fetch(API_BASE + path, { ...init, signal: ctrl.signal })
    if (!res.ok) {
      let detail = ''
      try { const b = await res.json(); detail = typeof b?.detail === 'string' ? b.detail : JSON.stringify(b?.detail ?? b) } catch { /* ignore */ }
      throw new ApiError(`Backend returned HTTP ${res.status}${detail ? `: ${detail}` : ''}`, 'http')
    }
    try { return await res.json() } catch { throw new ApiError('Backend returned a response that is not valid JSON.', 'invalid') }
  } catch (e) {
    if (e instanceof ApiError) throw e
    if ((e as Error).name === 'AbortError') throw new ApiError(`No response from the backend after ${Math.round(timeoutMs / 1000)}s.`, 'timeout')
    throw new ApiError(`Cannot reach the backend at ${API_BASE}. Check that it is running and that CORS allows this origin.`, 'network')
  } finally { clearTimeout(timer) }
}

const isObj = (v: unknown): v is Record<string, unknown> => typeof v === 'object' && v !== null

export async function getHealth(): Promise<Health> {
  const d = await request('/health', {}, 5000)
  if (!isObj(d) || typeof d.status !== 'string') throw new ApiError('Unexpected /health response shape.', 'invalid')
  return { status: d.status, service: String(d.service ?? 'TRACE API'), model: String(d.model ?? 'unknown') }
}

export async function runAgent(task: string): Promise<RunResponse> {
  const d = await request('/api/run', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ task }) }, 180000)
  if (!isObj(d) || typeof d.success !== 'boolean' || !Array.isArray(d.trace) || !Array.isArray(d.failure_reports))
    throw new ApiError('Unexpected /api/run response shape (missing success, trace or failure_reports).', 'invalid')
  return {
    success: d.success, task: String(d.task ?? task), answer: d.answer == null ? '' : String(d.answer),
    attempts: Number(d.attempts ?? 0), execution_time_ms: Number(d.execution_time_ms ?? 0),
    trace: d.trace as RunResponse['trace'], failure_reports: d.failure_reports as RunResponse['failure_reports'],
  }
}
