import type { AgentId } from './agent';

export type HITLDecision = 'approve' | 'edit' | 'reject';

export type HITLCheckpoint =
  | 'brief_review'
  | 'persona_review'
  | 'strategy_review'
  | 'content_review';

export interface HITLState {
  launch_id: string;
  checkpoint: HITLCheckpoint;
  agent_id: AgentId;
  output_preview: Record<string, unknown>;
  decision?: HITLDecision;
  edits?: Record<string, unknown>;
  created_at: string;
  resolved_at?: string;
}
