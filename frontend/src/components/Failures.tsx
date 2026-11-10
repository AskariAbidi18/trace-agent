import { useState } from 'react'
import { ChevronRight, ShieldCheck, Wrench } from 'lucide-react'
import { AnimatePresence, motion } from 'framer-motion'
import type { FailureReport } from '../types'
import { fmtTime, label, pretty } from './ui'

const UUID_KEYS = /event_?ids?$/i
function collectIds(v: unknown, out = new Set<string>()): Set<string> {
  if (Array.isArray(v)) v.forEach(x => collectIds(x, out))
  else if (v && typeof v === 'object') for (const [k, val] of Object.entries(v)) {
    if (UUID_KEYS.test(k)) (Array.isArray(val) ? val : [val]).forEach(x => typeof x === 'string' && out.add(x)); else collectIds(val, out)
  }
  return out
}
const field = (f: FailureReport, k: string) => { const v = f[k] ?? (f.evidence && typeof f.evidence === 'object' ? (f.evidence as Record<string, unknown>)[k] : undefined); return v == null ? null : pretty(v) }

function Row({ f }: { f: FailureReport }) {
  const [open, setOpen] = useState(false)
  const ids = collectIds(f.evidence)
  const method = field(f, 'diagnostic_method'), root = field(f, 'root_cause_status')
  return (
    <li>
      <button onClick={() => setOpen(o => !o)} aria-expanded={open} className="flex w-full items-start gap-3 p-4 text-left">
        <ChevronRight size={14} className={`mt-1 shrink-0 text-slate-500 transition-transform ${open ? 'rotate-90' : ''}`} />
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm font-medium text-rose-200">{label(f.category)}</span>
            <span className="rounded-md border border-white/10 px-1.5 py-0.5 text-[11px] text-slate-400">Stage: {label(f.stage)}</span>
            {f.timestamp && <time className="ml-auto font-mono text-xs text-slate-500">{fmtTime(f.timestamp)}</time>}
          </div>
          <p className="mt-1.5 text-sm text-slate-300">{f.message}</p>
        </div>
      </button>
      {f.recovery_suggestion && (
        <div className="mx-4 mb-4 ml-11 flex gap-2.5 rounded-lg border border-indigo2/20 bg-indigo-500/[0.07] p-3 text-sm text-slate-200">
          <Wrench size={15} className="mt-0.5 shrink-0 text-indigo2" /><div><div className="text-xs text-indigo2">Recovery suggestion</div>{f.recovery_suggestion}</div>
        </div>)}
      <AnimatePresence initial={false}>
        {open && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.18 }} className="overflow-hidden">
            <div className="mx-4 mb-4 ml-11 space-y-3 text-xs">
              <dl className="grid gap-x-6 gap-y-2 sm:grid-cols-2">
                <div><dt className="text-slate-500">Diagnostic method</dt><dd className="text-slate-200">{method ?? 'Not reported by backend'}</dd></div>
                <div><dt className="text-slate-500">Root cause status</dt><dd className="text-slate-200">{root ?? 'Not reported by backend'}</dd></div>
                <div className="sm:col-span-2"><dt className="text-slate-500">Failure ID</dt><dd className="break-all font-mono text-slate-300">{f.failure_id}</dd></div>
              </dl>
              <div><div className="mb-1 text-slate-500">Referenced event IDs</div>
                {ids.size ? <div className="flex flex-wrap gap-1.5">{[...ids].map(id => <code key={id} className="break-all rounded bg-ink-950/70 px-1.5 py-0.5 text-slate-300">{id}</code>)}</div> : <span className="text-slate-500">None found in evidence.</span>}</div>
              <div><div className="mb-1 text-slate-500">Supporting evidence</div>
                <pre className="max-h-64 overflow-auto whitespace-pre-wrap break-words rounded-lg bg-ink-950/60 p-3 font-mono text-slate-300">{f.evidence == null ? 'No evidence provided.' : pretty(f.evidence)}</pre></div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </li>
  )
}
export default function Failures({ reports }: { reports: FailureReport[] }) {
  if (!reports.length) return (
    <div className="panel flex items-center gap-2.5 px-4 py-3 text-sm text-slate-400"><ShieldCheck size={16} className="text-emerald-400" />No failures were reported for this execution.</div>)
  return <ul className="panel divide-y divide-white/[0.06] border-rose-400/20">{reports.map(f => <Row key={f.failure_id} f={f} />)}</ul>
}
