import { Loader2, Play, RotateCcw, Eraser } from 'lucide-react'
const EXAMPLE = 'Use the add tool to calculate 125 + 275.'
interface Props { value: string; onChange: (v: string) => void; onRun: () => void; onClear: () => void; running: boolean; canClear: boolean; offline: boolean }
export default function TaskPanel({ value, onChange, onRun, onClear, running, canClear, offline }: Props) {
  return (
    <div className="panel p-4">
      <label htmlFor="task" className="sr-only">Task</label>
      <textarea id="task" rows={3} value={value} disabled={running} onChange={e => onChange(e.target.value)}
        onKeyDown={e => { if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') onRun() }}
        placeholder="Ask TRACE to perform a task using its available tools..."
        className="w-full resize-y rounded-lg border border-white/[0.08] bg-ink-950/60 px-3.5 py-3 text-sm leading-relaxed text-slate-100 placeholder:text-slate-500 transition-colors focus:border-indigo2/60 focus:outline-none disabled:opacity-60" />
      <div className="mt-3 flex flex-wrap items-center gap-2">
        <button onClick={onRun} disabled={running || !value.trim()}
          className="inline-flex items-center gap-2 rounded-lg bg-indigo-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:bg-indigo-500/40 disabled:text-white/60">
          {running ? <Loader2 size={15} className="animate-spin" /> : <Play size={15} />}{running ? 'Running agent…' : 'Run Agent'}
        </button>
        <button onClick={() => onChange(EXAMPLE)} disabled={running} className="inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm text-slate-400 transition hover:bg-white/5 hover:text-white disabled:opacity-50"><RotateCcw size={14} />Use example task</button>
        {canClear && <button onClick={onClear} disabled={running} className="inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm text-slate-400 transition hover:bg-white/5 hover:text-white disabled:opacity-50"><Eraser size={14} />Clear result</button>}
        <span className="ml-auto hidden text-xs text-slate-500 sm:block">{offline ? 'Backend is unreachable. The request will likely fail.' : 'Ctrl/⌘ + Enter to run'}</span>
      </div>
    </div>
  )
}
