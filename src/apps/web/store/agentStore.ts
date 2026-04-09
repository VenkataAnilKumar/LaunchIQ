import { create } from "zustand";

import type { AgentId } from "@/packages/types";

interface AgentStore {
	events: Array<{
		type: string;
		agent_id?: AgentId;
		output?: unknown;
		error?: string;
		timestamp: string;
	}>;
	currentAgent: AgentId | null;
	addEvent: (event: Omit<AgentStore["events"][number], "timestamp"> & { timestamp?: string }) => void;
	setCurrentAgent: (agentId: AgentId | null) => void;
	clearEvents: () => void;
}

export const useAgentStore = create<AgentStore>((set) => ({
	events: [],
	currentAgent: null,
	addEvent: (event) =>
		set((state) => ({
			events: [...state.events, { ...event, timestamp: event.timestamp ?? new Date().toISOString() }],
		})),
	setCurrentAgent: (currentAgent) => set({ currentAgent }),
	clearEvents: () => set({ events: [], currentAgent: null }),
}));
