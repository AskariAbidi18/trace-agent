import { CheckCircle2, XCircle } from 'lucide-react'
import type { RunResponse } from '../types'
export default function Summary({ r }: { r: RunResponse }) {
  const m = [
    ['Execution time', `${Math.round(r.execution_time_ms).toLocaleString()} ms`],
    ['Attempts', String(r.attempts)],
    ['Trace events', String(r.trace.length)],
    ['Failure reports', String(r.failure_reports.length)],
  ]
  return (
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
      <div className={`panel col-span-2 flex items-center gap-3 p-4 lg:col-span-1 ${r.success ? 'border-emerald-400/25' : 'border-rose-400/30'}`}>
        {r.success ? <CheckCircle2 className="text-emerald-400" size={20} /> : <XCircle className="text-rose-400" size={20} />}
        <div><div className="text-xs text-slate-400">Status</div><div className="text-base font-semibold text-white">{r.success ? 'Successful' : 'Failed'}</div></div>
      </div>
      {m.map(([k, v]) => <div key={k} className="panel p-4"><div className="text-xs text-slate-400">{k}</div><div className="mt-0.5 font-mono text-lg text-white">{v}</div></div>)}
    </div>
  )
}
