"use client";

import { useParams } from "next/navigation";

import LaunchSection from "@/components/launch/LaunchSection";
import { StrategyView } from "@/components/launch/Views";
import type { LaunchStrategy } from "@/packages/types";

export default function LaunchStrategyPage() {
	const { id } = useParams<{ id: string }>();
	return (
		<LaunchSection launchId={id} waitingFor="Launch Strategy">
			{(launch) => {
				const strategy = launch.brief.strategy as LaunchStrategy | undefined;
				return strategy ? <StrategyView strategy={strategy} /> : null;
			}}
		</LaunchSection>
	);
}
