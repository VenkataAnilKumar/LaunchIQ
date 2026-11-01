"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { PageSkeleton } from "@/components/ui/Skeleton";
import { type AnalyticsResult, analyzeLaunch } from "@/lib/api";
import { useLaunch } from "@/lib/useLaunch";

const EXAMPLE = JSON.stringify(
	{ sessions: 1200, conversions: 48, engagement_rate: 0.52, ad_ctr: { a: 0.031, b: 0.012 } },
	null,
	2,
);

export default function LaunchAnalyticsPage() {
	const { id } = useParams<{ id: string }>();
	const launch = useLaunch(id);
	const [raw, setRaw] = useState(EXAMPLE);
	const [result, setResult] = useState<AnalyticsResult | null>(null);
	const [error, setError] = useState<string | null>(null);
	const [busy, setBusy] = useState(false);

	useEffect(() => {
		const saved = launch.data?.brief.analytics as AnalyticsResult | undefined;
		if (saved) {
			setResult(saved);
		}
	}, [launch.data]);

	async function submit(): Promise<void> {
		setError(null);
		let metrics: Record<string, unknown>;
		try {
			metrics = JSON.parse(raw) as Record<string, unknown>;
		} catch {
			setError("Metrics must be valid JSON.");
			return;
		}
		setBusy(true);
		try {
			setResult(await analyzeLaunch(id, metrics));
		} catch (submitError) {
			setError(submitError instanceof Error ? submitError.message : "Analysis failed");
		} finally {
			setBusy(false);
		}
	}

	if (launch.isLoading) {
		return <PageSkeleton />;
	}
	if (launch.data && launch.data.status !== "completed") {
		return (
			<section className="panel">
				<h2 style={{ marginTop: 0 }}>Analytics</h2>
				<p style={{ color: "var(--muted)", marginBottom: 0 }}>Available once the launch brief is completed.</p>
			</section>
		);
	}

	return (
		<main style={{ display: "grid", gap: "1rem" }}>
			<section className="panel">
				<h2 style={{ marginTop: 0 }}>Post-launch analytics</h2>
				<p style={{ color: "var(--muted)" }}>
					Paste the results you measured after launching. Recommendations are based only on these numbers; nothing is invented.
				</p>
				<label htmlFor="metrics-json">Measured metrics (JSON)</label>
				<textarea
					id="metrics-json"
					onChange={(event) => setRaw(event.target.value)}
					rows={8}
					style={{ fontFamily: "ui-monospace, Menlo, monospace", marginTop: "0.35rem" }}
					value={raw}
				/>
				{error ? <p className="field-error" role="alert">{error}</p> : null}
				<div style={{ marginTop: "0.7rem" }}>
					<button className="btn btn-primary" disabled={busy} onClick={() => void submit()} type="button">
						{busy ? "Analyzing..." : "Analyze results"}
					</button>
				</div>
			</section>

			{result ? (
				<section className="panel" data-testid="analytics-result" style={{ display: "grid", gap: "0.9rem" }}>
					<div>
						<h3 style={{ margin: 0 }}>Engagement score: {(result.engagement_score * 100).toFixed(0)}%</h3>
						<div aria-hidden="true" style={{ height: "0.5rem", background: "#e9efe6", borderRadius: "999px", marginTop: "0.5rem" }}>
							<div style={{ width: `${Math.round(result.engagement_score * 100)}%`, height: "100%", background: "var(--success)", borderRadius: "999px" }} />
						</div>
					</div>
					<p style={{ margin: 0 }}><strong>Next action:</strong> {result.predicted_next_action}</p>
					<div className="stat-grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))" }}>
						<div className="stat"><span>Top performing</span><ul style={{ margin: "0.3rem 0 0", paddingLeft: "1.1rem" }}>{result.top_performing_content.map((c) => <li key={c}>{c}</li>)}</ul></div>
						<div className="stat"><span>Underperforming</span><ul style={{ margin: "0.3rem 0 0", paddingLeft: "1.1rem" }}>{result.underperforming_content.map((c) => <li key={c}>{c}</li>)}</ul></div>
					</div>
					<div style={{ display: "grid", gap: "0.6rem" }}>
						{result.recommendations.map((rec) => (
							<div className="panel" key={`${rec.area}-${rec.action}`} style={{ display: "grid", gap: "0.25rem" }}>
								<div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
									<span className={`priority priority-${rec.priority}`}>{rec.priority}</span>
									<strong>{rec.area}</strong>
								</div>
								<span style={{ color: "var(--muted)" }}>{rec.insight}</span>
								<span>&rarr; {rec.action}</span>
							</div>
						))}
					</div>
				</section>
			) : null}
		</main>
	);
}
