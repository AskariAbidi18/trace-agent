import type { ReactNode } from 'react'
export const Section = ({ id, title, aside, children }: { id?: string; title: string; aside?: ReactNode; children: ReactNode }) => (
  <section id={id} className="scroll-mt-6">
    <div className="mb-3 flex items-center justify-between gap-3">
      <h2 className="text-sm font-medium text-slate-100">{title}</h2>{aside}
    </div>
    {children}
  </section>
)
export const sevStyle: Record<string, string> = {
  INFO: 'text-cyan2 bg-cyan2/10 border-cyan2/20',
  WARNING: 'text-amber-300 bg-amber-300/10 border-amber-300/20',
  ERROR: 'text-rose-300 bg-rose-400/10 border-rose-400/25',
}
export const SeverityBadge = ({ s }: { s: string }) => (
  <span className={`rounded-md border px-1.5 py-0.5 font-mono text-[11px] ${sevStyle[s] ?? 'text-slate-300 bg-white/5 border-white/10'}`}>{s}</span>
)
export const fmtTime = (iso: string) => { const d = new Date(iso); return isNaN(+d) ? iso : d.toLocaleTimeString([], { hour12: false }) + '.' + String(d.getMilliseconds()).padStart(3, '0') }
export const pretty = (v: unknown) => typeof v === 'string' ? v : JSON.stringify(v, null, 2)
export const label = (s: string) => s.replace(/_/g, ' ').replace(/^./, c => c.toUpperCase())
