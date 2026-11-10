import { useCallback, useEffect, useState } from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'
import { API_BASE, ApiError, getHealth, runAgent } from './api'
import type { Health, RunResponse } from './types'
import Sidebar, { connText, dot } from './components/Sidebar'
import TaskPanel from './components/TaskPanel'
import Summary from './components/Summary'
import Pipeline from './components/Pipeline'
import Trace from './components/Trace'
import Failures from './components/Failures'
import Result from './components/Result'
import { Section } from './components/ui'

export type ConnState = 'checking' | 'online' | 'offline'

export default function App() {
  const [conn, setConn] = useState<ConnState>('checking')
  const [health, setHealth] = useState<Health | null>(null)
  const [connError, setConnError] = useState<string | null>(null)
  const [task, setTask] = useState('')
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState<RunResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const check = useCallback(async () => {
    setConn('checking'); setConnError(null)
    try { const h = await getHealth(); setHealth(h); setConn(h.status === 'healthy' ? 'online' : 'offline'); if (h.status !== 'healthy') setConnError(`Backend reports status "${h.status}".`) }
    catch (e) { setHealth(null); setConn('offline'); setConnError((e as Error).message) }
  }, [])
  useEffect(() => { check() }, [check])

  const run = async () => {
    if (running || !task.trim()) return
    setRunning(true); setError(null); setResult(null)
    try { setResult(await runAgent(task.trim())); if (conn !== 'online') check() }
    catch (e) { setError(e instanceof ApiError ? e.message : 'Unexpected error while running the agent.'); if (e instanceof ApiError && (e.kind === 'network' || e.kind === 'timeout')) setConn('offline') }
    finally { setRunning(false) }
  }
  const clear = () => { setResult(null); setError(null) }

  return (
    <div className="min-h-screen">
      <Sidebar conn={conn} health={health} />
      <main className="mx-auto max-w-5xl space-y-8 px-4 py-6 md:ml-56 md:max-w-none md:px-8 md:py-8 xl:px-12">
        <header id="overview" className="flex flex-wrap items-start justify-between gap-4 scroll-mt-6">
          <div>
            <h1 className="text-xl font-semibold tracking-tight text-white">TRACE Dashboard</h1>
            <p className="mt-1 text-sm text-slate-400">Monitor, execute and diagnose tool-augmented agent workflows.</p>
          </div>
          <button onClick={check} disabled={conn === 'checking'} title="Refresh backend connection"
            className="inline-flex items-center gap-2 rounded-lg border border-white/10 px-3 py-1.5 text-sm text-slate-300 transition hover:bg-white/5 disabled:opacity-60">
            <span className={`h-2 w-2 rounded-full ${dot(conn)}`} />{connText(conn)}
            <RefreshCw size={13} className={conn === 'checking' ? 'animate-spin' : ''} />
          </button>
        </header>

        {conn === 'offline' && connError && (
          <div role="alert" className="flex gap-2.5 rounded-lg border border-amber-300/25 bg-amber-300/[0.06] px-4 py-3 text-sm text-amber-100"><AlertTriangle size={16} className="mt-0.5 shrink-0" />{connError}</div>)}

        <div id="execution" className="scroll-mt-6 space-y-4">
          <TaskPanel value={task} onChange={setTask} onRun={run} onClear={clear} running={running} canClear={!!result || !!error} offline={conn === 'offline'} />
          {running && <div className="panel flex items-center gap-3 px-4 py-3 text-sm text-slate-300" role="status"><span className="h-1.5 w-24 overflow-hidden rounded bg-white/10"><span className="block h-full w-1/3 animate-[slide_1.2s_ease-in-out_infinite] rounded bg-cyan2" /></span>Waiting for the backend to finish the run. Local models can take several seconds.</div>}
          {error && <div role="alert" className="flex gap-2.5 rounded-lg border border-rose-400/30 bg-rose-400/[0.07] px-4 py-3 text-sm text-rose-100"><AlertTriangle size={16} className="mt-0.5 shrink-0" />{error}</div>}
        </div>

        {result && (
          <>
            <Section title="Result"><Result r={result} /></Section>
            <Section title="Execution summary"><Summary r={result} /></Section>
            <Section title="Execution pipeline"><Pipeline r={result} /></Section>
            <Section title="Failure diagnosis" aside={<span className="text-xs text-slate-500">{result.failure_reports.length} report{result.failure_reports.length === 1 ? '' : 's'}</span>}><Failures reports={result.failure_reports} /></Section>
            <div id="history" className="scroll-mt-6"><Section title="Execution trace" aside={<span className="text-xs text-slate-500">Last run · {result.trace.length} events</span>}><Trace events={result.trace} /></Section></div>
          </>
        )}
        {!result && !running && !error && <div id="history" className="panel px-4 py-8 text-center text-sm text-slate-500">Run a task to see the result, pipeline, trace and any failure diagnosis here. The backend does not store history, so only the latest run is shown.</div>}

        <Section id="status" title="System status">
          <div className="panel grid gap-x-8 gap-y-2 p-4 text-sm sm:grid-cols-2">
            {[['API base URL', API_BASE], ['Connection', connText(conn)], ['Service', health?.service ?? '—'], ['Model', health?.model ?? '—']].map(([k, v]) =>
              <div key={k} className="flex justify-between gap-4"><span className="text-slate-500">{k}</span><span className="break-all font-mono text-slate-200">{v}</span></div>)}
          </div>
        </Section>
      </main>
    </div>
  )
}
