"use client";

import AgentPending from "@/components/ui/AgentPending";
import { PageSkeleton } from "@/components/ui/Skeleton";
import { useLaunch } from "@/lib/useLaunch";

import type { LaunchDetailResponse } from "@/lib/api";

/** Shared loading / error / not-ready handling for the result pages. */
export default function LaunchSection({
	launchId,
	waitingFor,
	children,
}: {
	launchId: string;
	waitingFor: string;
	children: (launch: LaunchDetailResponse) => React.ReactNode | null;
}) {
	const { data, error, isLoading } = useLaunch(launchId);

	if (isLoading) {
		return <PageSkeleton />;
	}
	if (error || !data) {
		return (
			<section className="panel" role="alert" style={{ color: "var(--danger)" }}>
				Could not load this launch{error instanceof Error ? `: ${error.message}` : "."}
			</section>
		);
	}
	return children(data) ?? <AgentPending agentName={waitingFor} />;
}
