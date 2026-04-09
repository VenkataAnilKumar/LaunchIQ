"use client";

import { useCallback, useEffect } from "react";

import { type LaunchStreamEvent, useSSE } from "@/lib/sse";
import type { AgentId, HITLCheckpoint as HITLCheckpointType } from "@/packages/types";
import { useAgentStore } from "@/store/agentStore";
import { useLaunchStore } from "@/store/launchStore";

const VALID_AGENT_IDS = new Set<AgentId>([
	"orchestrator",
	"market_intelligence",
	"audience_insight",
	"launch_strategy",
	"content_generation",
	"analytics_feedback",
]);

const VALID_HITL_CHECKPOINTS = new Set<HITLCheckpointType>([
	"brief_review",
	"persona_review",
	"strategy_review",
	"content_review",
]);

function isAgentId(value: string): value is AgentId {
	return VALID_AGENT_IDS.has(value as AgentId);
}

function isHITLCheckpoint(value: string): value is HITLCheckpointType {
	return VALID_HITL_CHECKPOINTS.has(value as HITLCheckpointType);
}

export default function AgentStream({ launchId, onReload }: { launchId: string; onReload?: () => void }) {
	const updateAgent = useLaunchStore((state) => state.updateAgent);
	const setHITL = useLaunchStore((state) => state.setHITL);
	const setStreaming = useLaunchStore((state) => state.setStreaming);
	const addEvent = useAgentStore((state) => state.addEvent);
	const setCurrentAgent = useAgentStore((state) => state.setCurrentAgent);

	const handleEvent = useCallback(
		(event: LaunchStreamEvent) => {
			if (!launchId || event.launch_id !== launchId) {
				return;
			}

			addEvent({
				type: event.type,
				agent_id: event.agent_id && isAgentId(event.agent_id) ? event.agent_id : undefined,
				output: event.output,
				error: event.error,
			});

			if (event.type === "connected") {
				setStreaming(true);
				return;
			}

			if (event.type === "agent_started" && event.agent_id && isAgentId(event.agent_id)) {
				updateAgent({ agent_id: event.agent_id, launch_id: launchId, status: "running", started_at: new Date().toISOString() });
				setCurrentAgent(event.agent_id);
				return;
			}

			if (event.type === "agent_completed" && event.agent_id && isAgentId(event.agent_id)) {
				updateAgent({
					agent_id: event.agent_id,
					launch_id: launchId,
					status: "completed",
					output: event.output,
					completed_at: new Date().toISOString(),
				});
				setCurrentAgent(null);
				return;
			}

			if (event.type === "agent_failed" && event.agent_id && isAgentId(event.agent_id)) {
				updateAgent({ agent_id: event.agent_id, launch_id: launchId, status: "failed", error: event.error });
				setCurrentAgent(null);
				return;
			}

			if (
				event.type === "hitl_required" &&
				event.agent_id &&
				event.checkpoint &&
				event.output_preview &&
				isAgentId(event.agent_id) &&
				isHITLCheckpoint(event.checkpoint)
			) {
				setHITL({
					launch_id: launchId,
					checkpoint: event.checkpoint,
					agent_id: event.agent_id,
					output_preview: event.output_preview,
					created_at: new Date().toISOString(),
				});
				return;
			}

			if (event.type === "hitl_resolved") {
				setHITL(null);
				onReload?.();
			}
		},
		[addEvent, launchId, onReload, setCurrentAgent, setHITL, setStreaming, updateAgent],
	);

	const { connected } = useSSE(launchId, handleEvent);

	useEffect(() => {
		setStreaming(connected);
	}, [connected, setStreaming]);

	return null;
}
