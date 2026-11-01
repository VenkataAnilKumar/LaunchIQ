"use client";

import BriefCard from "@/components/launch/BriefCard";
import { ContentView, PersonasView, StrategyView } from "@/components/launch/Views";
import type { ContentBundle, LaunchStrategy, MarketData, Persona } from "@/packages/types";

/** The reviewer reads the same formatted view as the result pages, not raw JSON. */
export default function ReviewPreview({ agentId, output }: { agentId: string; output: Record<string, unknown> }) {
	if (agentId === "market_intelligence") {
		return <BriefCard data={output as unknown as MarketData} />;
	}
	if (agentId === "audience_insight") {
		const personas = [output.primary_persona, ...((output.secondary_personas as unknown[]) ?? [])].filter(Boolean) as Persona[];
		return <PersonasView personas={personas} />;
	}
	if (agentId === "launch_strategy") {
		return <StrategyView strategy={output as unknown as LaunchStrategy} />;
	}
	if (agentId === "content_generation") {
		return <ContentView content={output as unknown as ContentBundle} />;
	}
	return <pre className="panel" style={{ overflow: "auto" }}>{JSON.stringify(output, null, 2)}</pre>;
}
