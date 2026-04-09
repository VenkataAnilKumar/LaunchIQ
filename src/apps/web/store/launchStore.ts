import { create } from "zustand";

import type { AgentRun, HITLState, Launch } from "@/packages/types";

interface LaunchStore {
	launch: Launch | null;
	agents: AgentRun[];
	hitl: HITLState | null;
	isStreaming: boolean;
	setLaunch: (launch: Launch | null) => void;
	setAgents: (agents: AgentRun[]) => void;
	updateAgent: (agent: AgentRun) => void;
	setHITL: (hitl: HITLState | null) => void;
	setStreaming: (isStreaming: boolean) => void;
	reset: () => void;
}

export const useLaunchStore = create<LaunchStore>((set) => ({
	launch: null,
	agents: [],
	hitl: null,
	isStreaming: false,
	setLaunch: (launch) => set({ launch }),
	setAgents: (agents) => set({ agents }),
	updateAgent: (agent) =>
		set((state) => ({
			agents: state.agents.some((current) => current.agent_id === agent.agent_id)
				? state.agents.map((current) =>
						current.agent_id === agent.agent_id ? { ...current, ...agent } : current,
					)
				: [...state.agents, agent],
		})),
	setHITL: (hitl) => set({ hitl }),
	setStreaming: (isStreaming) => set({ isStreaming }),
	reset: () => set({ launch: null, agents: [], hitl: null, isStreaming: false }),
}));
