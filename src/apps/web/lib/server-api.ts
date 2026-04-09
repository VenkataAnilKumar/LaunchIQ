import { auth } from "@clerk/nextjs/server";

import type { Launch } from "@/packages/types";

import type {
	IntegrationListResponse,
	IntegrationMutationResponse,
} from "@/lib/api";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

type IntegrationName = "hubspot" | "slack" | "ga4";

async function getServerBearerToken(): Promise<string> {
	if (!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY) {
		throw new Error("Clerk is not configured. Set NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY.");
	}

	const tokenTemplate = process.env.NEXT_PUBLIC_CLERK_JWT_TEMPLATE;
	const session = await auth();
	const token = await session.getToken(tokenTemplate ? { template: tokenTemplate } : undefined);
	if (!token) {
		throw new Error("No Clerk session token available. Sign in and try again.");
	}
	return token;
}

async function serverFetch<T>(path: string, init?: RequestInit): Promise<T> {
	const token = await getServerBearerToken();
	const res = await fetch(`${API_URL}/api/v1${path}`, {
		...init,
		headers: {
			"Content-Type": "application/json",
			Authorization: `Bearer ${token}`,
			...(init?.headers ?? {}),
		},
		cache: "no-store",
	});

	if (!res.ok) {
		throw new Error(await res.text());
	}

	return (await res.json()) as T;
}

export async function listLaunchesServer(): Promise<Launch[]> {
	return serverFetch<Launch[]>("/launches");
}

export async function listIntegrationsServer(): Promise<IntegrationListResponse> {
	return serverFetch<IntegrationListResponse>("/integrations");
}

export async function connectIntegrationServer(
	name: IntegrationName,
	credentials: Record<string, string>,
): Promise<IntegrationMutationResponse> {
	return serverFetch<IntegrationMutationResponse>(`/integrations/${name}`, {
		method: "POST",
		body: JSON.stringify({ credentials }),
	});
}

export async function disconnectIntegrationServer(
	name: IntegrationName,
): Promise<IntegrationMutationResponse> {
	return serverFetch<IntegrationMutationResponse>(`/integrations/${name}`, {
		method: "DELETE",
	});
}

export async function testIntegrationServer(
	name: IntegrationName,
	credentials: Record<string, string>,
): Promise<{ integration: IntegrationName; valid: boolean; message: string }> {
	return serverFetch<{ integration: IntegrationName; valid: boolean; message: string }>(
		`/integrations/test/${name}`,
		{
			method: "POST",
			body: JSON.stringify({ credentials }),
		},
	);
}
