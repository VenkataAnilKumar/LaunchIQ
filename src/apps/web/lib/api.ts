import type { AgentRun, HITLDecision, HITLState, Launch } from "@/packages/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "";
const API_PREFIX = `${BASE_URL}/api/v1`;

type AccessTokenProvider = () => Promise<string | null>;

let accessTokenProvider: AccessTokenProvider | null = null;

export function setAccessTokenProvider(provider: AccessTokenProvider | null): void {
	accessTokenProvider = provider;
}

export interface LaunchCreateInput {
	product_name: string;
	description: string;
	target_market: string;
	competitors: string[];
}

export interface LaunchCreateResponse {
	launch_id: string;
	status: string;
	created_at: string;
}

export interface LaunchDetailResponse {
	launch_id: string;
	status: string;
	brief: Record<string, unknown>;
	pipeline: AgentRun[];
	hitl_pending: boolean;
	hitl_checkpoint: string | null;
}

export interface IntegrationMetadata {
	name: "hubspot" | "slack" | "ga4";
	status: "connected" | "disconnected";
	connected: boolean;
	has_credentials: boolean;
	connected_at: string | null;
	updated_at: string | null;
	disconnected_at: string | null;
	last_error: string | null;
	configured_fields: string[];
}

export interface IntegrationListResponse {
	integrations: Record<"hubspot" | "slack" | "ga4", IntegrationMetadata>;
	connected_count: number;
	updated_at: string | null;
}

export interface IntegrationMutationResponse {
	integration: "hubspot" | "slack" | "ga4";
	status: "connected" | "disconnected";
	metadata: IntegrationMetadata;
}

async function getAuthorizationHeader(): Promise<Record<string, string>> {
	const clerkToken = accessTokenProvider ? await accessTokenProvider() : null;
	const token = clerkToken ?? process.env.NEXT_PUBLIC_DEV_BEARER_TOKEN ?? null;
	return token ? { Authorization: `Bearer ${token}` } : {};
}

async function parseResponse<T>(res: Response): Promise<T> {
	if (!res.ok) {
		if (res.status === 401) {
			throw new Error("Authentication required. Sign in again to continue.");
		}
		throw new Error(await res.text());
	}
	return (await res.json()) as T;
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
	const authHeader = await getAuthorizationHeader();
	const res = await fetch(`${API_PREFIX}${path}`, {
		...init,
		headers: {
			"Content-Type": "application/json",
			...authHeader,
			...(init?.headers ?? {}),
		},
		cache: "no-store",
	});
	return parseResponse<T>(res);
}

export async function createLaunch(data: LaunchCreateInput): Promise<LaunchCreateResponse> {
	return apiFetch<LaunchCreateResponse>("/launches", {
		method: "POST",
		body: JSON.stringify(data),
	});
}

export async function getLaunch(launchId: string): Promise<LaunchDetailResponse> {
	return apiFetch<LaunchDetailResponse>(`/launches/${launchId}`);
}

export async function listLaunches(): Promise<Launch[]> {
	return apiFetch<Launch[]>("/launches");
}

export async function getPendingHITL(launchId: string): Promise<HITLState | null> {
	const authHeader = await getAuthorizationHeader();
	const res = await fetch(`${API_PREFIX}/hitl/${launchId}/pending`, {
		headers: authHeader,
		cache: "no-store",
	});
	if (res.status === 404) {
		return null;
	}
	return parseResponse<HITLState | null>(res);
}

export async function resolveHITL(
	launchId: string,
	decision: HITLDecision,
	edits?: Record<string, unknown>,
): Promise<{ status: string; next_step: string }> {
	return apiFetch<{ status: string; next_step: string }>(`/hitl/${launchId}/decide`, {
		method: "POST",
		body: JSON.stringify({ decision, edits }),
	});
}

export async function retryAgent(launchId: string, agentId: string): Promise<{ launch_id: string; agent_id: string; status: string }> {
	return apiFetch<{ launch_id: string; agent_id: string; status: string }>(`/agents/${launchId}/${agentId}/retry`, {
		method: "POST",
	});
}

export async function listIntegrations(): Promise<IntegrationListResponse> {
	return apiFetch<IntegrationListResponse>("/integrations");
}

export async function connectIntegration(
	name: "hubspot" | "slack" | "ga4",
	credentials: Record<string, unknown>,
): Promise<IntegrationMutationResponse> {
	return apiFetch<IntegrationMutationResponse>(`/integrations/${name}`, {
		method: "POST",
		body: JSON.stringify({ credentials }),
	});
}

export async function disconnectIntegration(name: "hubspot" | "slack" | "ga4"): Promise<IntegrationMutationResponse> {
	return apiFetch<IntegrationMutationResponse>(`/integrations/${name}`, {
		method: "DELETE",
	});
}

const RECENT_LAUNCHES_KEY = "launchiq:recent-launches";

export function rememberLaunchId(launchId: string): void {
	if (typeof window === "undefined") {
		return;
	}
	const existing = getRememberedLaunchIds().filter((id) => id !== launchId);
	const next = [launchId, ...existing].slice(0, 20);
	localStorage.setItem(RECENT_LAUNCHES_KEY, JSON.stringify(next));
}

export function getRememberedLaunchIds(): string[] {
	if (typeof window === "undefined") {
		return [];
	}
	const raw = localStorage.getItem(RECENT_LAUNCHES_KEY);
	if (!raw) {
		return [];
	}
	try {
		const parsed = JSON.parse(raw);
		return Array.isArray(parsed) ? parsed.filter((v) => typeof v === "string") : [];
	} catch {
		return [];
	}
}

export function toLaunchSummary(id: string, detail: LaunchDetailResponse): Launch {
	const now = new Date().toISOString();
	return {
		launch_id: id,
		product_name: String(detail.brief.product_name ?? "Untitled launch"),
		description: String(detail.brief.description ?? ""),
		target_market: String(detail.brief.target_market ?? ""),
		competitors: Array.isArray(detail.brief.competitors)
			? detail.brief.competitors.filter((c): c is string => typeof c === "string")
			: [],
		status: detail.status as Launch["status"],
		created_at: now,
		updated_at: now,
	};
}
