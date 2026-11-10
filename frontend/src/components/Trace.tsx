import { useState } from 'react'
import { ChevronRight } from 'lucide-react'
import { AnimatePresence, motion } from 'framer-motion'
import type { TraceEvent } from '../types'
import { SeverityBadge, fmtTime, label, pretty } from './ui'

const bar: Record<string, string> = { INFO: 'bg-cyan2/60', WARNING: 'bg-amber-300/70', ERROR: 'bg-rose-400' }

export function TraceRow({ e }: { e: TraceEvent }) {
  const [open, setOpen] = useState(false)
  const hasDetails = e.details && Object.keys(e.details).length > 0
  return (
    <li className="relative">
      <span className={`absolute left-0 top-2 bottom-2 w-0.5 rounded-full ${bar[e.severity] ?? 'bg-slate-500'}`} />
      <button onClick={() => setOpen(o => !o)} aria-expanded={open} className="flex w-full items-center gap-3 rounded-lg py-2.5 pl-4 pr-2 text-left transition-colors hover:bg-white/[0.03]">
        <ChevronRight size={14} className={`shrink-0 text-slate-500 transition-transform ${open ? 'rotate-90' : ''}`} />
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
            <span className="text-sm font-medium text-slate-100">{label(e.event_type)}</span>
            <SeverityBadge s={e.severity} />
          </div>
          <div className="mt-0.5 text-xs text-slate-500">Stage: {label(e.stage)}</div>
        </div>
        <time className="shrink-0 font-mono text-xs text-slate-500">{fmtTime(e.timestamp)}</time>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.18 }} className="overflow-hidden">
            <div className="mb-2 ml-9 mr-2 space-y-2 rounded-lg bg-ink-950/60 p-3 text-xs">
              <div className="grid gap-1 font-mono text-slate-400">
                <div>event_id: <span className="break-all text-slate-300">{e.event_id}</span></div>
                {e.execution_id && <div>execution_id: <span className="break-all text-slate-300">{e.execution_id}</span></div>}
              </div>
              {hasDetails ? <pre className="max-h-64 overflow-auto whitespace-pre-wrap break-words font-mono text-slate-300">{pretty(e.details)}</pre> : <div className="text-slate-500">No additional details for this event.</div>}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </li>
  )
}
export default function Trace({ events }: { events: TraceEvent[] }) {
  if (!events.length) return <div className="panel p-4 text-sm text-slate-500">The backend returned no trace events.</div>
  return <ul className="panel divide-y divide-white/[0.05] p-1.5">{events.map(e => <TraceRow key={e.event_id} e={e} />)}</ul>
}
