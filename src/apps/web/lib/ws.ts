export function buildLaunchWsUrl(launchId: string): string {
	const base = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000";
	return `${base}/api/v1/launches/${launchId}/ws`;
}
