import type { RunResponse } from '../types'
export default function Result({ r }: { r: RunResponse }) {
  return (
    <div className="grid gap-3 lg:grid-cols-3">
      <div className={`panel p-5 lg:col-span-2 ${r.success ? 'border-cyan2/20' : 'border-rose-400/25'}`}>
        <div className="text-xs text-slate-400">Answer</div>
        <p className="mt-2 whitespace-pre-wrap text-lg leading-relaxed text-white">{r.answer || <span className="text-slate-500">The agent did not produce an answer.</span>}</p>
      </div>
      <div className="space-y-3">
        <div className="panel p-4"><div className="text-xs text-slate-400">Submitted task</div><p className="mt-1 whitespace-pre-wrap text-sm text-slate-300">{r.task}</p></div>
        <div className="panel p-4 font-mono text-xs text-slate-400">
          {[['success', String(r.success)], ['attempts', r.attempts], ['execution_time_ms', r.execution_time_ms.toFixed(2)], ['trace', r.trace.length], ['failure_reports', r.failure_reports.length]].map(([k, v]) =>
            <div key={String(k)} className="flex justify-between py-0.5"><span>{k}</span><span className="text-slate-200">{v}</span></div>)}
        </div>
      </div>
    </div>
  )
}
