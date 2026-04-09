import type { Persona } from "@/packages/types";

export default function PersonaCard({ persona, isPrimary = false }: { persona: Persona; isPrimary?: boolean }) {
	return (
		<article className="panel" style={{ display: "grid", gap: "0.7rem" }}>
			<div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
				<div style={{ display: "flex", alignItems: "center", gap: "0.8rem" }}>
					<div
						style={{
							width: "3rem",
							height: "3rem",
							borderRadius: "999px",
							background: "linear-gradient(135deg, #159d75, #2d6cdf)",
							color: "white",
							display: "grid",
							placeItems: "center",
							fontWeight: 700,
						}}
					>
						{persona.name.charAt(0)}
					</div>
					<div>
						<strong>{persona.name}</strong>
						<div style={{ color: "var(--muted)" }}>{persona.role} | {persona.age_range}</div>
					</div>
				</div>
				{isPrimary ? <span className="status-pill status-completed">Primary</span> : null}
			</div>
			<div><strong>Pain Points:</strong> {persona.pain_points.join(", ")}</div>
			<div><strong>Goals:</strong> {persona.goals.join(", ")}</div>
			<div><strong>Channels:</strong> {persona.channels.join(", ")}</div>
			<blockquote style={{ margin: 0, paddingLeft: "0.8rem", borderLeft: "3px solid var(--line)", color: "var(--muted)" }}>
				{persona.message_hook}
			</blockquote>
		</article>
	);
}
