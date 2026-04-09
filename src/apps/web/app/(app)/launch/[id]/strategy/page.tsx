"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import StrategyPhase from "@/components/launch/StrategyPhase";
import AgentPending from "@/components/ui/AgentPending";
import { getLaunch } from "@/lib/api";
import type { LaunchStrategy } from "@/packages/types";

export default function LaunchStrategyPage() {
	const params = useParams<{ id: string }>();
	const [strategy, setStrategy] = useState<LaunchStrategy | null>(null);

	useEffect(() => {
		void getLaunch(params.id).then((launch) => {
			setStrategy((launch.brief.strategy as LaunchStrategy | undefined) ?? null);
		});
	}, [params.id]);

	if (!strategy) {
		return <AgentPending agentName="Launch Strategy" />;
	}

	return (
		<section style={{ display: "grid", gap: "1rem" }}>
			<div className="panel">
				<h2 style={{ marginTop: 0 }}>Positioning</h2>
				<p>{strategy.positioning_statement}</p>
				<p style={{ marginBottom: 0, color: "var(--muted)" }}>
					Recommended launch date: {strategy.launch_date_recommendation}
				</p>
			</div>
			{strategy.phases.map((phase, index) => (
				<StrategyPhase index={index} key={`${phase.phase}-${index}`} phase={phase} />
			))}
			<div className="panel">
				<h3 style={{ marginTop: 0 }}>Risks</h3>
				<ul style={{ marginBottom: 0 }}>
					{strategy.risks.map((risk) => (
						<li key={risk}>{risk}</li>
					))}
				</ul>
			</div>
		</section>
	);
}
