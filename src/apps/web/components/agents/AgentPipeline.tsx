"use client";

import type { AgentId, AgentRun } from "@/packages/types";

import AgentCard from "./AgentCard";

const ORDER: AgentId[] = [
	"market_intelligence",
	"audience_insight",
	"launch_strategy",
	"content_generation",
];

export default function AgentPipeline({ agents }: { agents: AgentRun[] }) {
	const map = new Map(agents.map((agent) => [agent.agent_id, agent]));
	const normalized = ORDER.map((agentId) => {
		const existing = map.get(agentId);
		return (
			existing ?? {
				agent_id: agentId,
				launch_id: "",
				status: "pending" as const,
			}
		);
	});

	return (
		<section style={{ display: "grid", gap: "0.9rem" }}>
			<h2 style={{ margin: 0 }}>Agent Pipeline</h2>
			<div style={{ display: "grid", gap: "0.8rem", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))" }}>
				{normalized.map((agent) => (
					<AgentCard key={agent.agent_id} run={agent} />
				))}
			</div>
		</section>
	);
}
