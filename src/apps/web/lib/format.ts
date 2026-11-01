export function formatDate(iso: string | null | undefined): string {
	if (!iso) {
		return "";
	}
	const date = new Date(iso.endsWith("Z") || iso.includes("+") ? iso : `${iso}Z`);
	if (Number.isNaN(date.getTime())) {
		return "";
	}
	return date.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

export function formatCost(usd: number | null | undefined): string {
	if (!usd) {
		return "$0.00";
	}
	return usd < 0.01 ? `$${usd.toFixed(4)}` : `$${usd.toFixed(2)}`;
}

export const STATUS_LABEL: Record<string, string> = {
	pending: "Queued",
	running: "Running",
	hitl_pending: "Needs review",
	completed: "Completed",
	failed: "Failed",
	rejected: "Rejected",
};

export const AGENT_LABEL: Record<string, string> = {
	market_intelligence: "Market Intelligence",
	audience_insight: "Audience Insight",
	launch_strategy: "Launch Strategy",
	content_generation: "Content Generation",
	analytics_feedback: "Analytics",
};
