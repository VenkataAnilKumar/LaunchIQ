import type { LaunchStrategy } from "@/packages/types";

type Phase = LaunchStrategy["phases"][number];

export default function StrategyPhase({ phase, index }: { phase: Phase; index: number }) {
	return (
		<article className="panel" style={{ display: "grid", gap: "0.6rem" }}>
			<div style={{ display: "flex", alignItems: "center", gap: "0.7rem" }}>
				<div
					style={{
						width: "2rem",
						height: "2rem",
						borderRadius: "999px",
						background: "#e8f3e8",
						display: "grid",
						placeItems: "center",
						fontWeight: 700,
					}}
				>
					{index + 1}
				</div>
				<div>
					<strong>{phase.phase}</strong>
					<div style={{ color: "var(--muted)" }}>{phase.duration}</div>
				</div>
			</div>
			<div><strong>Goals:</strong> {phase.goals.join(", ")}</div>
			<div><strong>Tactics:</strong> {phase.tactics.join(", ")}</div>
			<div><strong>KPIs:</strong> {phase.kpis.join(", ")}</div>
		</article>
	);
}
