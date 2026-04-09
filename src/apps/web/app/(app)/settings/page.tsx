import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { Settings2 } from "lucide-react";

import type { IntegrationMetadata } from "@/lib/api";
import {
	connectIntegrationServer,
	disconnectIntegrationServer,
	listIntegrationsServer,
	testIntegrationServer,
} from "@/lib/server-api";

type IntegrationName = "hubspot" | "slack" | "ga4";

interface IntegrationField {
	key: string;
	label: string;
	placeholder: string;
	multiline?: boolean;
}

const INTEGRATIONS = ["hubspot", "slack", "ga4"] as const;

const COPY: Record<IntegrationName, { description: string; detail: string }> = {
	hubspot: {
		description: "Sync CRM context and campaign outcomes into LaunchIQ workflows.",
		detail: "Used by strategy and analytics flows when launch feedback needs pipeline context.",
	},
	slack: {
		description: "Send approvals, summaries, and alerts into the launch command channel.",
		detail: "Best for HITL checkpoints and launch-room notifications.",
	},
	ga4: {
		description: "Pull traffic and conversion signals back into post-launch analysis.",
		detail: "Feeds the analytics feedback agent with property-level performance data.",
	},
};

const FIELD_CONFIG: Record<IntegrationName, IntegrationField[]> = {
	hubspot: [
		{ key: "portal_id", label: "Portal ID", placeholder: "12345678" },
		{ key: "access_token", label: "Private app token", placeholder: "pat-na1-..." },
	],
	slack: [
		{ key: "bot_token", label: "Bot token", placeholder: "xoxb-..." },
		{ key: "channel_id", label: "Channel ID", placeholder: "C01234567" },
	],
	ga4: [
		{ key: "property_id", label: "Property ID", placeholder: "123456789" },
		{
			key: "service_account_json",
			label: "Service account JSON",
			placeholder: "Paste service account JSON",
			multiline: true,
		},
	],
};

const EMPTY_METADATA: Record<IntegrationName, IntegrationMetadata> = {
	hubspot: {
		name: "hubspot",
		status: "disconnected",
		connected: false,
		has_credentials: false,
		connected_at: null,
		updated_at: null,
		disconnected_at: null,
		last_error: null,
		configured_fields: [],
	},
	slack: {
		name: "slack",
		status: "disconnected",
		connected: false,
		has_credentials: false,
		connected_at: null,
		updated_at: null,
		disconnected_at: null,
		last_error: null,
		configured_fields: [],
	},
	ga4: {
		name: "ga4",
		status: "disconnected",
		connected: false,
		has_credentials: false,
		connected_at: null,
		updated_at: null,
		disconnected_at: null,
		last_error: null,
		configured_fields: [],
	},
};

function parseIntegrationName(value: FormDataEntryValue | null): IntegrationName {
	const normalized = typeof value === "string" ? value : "";
	if (normalized === "hubspot" || normalized === "slack" || normalized === "ga4") {
		return normalized;
	}
	throw new Error("Unsupported integration selected");
}

function readCredentials(name: IntegrationName, formData: FormData): Record<string, string> {
	const values: Record<string, string> = {};
	for (const field of FIELD_CONFIG[name]) {
		const value = String(formData.get(field.key) ?? "").trim();
		if (!value) {
			throw new Error(`${field.label} is required`);
		}
		values[field.key] = value;
	}
	return values;
}

function settingsUrl(params: { error?: string; notice?: string }): string {
	const query = new URLSearchParams();
	if (params.error) {
		query.set("error", params.error);
	}
	if (params.notice) {
		query.set("notice", params.notice);
	}
	const suffix = query.toString();
	return suffix ? `/settings?${suffix}` : "/settings";
}

async function testCredentialsAction(formData: FormData): Promise<void> {
	"use server";

	try {
		const name = parseIntegrationName(formData.get("integration"));
		const credentials = readCredentials(name, formData);
		const result = await testIntegrationServer(name, credentials);
		revalidatePath("/settings");
		redirect(settingsUrl({ notice: `${name}: ${result.message}` }));
	} catch (error) {
		const message = error instanceof Error ? error.message : "Unable to test credentials";
		revalidatePath("/settings");
		redirect(settingsUrl({ error: message }));
	}
}

async function connectAction(formData: FormData): Promise<void> {
	"use server";

	try {
		const name = parseIntegrationName(formData.get("integration"));
		const credentials = readCredentials(name, formData);
		const test = await testIntegrationServer(name, credentials);
		if (!test.valid) {
			revalidatePath("/settings");
			redirect(settingsUrl({ error: `${name}: ${test.message}` }));
		}
		await connectIntegrationServer(name, credentials);
		revalidatePath("/settings");
		redirect(settingsUrl({ notice: `${name} connected` }));
	} catch (error) {
		const message = error instanceof Error ? error.message : "Unable to connect integration";
		revalidatePath("/settings");
		redirect(settingsUrl({ error: message }));
	}
}

