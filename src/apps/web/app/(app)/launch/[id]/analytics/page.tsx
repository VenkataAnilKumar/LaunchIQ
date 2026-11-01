"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { type AnalyticsResult, analyzeLaunch, getLaunch } from "@/lib/api";

const EXAMPLE = JSON.stringify(
	{ sessions: 1200, conversions: 48, engagement_rate: 0.52, ad_ctr: { a: 0.031, b: 0.012 } },
	null,
	2,
);

export default function LaunchAnalyticsPage() {
	const params = useParams<{ id: string }>();
	const [raw, setRaw] = useState(EXAMPLE);
	const [result, setResult] = useState<AnalyticsResult | null>(null);
	const [status, setStatus] = useState<string | null>(null);
	const [error, setError] = useState<string | null>(null);
	const [busy, setBusy] = useState(false);

	useEffect(() => {
		getLaunch(params.id)
			.then((launch) => {
				setStatus(launch.status);
				setResult((launch.brief.analytics as AnalyticsResult | undefined) ?? null);
			})
			.catch((loadError: unknown) => setError(loadError instanceof Error ? loadError.message : "Failed to load"));
	}, [params.id]);

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
			setResult(await analyzeLaunch(params.id, metrics));
		} catch (submitError) {
			setError(submitError instanceof Error ? submitError.message : "Analysis failed");
		} finally {
			setBusy(false);
		}
	}

	if (status && status !== "completed") {
		return (
			<section className="panel">
				<h2 style={{ marginTop: 0 }}>Analytics</h2>
				<p style={{ color: "var(--muted)" }}>Available once the launch brief is completed.</p>
			</section>
		);
	}

	return (
		<main style={{ display: "grid", gap: "1rem" }}>
			<section className="panel">
				<h2 style={{ marginTop: 0 }}>Post-launch analytics</h2>
				<p style={{ color: "var(--muted)" }}>
					Paste the results you measured after launching. Recommendations are based only on these numbers.
				</p>
				<label htmlFor="metrics-json" style={{ display: "block", marginBottom: "0.4rem" }}>
					Measured metrics (JSON)
				</label>
				<textarea
					id="metrics-json"
					onChange={(event) => setRaw(event.target.value)}
					rows={8}
					style={{ width: "100%", fontFamily: "ui-monospace, Menlo, monospace" }}
					value={raw}
				/>
				{error ? <p style={{ color: "var(--danger)" }}>{error}</p> : null}
				<button className="btn btn-primary" disabled={busy} onClick={() => void submit()} type="button">
					{busy ? "Analyzing..." : "Analyze results"}
				</button>
			</section>

			{result ? (
				<section className="panel" data-testid="analytics-result">
					<h3 style={{ marginTop: 0 }}>Engagement score: {(result.engagement_score * 100).toFixed(0)}%</h3>
					<p>
						<strong>Next action:</strong> {result.predicted_next_action}
					</p>
					<ul>
						{result.recommendations.map((rec) => (
							<li key={`${rec.area}-${rec.action}`}>
								<strong>[{rec.priority}] {rec.area}:</strong> {rec.insight} &rarr; {rec.action}
							</li>
						))}
					</ul>
				</section>
			) : null}
		</main>
	);
}
