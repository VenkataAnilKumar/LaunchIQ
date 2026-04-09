"use client";

import { useState } from "react";

import type { ContentItem } from "@/packages/types";

export default function ContentBlock({ item }: { item: ContentItem }) {
	const [copied, setCopied] = useState(false);

	async function copy(): Promise<void> {
		await navigator.clipboard.writeText(`${item.headline}\n\n${item.body}\n\nCTA: ${item.cta}`);
		setCopied(true);
		setTimeout(() => setCopied(false), 1500);
	}

	return (
		<article className="panel" style={{ display: "grid", gap: "0.6rem" }}>
			<div style={{ display: "flex", justifyContent: "space-between", gap: "0.5rem", alignItems: "center" }}>
				<div>
					<span className="status-pill status-pending">{item.format}</span>
					<span style={{ marginLeft: "0.4rem", color: "var(--muted)" }}>Variant {item.variant.toUpperCase()}</span>
				</div>
				<button className="btn btn-secondary" onClick={copy} type="button">{copied ? "Copied" : "Copy"}</button>
			</div>
			<strong>{item.headline}</strong>
			<p style={{ margin: 0 }}>{item.body}</p>
			<div><strong>CTA:</strong> {item.cta}</div>
			<div style={{ color: "var(--muted)" }}>Persona: {item.target_persona}</div>
		</article>
	);
}
