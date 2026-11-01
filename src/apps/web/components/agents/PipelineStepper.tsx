"use client";

import { AGENT_LABEL } from "@/lib/format";
import type { AgentId, AgentRun } from "@/packages/types";

const ORDER: AgentId[] = ["market_intelligence", "audience_insight", "launch_strategy", "content_generation"];

const ICON: Record<string, string> = { pending: "", running: "…", completed: "✓", failed: "!", skipped: "–" };

function duration(run?: AgentRun): string | null {
	if (!run?.started_at || !run.completed_at) {
		return null;
	}
	const seconds = (new Date(run.completed_at).getTime() - new Date(run.started_at).getTime()) / 1000;
	return Number.isFinite(seconds) && seconds >= 0 ? `${seconds < 10 ? seconds.toFixed(1) : Math.round(seconds)}s` : null;
}

export default function PipelineStepper({ agents, reviewAgent }: { agents: AgentRun[]; reviewAgent?: string | null }) {
	const byId = new Map(agents.map((agent) => [agent.agent_id, agent]));

	return (
		<section aria-label="Agent pipeline" style={{ display: "grid", gap: "0.7rem" }}>
			<h2 style={{ margin: 0 }}>Pipeline</h2>
			<ol className="stepper" style={{ listStyle: "none", margin: 0, padding: 0 }}>
				{ORDER.map((agentId, index) => {
					const run = byId.get(agentId);
					const status = run?.status ?? "pending";
					const waiting = reviewAgent === agentId;
					const took = duration(run);
					return (
						<li className="step" data-status={status} key={agentId}>
							<div className="step-head">
								<span aria-hidden="true" className="step-icon">{ICON[status] || index + 1}</span>
								<span>{AGENT_LABEL[agentId]}</span>
							</div>
							<span className="step-meta">
								{waiting
									? "Waiting for your review"
									: status === "running"
										? "Working…"
										: status === "completed"
											? `Done${took ? ` in ${took}` : ""}${run?.tokens_used ? ` · ${run.tokens_used.toLocaleString()} tokens` : ""}`
											: status === "failed"
												? "Failed"
												: "Not started"}
							</span>
							{run?.error ? <span className="field-error">{run.error}</span> : null}
						</li>
					);
				})}
			</ol>
		</section>
	);
}
