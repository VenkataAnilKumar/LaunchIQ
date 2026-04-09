"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";

import ContentBlock from "@/components/launch/ContentBlock";
import AgentPending from "@/components/ui/AgentPending";
import { getLaunch } from "@/lib/api";
import type { ContentBundle, ContentItem } from "@/packages/types";

type TabKey = "email" | "social" | "ads";

export default function LaunchContentPage() {
	const params = useParams<{ id: string }>();
	const [content, setContent] = useState<ContentBundle | null>(null);
	const [tab, setTab] = useState<TabKey>("email");

	useEffect(() => {
		void getLaunch(params.id).then((launch) => {
			setContent((launch.brief.content as ContentBundle | undefined) ?? null);
		});
	}, [params.id]);

	const items = useMemo<ContentItem[]>(() => {
		if (!content) return [];
		if (tab === "email") return content.email_sequence;
		if (tab === "social") return content.social_posts;
		return content.ad_copy;
	}, [content, tab]);

	if (!content) {
		return <AgentPending agentName="Content Generation" />;
	}

	return (
		<section style={{ display: "grid", gap: "1rem" }}>
			<div className="panel" style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
				{(["email", "social", "ads"] as const).map((key) => (
					<button
						className={key === tab ? "btn btn-primary" : "btn btn-secondary"}
						key={key}
						onClick={() => setTab(key)}
						type="button"
					>
						{key}
					</button>
				))}
			</div>
			<div style={{ display: "grid", gap: "0.8rem", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))" }}>
				{items.map((item, index) => (
					<ContentBlock item={item} key={`${item.format}-${item.variant}-${index}`} />
				))}
			</div>
		</section>
	);
}
