"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";

import AgentStream from "@/components/agents/AgentStream";
import PipelineStepper from "@/components/agents/PipelineStepper";
import HITLCheckpoint from "@/components/hitl/HITLCheckpoint";
import {
	downloadLaunchBrief,
	getLaunch,
	getPendingHITL,
	rememberLaunchId,
	retryAgent,
	toLaunchSummary,
} from "@/lib/api";
import { useLaunchStore } from "@/store/launchStore";

const STATUS_COPY: Record<string, { label: string; detail: string }> = {
	pending: { label: "Queued", detail: "Waiting for a worker to pick this launch up." },
	running: { label: "Running", detail: "Agents are working. This page updates automatically." },
	hitl_pending: { label: "Needs your review", detail: "The pipeline is paused until you approve, edit or reject below." },
	completed: { label: "Completed", detail: "Your launch brief is ready." },
	failed: { label: "Failed", detail: "An agent could not finish. Retry it below." },
	rejected: { label: "Rejected", detail: "You rejected this launch at a review checkpoint; the pipeline stopped." },
};

const POLL_MS = 5000;

export default function LaunchTrackerPage() {
	const params = useParams<{ id: string }>();
	const launchId = params.id;

	const { agents, hitl, isStreaming, launch, reset, setAgents, setHITL, setLaunch } = useLaunchStore();
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [exportReady, setExportReady] = useState(false);
	const [cost, setCost] = useState(0);
	const [notice, setNotice] = useState<string | null>(null);

	const hydrate = useCallback(
		async (initial = false) => {
			if (!launchId) {
				return;
			}
			try {
				const detail = await getLaunch(launchId);
				setAgents(detail.pipeline);
				setLaunch(toLaunchSummary(launchId, detail));
				setExportReady(Boolean(detail.export_ready));
				setCost(detail.total_cost_usd ?? 0);
				rememberLaunchId(launchId);
				setError(null);

				if (detail.hitl_pending) {
					setHITL(await getPendingHITL(launchId));
				} else {
					setHITL(null);
				}
			} catch (loadError) {
				setError(loadError instanceof Error ? loadError.message : "Failed to load launch");
			} finally {
				if (initial) {
					setLoading(false);
				}
			}
		},
		[launchId, setAgents, setHITL, setLaunch],
	);

	// A different launch must never show the previous launch's state.
	useEffect(() => {
		reset();
		setLoading(true);
		setNotice(null);
		void hydrate(true);
	}, [launchId, reset, hydrate]);

	// Safety net for events missed while the stream was down.
	const status = launch?.status;
	useEffect(() => {
		if (status === "completed" || status === "failed" || status === "rejected") {
			return undefined;
		}
		const timer = setInterval(() => void hydrate(), POLL_MS);
		return () => clearInterval(timer);
	}, [status, hydrate]);

	const title = useMemo(() => launch?.product_name ?? "Launch Tracker", [launch?.product_name]);
	const copy = status ? STATUS_COPY[status] : undefined;
	const failedAgents = agents.filter((agent) => agent.status === "failed");

	async function onRetry(agentId: string): Promise<void> {
		setNotice(null);
		try {
			await retryAgent(launchId, agentId);
			await hydrate();
		} catch (retryError) {
			setNotice(retryError instanceof Error ? retryError.message : "Retry failed");
		}
	}

	async function onExport(): Promise<void> {
		setNotice(null);
		try {
			await downloadLaunchBrief(launchId, title);
		} catch (exportError) {
			setNotice(exportError instanceof Error ? exportError.message : "Export failed");
		}
	}

	return (
		<main style={{ display: "grid", gap: "1rem" }}>
			{launchId ? <AgentStream launchId={launchId} onReload={() => void hydrate()} /> : null}
			<section className="panel">
				<h1 style={{ margin: 0 }}>{title}</h1>
				<p style={{ margin: "0.4rem 0 0", color: "var(--muted)" }}>Launch ID: {launchId}</p>
				<p style={{ margin: "0.35rem 0 0", color: "var(--muted)" }}>
					Live updates: {isStreaming ? "connected" : "reconnecting"}
					{cost > 0 ? ` | Estimated cost: $${cost.toFixed(4)}` : ""}
				</p>
			</section>

			{copy ? (
				<section className="panel" data-testid="launch-status" data-status={status}>
					<strong>{copy.label}</strong>
					<p style={{ margin: "0.3rem 0 0", color: "var(--muted)" }}>{copy.detail}</p>
					{status === "completed" && exportReady ? (
						<button className="btn btn-primary" onClick={() => void onExport()} style={{ marginTop: "0.6rem" }} type="button">
							Download launch brief (.md)
						</button>
					) : null}
					{status === "failed"
						? failedAgents.map((agent) => (
								<div key={agent.agent_id} style={{ marginTop: "0.6rem" }}>
									<span style={{ color: "var(--danger)" }}>
										{agent.agent_id} failed{agent.error ? `: ${agent.error}` : ""}
									</span>{" "}
									<button className="btn btn-secondary" onClick={() => void onRetry(agent.agent_id)} type="button">
										Retry {agent.agent_id}
									</button>
								</div>
							))
						: null}
					{notice ? <p style={{ color: "var(--danger)", marginBottom: 0 }}>{notice}</p> : null}
				</section>
			) : null}

			{loading ? <p>Loading launch data...</p> : null}
			{error ? <p style={{ color: "var(--danger)" }}>{error}</p> : null}
			{hitl ? <HITLCheckpoint hitl={hitl} onResolved={() => void hydrate()} /> : null}
			<PipelineStepper agents={agents} reviewAgent={hitl?.agent_id ?? null} />
		</main>
	);
}
