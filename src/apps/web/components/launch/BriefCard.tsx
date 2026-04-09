import type { MarketData } from "@/packages/types";

export default function BriefCard({ data }: { data: MarketData }) {
	return (
		<section className="panel" style={{ display: "grid", gap: "1rem" }}>
			<div style={{ display: "grid", gap: "0.75rem", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))" }}>
				<div className="panel">
					<div style={{ color: "var(--muted)" }}>Market Size</div>
					<strong>{data.market_size}</strong>
				</div>
				<div className="panel">
					<div style={{ color: "var(--muted)" }}>Growth Rate</div>
					<strong>{data.growth_rate}</strong>
				</div>
			</div>

			<div>
				<h3>Competitors</h3>
				<div style={{ display: "grid", gap: "0.75rem", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))" }}>
					{data.competitors.map((competitor) => (
						<article className="panel" key={competitor.name}>
							<strong>{competitor.name}</strong>
							<p style={{ color: "var(--muted)" }}>{competitor.positioning}</p>
							<p style={{ marginBottom: "0.35rem" }}><strong>Strengths:</strong> {competitor.strengths.join(", ")}</p>
							<p style={{ margin: 0 }}><strong>Weaknesses:</strong> {competitor.weaknesses.join(", ")}</p>
						</article>
					))}
				</div>
			</div>

			<div className="panel" style={{ background: "#f7fbf5" }}>
				<h3 style={{ marginTop: 0 }}>White Space</h3>
				<p>{data.white_space}</p>
				<h4>Recommended Positioning</h4>
				<p style={{ marginBottom: 0 }}>{data.recommended_positioning}</p>
			</div>
		</section>
	);
}
