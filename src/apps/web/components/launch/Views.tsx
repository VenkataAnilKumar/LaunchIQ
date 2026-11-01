"use client";

import { useMemo, useState } from "react";

import type { ContentBundle, ContentItem, LaunchStrategy, Persona } from "@/packages/types";

import ContentBlock from "./ContentBlock";
import PersonaCard from "./PersonaCard";
import StrategyPhase from "./StrategyPhase";

export function PersonasView({ personas }: { personas: Persona[] }) {
	return (
		<section style={{ display: "grid", gap: "0.8rem", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))" }}>
			{personas.map((persona, index) => (
				<PersonaCard isPrimary={index === 0} key={`${persona.name}-${index}`} persona={persona} />
			))}
		</section>
	);
}

export function StrategyView({ strategy }: { strategy: LaunchStrategy }) {
	return (
		<section style={{ display: "grid", gap: "1rem" }}>
			<div className="panel">
				<h2 style={{ marginTop: 0 }}>Positioning</h2>
				<p>{strategy.positioning_statement}</p>
				<p style={{ marginBottom: 0, color: "var(--muted)" }}>
					Recommended launch date: {strategy.launch_date_recommendation}
				</p>
			</div>
			{strategy.phases.map((phase, index) => (
				<StrategyPhase index={index} key={`${phase.phase}-${index}`} phase={phase} />
			))}
			<div className="stat-grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))" }}>
				<div className="panel">
					<h3 style={{ marginTop: 0 }}>Budget allocation</h3>
					<ul style={{ margin: 0, paddingLeft: "1.1rem" }}>
						{Object.entries(strategy.budget_allocation).map(([area, share]) => (
							<li key={area}>{area}: {share}</li>
						))}
					</ul>
				</div>
				<div className="panel">
					<h3 style={{ marginTop: 0 }}>Success metrics</h3>
					<ul style={{ margin: 0, paddingLeft: "1.1rem" }}>
						{strategy.success_metrics.map((metric) => <li key={metric}>{metric}</li>)}
					</ul>
				</div>
				<div className="panel">
					<h3 style={{ marginTop: 0 }}>Risks</h3>
					<ul style={{ margin: 0, paddingLeft: "1.1rem" }}>
						{strategy.risks.map((risk) => <li key={risk}>{risk}</li>)}
					</ul>
				</div>
			</div>
		</section>
	);
}

type TabKey = "email" | "social" | "ads";

export function ContentView({ content }: { content: ContentBundle }) {
	const [tab, setTab] = useState<TabKey>("email");
	const items = useMemo<ContentItem[]>(() => {
		if (tab === "email") return content.email_sequence;
		if (tab === "social") return content.social_posts;
		return content.ad_copy;
	}, [content, tab]);

	return (
		<section style={{ display: "grid", gap: "1rem" }}>
			<div aria-label="Content type" className="panel" role="group" style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
				{(["email", "social", "ads"] as const).map((key) => (
					<button aria-pressed={key === tab} className={key === tab ? "btn btn-primary" : "btn btn-secondary"} key={key} onClick={() => setTab(key)} type="button">
						{key === "email" ? `Email (${content.email_sequence.length})` : key === "social" ? `Social (${content.social_posts.length})` : `Ads (${content.ad_copy.length})`}
					</button>
				))}
			</div>
			<div style={{ display: "grid", gap: "0.8rem", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))" }}>
				{items.map((item, index) => (
					<ContentBlock item={item} key={`${item.format}-${item.variant}-${index}`} />
				))}
			</div>
			{content.brand_voice_notes ? (
				<p className="field-hint">Brand voice notes: {content.brand_voice_notes}</p>
			) : null}
		</section>
	);
}
