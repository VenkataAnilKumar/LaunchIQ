"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import BriefCard from "@/components/launch/BriefCard";
import AgentPending from "@/components/ui/AgentPending";
import { getLaunch } from "@/lib/api";
import type { MarketData } from "@/packages/types";

export default function LaunchBriefPage() {
	const params = useParams<{ id: string }>();
	const [data, setData] = useState<MarketData | null>(null);

	useEffect(() => {
		void getLaunch(params.id).then((launch) => {
			setData((launch.brief.market_data as MarketData | undefined) ?? null);
		});
	}, [params.id]);

	return data ? <BriefCard data={data} /> : <AgentPending agentName="Market Intelligence" />;
}
