import Link from "next/link";

import LaunchList from "@/components/launch/LaunchList";
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
			<section className="panel" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "1rem", flexWrap: "wrap" }}>
				<div>
					<h1 style={{ margin: 0 }}>Launches</h1>
					<p style={{ margin: "0.35rem 0 0", color: "var(--muted)" }}>Your launch briefs and where each one stands.</p>
				</div>
				<Link className="btn btn-primary" href="/launch/new">
					New launch
				</Link>
			</section>

			{error ? (
				<section className="panel" role="alert" style={{ color: "var(--danger)" }}>
					Could not load your launches: {error}
				</section>
			) : (
				<LaunchList rows={rows} />
			)}
		</main>
	);
}
