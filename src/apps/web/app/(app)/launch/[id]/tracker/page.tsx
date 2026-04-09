"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";

import AgentStream from "@/components/agents/AgentStream";
import AgentPipeline from "@/components/agents/AgentPipeline";
import HITLCheckpoint from "@/components/hitl/HITLCheckpoint";
import { getLaunch, getPendingHITL, rememberLaunchId, toLaunchSummary } from "@/lib/api";
import { useLaunchStore } from "@/store/launchStore";

export default function LaunchTrackerPage() {
	const params = useParams<{ id: string }>();
	const launchId = params.id;

	const { agents, hitl, isStreaming, launch, setAgents, setHITL, setLaunch } = useLaunchStore();
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);

	const hydrate = useCallback(async () => {
		if (!launchId) {
			return;
		}
		setLoading(true);
		setError(null);
		try {
			const detail = await getLaunch(launchId);
			setAgents(detail.pipeline);
			setLaunch(toLaunchSummary(launchId, detail));
			rememberLaunchId(launchId);

			if (detail.hitl_pending) {
				const pending = await getPendingHITL(launchId);
				setHITL(pending);
			} else {
				setHITL(null);
			}
		} catch (loadError) {
			setError(loadError instanceof Error ? loadError.message : "Failed to load launch");
		} finally {
			setLoading(false);
		}
	}, [launchId, setAgents, setHITL, setLaunch]);

	useEffect(() => {
		void hydrate();
	}, [hydrate]);

	const title = useMemo(() => launch?.product_name ?? "Launch Tracker", [launch?.product_name]);

	return (
		<main style={{ display: "grid", gap: "1rem" }}>
			{launchId ? <AgentStream launchId={launchId} onReload={() => void hydrate()} /> : null}
			<section className="panel">
				<h1 style={{ margin: 0 }}>{title}</h1>
				<p style={{ margin: "0.4rem 0 0", color: "var(--muted)" }}>Launch ID: {launchId}</p>
				<p style={{ margin: "0.35rem 0 0", color: "var(--muted)" }}>
					Stream status: {isStreaming ? "connected" : "reconnecting"}
				</p>
			</section>

			{loading ? <p>Loading launch data...</p> : null}
			{error ? <p style={{ color: "var(--danger)" }}>{error}</p> : null}
			<AgentPipeline agents={agents} />

			{hitl ? <HITLCheckpoint hitl={hitl} onResolved={() => setHITL(null)} /> : null}
		</main>
	);
}
