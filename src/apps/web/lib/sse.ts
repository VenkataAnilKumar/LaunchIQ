import { useEffect, useRef, useState } from "react";

import { getAuthorizationHeader } from "@/lib/api";

export interface LaunchStreamEvent {
	type: string;
	launch_id?: string;
	agent_id?: string;
	status?: string;
	output?: Record<string, unknown>;
	error?: string;
	reason?: string;
	checkpoint?: string;
	output_preview?: Record<string, unknown>;
	decision?: "approve" | "edit" | "reject";
	edits?: Record<string, unknown>;
}

const SSE_RECONNECT_MS = 3000;

/**
 * Subscribe to a launch's event stream.
 *
 * The browser EventSource API cannot send an Authorization header, so the stream is read
 * with fetch() and parsed as text/event-stream. Reconnects automatically.
 */
export function useSSE(
	launchId: string | null,
	onEvent: (event: LaunchStreamEvent) => void,
): { connected: boolean } {
	const [connected, setConnected] = useState(false);
	const onEventRef = useRef(onEvent);
	onEventRef.current = onEvent;

	useEffect(() => {
		if (!launchId) {
			return undefined;
		}
		const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "";
		const controller = new AbortController();
		let retry: ReturnType<typeof setTimeout> | null = null;
		let stopped = false;

		async function connect(): Promise<void> {
			try {
				const headers = await getAuthorizationHeader();
				const res = await fetch(`${baseUrl}/api/v1/launches/${launchId}/stream`, {
					headers: { Accept: "text/event-stream", ...headers },
					signal: controller.signal,
					cache: "no-store",
				});
				if (!res.ok || !res.body) {
					throw new Error(`stream failed: ${res.status}`);
				}
				setConnected(true);
				const reader = res.body.getReader();
				const decoder = new TextDecoder();
				let buffer = "";
				for (;;) {
					const { done, value } = await reader.read();
					if (done) {
						break;
					}
					buffer += decoder.decode(value, { stream: true });
					let boundary = buffer.indexOf("\n\n");
					while (boundary !== -1) {
						const frame = buffer.slice(0, boundary);
						buffer = buffer.slice(boundary + 2);
						const data = frame
							.split("\n")
							.filter((line) => line.startsWith("data:"))
							.map((line) => line.slice(5).trim())
							.join("\n");
						if (data) {
							try {
								onEventRef.current(JSON.parse(data) as LaunchStreamEvent);
							} catch {
								// Ignore malformed events to keep the stream alive.
							}
						}
						boundary = buffer.indexOf("\n\n");
					}
				}
			} catch {
				// fall through to reconnect
			}
			setConnected(false);
			if (!stopped) {
				retry = setTimeout(() => void connect(), SSE_RECONNECT_MS);
			}
		}

		void connect();
		return () => {
			stopped = true;
			controller.abort();
			if (retry) {
				clearTimeout(retry);
			}
			setConnected(false);
		};
	}, [launchId]);

	return { connected };
}
