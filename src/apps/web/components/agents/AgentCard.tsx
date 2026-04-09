"use client";

import type { AgentRun } from "@/packages/types";

const AGENT_LABELS: Record<string, string> = {
	market_intelligence: "Market Intelligence",
	audience_insight: "Audience Insight",
	launch_strategy: "Launch Strategy",
	content_generation: "Content Generation",
};

function statusClassName(status: string): string {
	if (status === "running") return "status-pill status-running";
	if (status === "completed") return "status-pill status-completed";
	if (status === "failed") return "status-pill status-failed";
	return "status-pill status-pending";
}

export default function AgentCard({ run }: { run: AgentRun }) {
	const preview = run.output ? JSON.stringify(run.output, null, 2).slice(0, 220) : "No output yet";

	return (
		<article className="panel" style={{ minHeight: "10rem" }} title={preview}>
			<header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
				<h3 style={{ margin: 0, fontSize: "1rem" }}>{AGENT_LABELS[run.agent_id] ?? run.agent_id}</h3>
				<span className={statusClassName(run.status)}>{run.status}</span>
			</header>

			<div style={{ marginTop: "0.7rem", color: "var(--muted)", fontSize: "0.92rem" }}>
				<div style={{ display: "flex", justifyContent: "space-between" }}>
					<span>Tokens</span>
					<strong>{run.tokens_used ?? 0}</strong>
				</div>
				{run.status === "running" ? <p style={{ margin: "0.6rem 0 0" }}>Analyzing...</p> : null}
				{run.error ? <p style={{ margin: "0.6rem 0 0", color: "var(--danger)" }}>{run.error}</p> : null}
			</div>
		</article>
	);
}
