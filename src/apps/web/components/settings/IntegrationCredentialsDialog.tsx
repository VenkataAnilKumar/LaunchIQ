"use client";

import * as Dialog from "@radix-ui/react-dialog";
import { useEffect, useMemo, useState } from "react";

type IntegrationName = "hubspot" | "slack" | "ga4";

interface IntegrationField {
	key: string;
	label: string;
	placeholder: string;
	type?: "text" | "password";
	help?: string;
}

const FIELD_CONFIG: Record<IntegrationName, IntegrationField[]> = {
	hubspot: [
		{ key: "portal_id", label: "Portal ID", placeholder: "12345678" },
		{ key: "access_token", label: "Private app token", placeholder: "pat-na1-...", type: "password" },
	],
	slack: [
		{ key: "bot_token", label: "Bot token", placeholder: "xoxb-...", type: "password" },
		{ key: "channel_id", label: "Channel ID", placeholder: "C01234567", help: "Used for launch alerts and approvals." },
	],
	ga4: [
		{ key: "property_id", label: "Property ID", placeholder: "123456789" },
		{ key: "service_account_json", label: "Service account JSON", placeholder: "Paste service account JSON", type: "password", help: "Stored server-side by the integration endpoint." },
	],
};

const TITLES: Record<IntegrationName, string> = {
	hubspot: "HubSpot credentials",
	slack: "Slack credentials",
	ga4: "GA4 credentials",
};

export default function IntegrationCredentialsDialog({
	busy,
	name,
	open,
	onOpenChange,
	onSubmit,
}: {
	busy: boolean;
	name: IntegrationName | null;
	open: boolean;
	onOpenChange: (open: boolean) => void;
	onSubmit: (name: IntegrationName, credentials: Record<string, string>) => Promise<void>;
}) {
	const fields = useMemo(() => (name ? FIELD_CONFIG[name] : []), [name]);
	const [values, setValues] = useState<Record<string, string>>({});
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		if (!open || !name) {
			setValues({});
			setError(null);
		}
	}, [name, open]);

	async function handleSubmit(formData: FormData): Promise<void> {
		if (!name) {
			return;
		}

		const nextValues = Object.fromEntries(
			fields.map((field) => [field.key, String(formData.get(field.key) ?? "").trim()]),
		);
		setValues(nextValues);

		if (Object.values(nextValues).some((value) => !value)) {
			setError("Complete every field before connecting the integration.");
			return;
		}

		setError(null);
		await onSubmit(name, nextValues);
		setValues({});
		setError(null);
		onOpenChange(false);
	}

	return (
		<Dialog.Root onOpenChange={onOpenChange} open={open}>
			<Dialog.Portal>
				<Dialog.Overlay className="dialog-overlay" />
				<Dialog.Content className="dialog-content">
					<Dialog.Title style={{ margin: 0 }}>{name ? TITLES[name] : "Integration credentials"}</Dialog.Title>
					<Dialog.Description style={{ color: "var(--muted)", margin: "0.5rem 0 1rem" }}>
						Connect the integration with the credentials LaunchIQ needs for agent workflows.
					</Dialog.Description>
					<form
						action={(formData) => {
							void handleSubmit(formData);
						}}
						style={{ display: "grid", gap: "0.9rem" }}
					>
						{fields.map((field) => (
							<label key={field.key} style={{ display: "grid", gap: "0.35rem" }}>
								<span>{field.label}</span>
								{field.key === "service_account_json" ? (
									<textarea defaultValue={values[field.key] ?? ""} name={field.key} placeholder={field.placeholder} rows={5} />
								) : (
									<input defaultValue={values[field.key] ?? ""} name={field.key} placeholder={field.placeholder} type={field.type ?? "text"} />
								)}
								{field.help ? <small style={{ color: "var(--muted)" }}>{field.help}</small> : null}
							</label>
						))}

						{error ? <p style={{ color: "var(--danger)", margin: 0 }}>{error}</p> : null}

						<div style={{ display: "flex", justifyContent: "flex-end", gap: "0.75rem" }}>
							<Dialog.Close asChild>
								<button className="btn btn-secondary" type="button">
									Cancel
								</button>
							</Dialog.Close>
							<button className="btn btn-primary" disabled={busy} type="submit">
								{busy ? "Connecting..." : "Connect"}
							</button>
						</div>
					</form>
				</Dialog.Content>
			</Dialog.Portal>
		</Dialog.Root>
	);
}
