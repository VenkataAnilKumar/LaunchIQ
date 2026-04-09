import { useCallback, useEffect, useState } from "react";

export interface LaunchStreamEvent {
	type: string;
	launch_id?: string;
	agent_id?: string;
	status?: string;
	output?: Record<string, unknown>;
	error?: string;
	checkpoint?: string;
	output_preview?: Record<string, unknown>;
	decision?: "approve" | "edit" | "reject";
	edits?: Record<string, unknown>;
}

const SSE_RECONNECT_MS = 3000;

export function useSSE(
	launchId: string | null,
	onEvent: (event: LaunchStreamEvent) => void,
	): { connected: boolean } {
	const [connected, setConnected] = useState(false);

	const connect = useCallback(() => {
		if (!launchId) {
			return () => undefined;
		}

		const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "";
		const source = new EventSource(`${baseUrl}/api/v1/launches/${launchId}/stream`);
		let retryHandle: ReturnType<typeof setTimeout> | null = null;

		source.onopen = () => {
			setConnected(true);
		};

		source.onmessage = (message) => {
			try {
				const parsed = JSON.parse(message.data) as LaunchStreamEvent;
				onEvent(parsed);
			} catch {
				// Ignore malformed events to keep stream alive.
			}
		};

		source.onerror = () => {
			setConnected(false);
			source.close();
			retryHandle = setTimeout(() => {
				connect();
			}, SSE_RECONNECT_MS);
		};

		return () => {
			setConnected(false);
			source.close();
			if (retryHandle) {
				clearTimeout(retryHandle);
			}
		};
	}, [launchId, onEvent]);

	useEffect(() => {
		return connect();
	}, [connect]);

	return { connected };
}
