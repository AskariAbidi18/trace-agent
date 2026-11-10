export type Severity = 'INFO' | 'WARNING' | 'ERROR'
export interface TraceEvent { event_id: string; execution_id?: string; event_type: string; stage: string; severity: Severity | string; timestamp: string; details?: Record<string, unknown> | null }
export interface FailureReport { failure_id: string; category: string; stage: string; message: string; evidence?: unknown; recovery_suggestion?: string; timestamp?: string; [k: string]: unknown }
export interface RunResponse { success: boolean; task: string; answer: string; attempts: number; execution_time_ms: number; trace: TraceEvent[]; failure_reports: FailureReport[] }
export interface Health { status: string; service: string; model: string }
