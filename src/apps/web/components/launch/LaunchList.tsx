"use client";

import Link from "next/link";
import type { Route } from "next";
import { useMemo, useState } from "react";

import EmptyState from "@/components/ui/EmptyState";
import StatusPill from "@/components/ui/StatusPill";
import { formatDate } from "@/lib/format";
import type { Launch } from "@/packages/types";

const FILTERS: Array<{ value: string; label: string }> = [
	{ value: "all", label: "All" },
	{ value: "hitl_pending", label: "Needs review" },
	{ value: "running", label: "Running" },
	{ value: "completed", label: "Completed" },
	{ value: "failed", label: "Failed" },
];

export default function LaunchList({ rows }: { rows: Launch[] }) {
	const [query, setQuery] = useState("");
	const [filter, setFilter] = useState("all");

	const counts = useMemo(
		() => ({
			total: rows.length,
			review: rows.filter((r) => r.status === "hitl_pending").length,
			running: rows.filter((r) => r.status === "running" || r.status === "pending").length,
			completed: rows.filter((r) => r.status === "completed").length,
		}),
		[rows],
	);

	const visible = useMemo(() => {
		const needle = query.trim().toLowerCase();
		return rows.filter((row) => {
			const statusMatch =
				filter === "all" || row.status === filter || (filter === "running" && row.status === "pending");
			const textMatch =
				!needle || `${row.product_name} ${row.target_market} ${row.description}`.toLowerCase().includes(needle);
			return statusMatch && textMatch;
		});
	}, [rows, query, filter]);

	if (rows.length === 0) {
		return (
			<EmptyState
				action={{ label: "Create your first launch", href: "/launch/new" }}
				description="Describe your product and the agents will research the market, build personas, plan the launch and draft content. You review it at two checkpoints."
				title="No launches yet"
			/>
		);
	}

	return (
		<div style={{ display: "grid", gap: "1rem" }}>
			<div className="stat-grid">
				<div className="stat"><strong>{counts.total}</strong><span>Launches</span></div>
				<div className="stat"><strong>{counts.review}</strong><span>Need your review</span></div>
				<div className="stat"><strong>{counts.running}</strong><span>In progress</span></div>
				<div className="stat"><strong>{counts.completed}</strong><span>Completed</span></div>
			</div>

			<section className="panel" style={{ display: "grid", gap: "0.8rem" }}>
				<div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap", alignItems: "center" }}>
					<label className="sr-only" htmlFor="launch-search">Search launches</label>
					<input
						id="launch-search"
						onChange={(event) => setQuery(event.target.value)}
						placeholder="Search launches"
						style={{ maxWidth: "20rem" }}
						type="search"
						value={query}
					/>
					<div aria-label="Filter by status" role="group" style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap" }}>
						{FILTERS.map((item) => (
							<button aria-pressed={filter === item.value} className="chip" key={item.value} onClick={() => setFilter(item.value)} type="button">
								{item.label}
							</button>
						))}
					</div>
				</div>

				{visible.length === 0 ? (
					<p style={{ color: "var(--muted)", margin: 0 }}>No launches match your search.</p>
				) : (
					<div style={{ display: "grid", gap: "0.6rem" }}>
						{visible.map((row) => (
							<Link
								className="panel launch-card"
								data-attention={row.status === "hitl_pending"}
								href={`/launch/${row.launch_id}/tracker` as Route}
								key={row.launch_id}
							>
								<div style={{ display: "flex", justifyContent: "space-between", gap: "0.8rem", alignItems: "start" }}>
									<strong>{row.product_name}</strong>
									<StatusPill status={row.status} />
								</div>
								<span style={{ color: "var(--muted)" }}>{row.target_market}</span>
								<span style={{ color: "var(--muted)", fontSize: "0.82rem" }}>Created {formatDate(row.created_at)}</span>
							</Link>
						))}
					</div>
				)}
			</section>
		</div>
	);
}
