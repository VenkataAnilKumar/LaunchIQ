import Link from "next/link";
import type { Route } from "next";

import EmptyState from "@/components/ui/EmptyState";
import { listLaunchesServer } from "@/lib/server-api";

export default async function DashboardPage() {
	let rows: Awaited<ReturnType<typeof listLaunchesServer>> = [];
	let error: string | null = null;

	try {
		rows = await listLaunchesServer();
	} catch (loadError) {
		error = loadError instanceof Error ? loadError.message : "Failed to load launches";
	}

	return (
		<main style={{ display: "grid", gap: "1rem" }}>
			<section className="panel" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
				<div>
					<h1 style={{ margin: 0 }}>Launch Dashboard</h1>
					<p style={{ margin: "0.35rem 0 0", color: "var(--muted)" }}>
						Recent launches and pipeline status.
					</p>
				</div>
				<Link className="btn btn-primary" href="/launch/new">
					New launch
				</Link>
			</section>

			<section className="panel">
				{error ? <p style={{ color: "var(--danger)" }}>{error}</p> : null}

				{!error && rows.length === 0 ? (
					<EmptyState
						description="Create your first launch brief to start the agent pipeline."
						title="No Launches Yet"
						action={{ label: "Create launch", href: "/launch/new" }}
					/>
				) : null}

				{rows.length > 0 ? (
					<div style={{ display: "grid", gap: "0.6rem" }}>
						{rows.map((row) => (
							<Link className="panel" href={`/launch/${row.launch_id}/tracker` as Route} key={row.launch_id}>
								<div style={{ display: "flex", justifyContent: "space-between", gap: "0.8rem" }}>
									<div>
										<strong>{row.product_name}</strong>
										<p style={{ margin: "0.3rem 0 0", color: "var(--muted)" }}>{row.target_market}</p>
									</div>
									<span className={`status-pill status-${row.status}`}>{row.status}</span>
								</div>
							</Link>
						))}
					</div>
				) : null}
			</section>
		</main>
	);
}