async function disconnectAction(formData: FormData): Promise<void> {
	"use server";

	try {
		const name = parseIntegrationName(formData.get("integration"));
		await disconnectIntegrationServer(name);
		revalidatePath("/settings");
		redirect(settingsUrl({ notice: `${name} disconnected` }));
	} catch (error) {
		const message = error instanceof Error ? error.message : "Unable to disconnect integration";
		revalidatePath("/settings");
		redirect(settingsUrl({ error: message }));
	}
}

export default async function SettingsPage({
	searchParams,
}: {
	searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
	const params = await searchParams;
	const notice = typeof params.notice === "string" ? params.notice : null;
	const error = typeof params.error === "string" ? params.error : null;

	let connectedCount = 0;
	let status = EMPTY_METADATA;
	let loadError: string | null = null;

	try {
		const response = await listIntegrationsServer();
		status = response.integrations;
		connectedCount = response.connected_count;
	} catch (fetchError) {
		loadError = fetchError instanceof Error ? fetchError.message : "Failed to load integrations.";
	}

	return (
		<main style={{ display: "grid", gap: "1rem" }}>
			<section
				className="panel"
				style={{
					display: "flex",
					justifyContent: "space-between",
					gap: "1rem",
					alignItems: "center",
					flexWrap: "wrap",
				}}
			>
				<div>
					<h1 style={{ margin: 0 }}>Integrations</h1>
					<p style={{ margin: "0.35rem 0 0", color: "var(--muted)" }}>
						Connect outbound channels and measurement systems for launch execution.
					</p>
				</div>
				<div className="panel" style={{ padding: "0.6rem 0.9rem", display: "flex", gap: "0.5rem", alignItems: "center" }}>
					<Settings2 size={16} />
					<span style={{ color: "var(--muted)" }}>{`${connectedCount}/3 connected`}</span>
				</div>
			</section>

			{notice ? (
				<section className="panel">
					<p style={{ margin: 0, color: "var(--success)" }}>{notice}</p>
				</section>
			) : null}

			{error ? (
				<section className="panel">
					<p style={{ margin: 0, color: "var(--danger)" }}>{error}</p>
				</section>
			) : null}

			{loadError ? (
				<section className="panel">
					<p style={{ margin: 0, color: "var(--danger)" }}>{loadError}</p>
				</section>
			) : null}

			<section style={{ display: "grid", gap: "0.8rem" }}>
				{INTEGRATIONS.map((name) => {
					const metadata = status[name];
					const isConnected = metadata.connected;
					const fieldsLabel =
						metadata.configured_fields.length > 0
							? `Configured fields: ${metadata.configured_fields.join(", ")}`
							: "No credentials configured yet.";
					const syncLabel = metadata.updated_at
						? `Last updated ${new Date(metadata.updated_at).toLocaleString()}`
						: "No updates yet.";

					return (
						<article
							className="panel"
							key={name}
							style={{ display: "grid", gap: "0.8rem" }}
						>
							<div style={{ display: "grid", gap: "0.35rem" }}>
								<div style={{ display: "flex", gap: "0.5rem", alignItems: "center", flexWrap: "wrap" }}>
									<strong style={{ textTransform: "capitalize" }}>{name}</strong>
									<span className={`status-pill ${isConnected ? "status-completed" : "status-pending"}`}>
										{isConnected ? "Connected" : "Not connected"}
									</span>
								</div>
								<p style={{ margin: 0, color: "var(--muted)" }}>{COPY[name].description}</p>
								<small style={{ color: "var(--muted)" }}>{COPY[name].detail}</small>
								<small style={{ color: "var(--muted)" }}>{fieldsLabel}</small>
								<small style={{ color: "var(--muted)" }}>{syncLabel}</small>
								{metadata.last_error ? <small style={{ color: "var(--danger)" }}>{metadata.last_error}</small> : null}
							</div>

							<form style={{ display: "grid", gap: "0.65rem" }}>
								<input name="integration" type="hidden" value={name} />
								{FIELD_CONFIG[name].map((field) => (
									<label key={`${name}-${field.key}`} style={{ display: "grid", gap: "0.35rem" }}>
										<span>{field.label}</span>
										{field.multiline ? (
											<textarea name={field.key} placeholder={field.placeholder} rows={4} />
										) : (
											<input name={field.key} placeholder={field.placeholder} />
										)}
									</label>
								))}
								<div style={{ display: "flex", gap: "0.7rem", flexWrap: "wrap" }}>
									<button className="btn btn-secondary" formAction={testCredentialsAction} type="submit">
										Test credentials
									</button>
									<button className="btn btn-primary" formAction={connectAction} type="submit">
										{isConnected ? "Update credentials" : "Connect"}
									</button>
									<button className="btn btn-secondary" formAction={disconnectAction} type="submit">
										Disconnect
									</button>
								</div>
							</form>
						</article>
					);
				})}
			</section>
		</main>
	);
}
