export type AgentStatus = 'pending' | 'running' | 'completed' | 'failed' | 'skipped';

export type AgentId =
  | 'orchestrator'
  | 'market_intelligence'
  | 'audience_insight'
  | 'launch_strategy'
  | 'content_generation'
  | 'analytics_feedback';

export interface AgentRun {
  agent_id: AgentId;
  launch_id: string;
  status: AgentStatus;
  output?: Record<string, unknown>;
  tokens_used?: number;
  started_at?: string;
  completed_at?: string;
  error?: string;
}
