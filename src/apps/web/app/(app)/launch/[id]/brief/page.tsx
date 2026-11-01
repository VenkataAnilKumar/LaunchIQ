"use client";

import { useParams } from "next/navigation";

import BriefCard from "@/components/launch/BriefCard";
import LaunchSection from "@/components/launch/LaunchSection";
import type { MarketData } from "@/packages/types";

export default function LaunchBriefPage() {
	const { id } = useParams<{ id: string }>();
	return (
		<LaunchSection launchId={id} waitingFor="Market Intelligence">
			{(launch) => {
				const data = launch.brief.market_data as MarketData | undefined;
				return data ? <BriefCard data={data} /> : null;
			}}
		</LaunchSection>
	);
}
