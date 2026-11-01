"use client";

import { useQuery } from "@tanstack/react-query";

import { getLaunch } from "@/lib/api";

const TERMINAL = new Set(["completed", "failed", "rejected"]);

/** Launch detail with loading/error state; keeps refreshing while the pipeline is still moving. */
export function useLaunch(launchId: string) {
	return useQuery({
		queryKey: ["launch", launchId],
		queryFn: () => getLaunch(launchId),
		refetchInterval: (query) => (query.state.data && TERMINAL.has(query.state.data.status) ? false : 5000),
	});
}
