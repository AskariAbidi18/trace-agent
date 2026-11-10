import { Activity, GitBranch, History, LayoutGrid, Cpu } from 'lucide-react'
import type { Health } from '../types'
import type { ConnState } from '../App'

const nav = [
  { href: '#overview', label: 'Overview', icon: LayoutGrid },
  { href: '#execution', label: 'Agent Execution', icon: GitBranch },
  { href: '#history', label: 'Execution History', icon: History },
  { href: '#status', label: 'System Status', icon: Activity },
]
export const dot = (c: ConnState) => c === 'online' ? 'bg-emerald-400' : c === 'checking' ? 'bg-amber-300 animate-pulse' : 'bg-rose-400'
export const connText = (c: ConnState) => c === 'online' ? 'Backend connected' : c === 'checking' ? 'Checking backend' : 'Backend unreachable'

export default function Sidebar({ conn, health }: { conn: ConnState; health: Health | null }) {
  return (
    <aside className="border-b border-white/[0.07] bg-ink-950/60 md:fixed md:inset-y-0 md:left-0 md:w-56 md:border-b-0 md:border-r">
      <div className="flex h-full flex-col px-4 py-4 md:py-6">
        <div className="flex items-center gap-2.5 px-1">
          <div className="grid h-7 w-7 place-items-center rounded-md bg-gradient-to-br from-indigo-500 to-cyan-400 text-[13px] font-semibold text-ink-950">T</div>
          <span className="text-[15px] font-semibold tracking-tight text-white">TRACE</span>
        </div>
        <nav className="mt-3 flex gap-1 overflow-x-auto md:mt-8 md:flex-col" aria-label="Sections">
          {nav.map(n => (
            <a key={n.href} href={n.href} className="flex shrink-0 items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm text-slate-400 transition-colors hover:bg-white/5 hover:text-white">
              <n.icon size={16} strokeWidth={1.75} />{n.label}
            </a>
          ))}
        </nav>
        <div className="mt-auto hidden space-y-2.5 border-t border-white/[0.07] pt-4 text-xs text-slate-400 md:block">
          <div className="flex items-center gap-2"><Cpu size={14} className="text-indigo2" /><span>{health ? health.model : 'Qwen 2.5 3B'}</span></div>
          <div className="flex items-center gap-2"><span className={`h-2 w-2 rounded-full ${dot(conn)}`} />{connText(conn)}</div>
          <div className="font-mono text-slate-500">v0.1.0</div>
        </div>
      </div>
    </aside>
  )
}
