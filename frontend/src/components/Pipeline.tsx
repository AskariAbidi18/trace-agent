import { Check, X, Minus } from 'lucide-react'
import { motion } from 'framer-motion'
import type { RunResponse } from '../types'

const STAGES = [
  { name: 'Task Initialization', keys: ['init'] }, { name: 'Planning', keys: ['plan'] },
  { name: 'Tool Selection', keys: ['tool_select', 'selection'] }, { name: 'Argument Generation', keys: ['argument', 'arg_'] },
  { name: 'Tool Execution', keys: ['tool_exec', 'execution'] }, { name: 'Output Interpretation', keys: ['interpret', 'output'] },
  { name: 'Completion', keys: ['complet', 'final'] },
]
const norm = (s: string) => s.toLowerCase().replace(/[\s-]+/g, '_')
const matches = (stage: string, keys: string[]) => keys.some(k => norm(stage).includes(k))

export default function Pipeline({ r }: { r: RunResponse }) {
  const items = STAGES.map(s => {
    const evs = r.trace.filter(e => matches(e.stage, s.keys))
    const failed = evs.some(e => e.severity === 'ERROR') || r.failure_reports.some(f => matches(f.stage, s.keys))
    const seen = evs.length > 0 || r.failure_reports.some(f => matches(f.stage, s.keys))
    return { ...s, count: evs.length, state: failed ? 'failed' : seen ? 'done' : 'skipped' } as const
  })
  const known = new Set(items.flatMap(i => i.keys))
  const other = [...new Set(r.trace.map(e => e.stage))].filter(st => !matches(st, [...known]))
  const style = { done: 'border-emerald-400/40 bg-emerald-400/10 text-emerald-300', failed: 'border-rose-400/50 bg-rose-400/10 text-rose-300', skipped: 'border-white/10 bg-transparent text-slate-600' }
  const text = { done: 'Completed', failed: 'Failed', skipped: 'Not executed' }
  return (
    <div className="panel p-4">
      <ol className="flex flex-col gap-1 md:grid md:grid-cols-7 md:gap-2">
        {items.map((s, i) => (
          <motion.li key={s.name} initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}
            className="relative flex items-center gap-3 md:flex-col md:items-start md:gap-2">
            <div className="flex items-center md:w-full">
              <span className={`grid h-7 w-7 shrink-0 place-items-center rounded-full border ${style[s.state]}`}>
                {s.state === 'done' ? <Check size={14} /> : s.state === 'failed' ? <X size={14} /> : <Minus size={14} />}
              </span>
              {i < items.length - 1 && <span className={`ml-2 hidden h-px flex-1 md:block ${s.state === 'skipped' ? 'bg-white/10' : s.state === 'failed' ? 'bg-rose-400/40' : 'bg-emerald-400/30'}`} />}
            </div>
            <div>
              <div className={`text-[13px] font-medium ${s.state === 'skipped' ? 'text-slate-500' : 'text-slate-100'}`}>{s.name}</div>
              <div className="text-xs text-slate-500">{text[s.state]}{s.count > 0 && ` · ${s.count} event${s.count > 1 ? 's' : ''}`}</div>
            </div>
          </motion.li>
        ))}
      </ol>
      {other.length > 0 && <p className="mt-3 border-t border-white/[0.06] pt-3 text-xs text-slate-500">Other stages in the trace: <span className="font-mono">{other.join(', ')}</span></p>}
    </div>
  )
}
