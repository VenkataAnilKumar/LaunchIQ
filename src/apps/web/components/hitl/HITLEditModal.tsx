"use client";

import Form from "@rjsf/core";
import type { RJSFSchema } from "@rjsf/utils";
import validator from "@rjsf/validator-ajv8";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import { getAgentSchema } from "@/lib/api";
import { pruneEmpty, simplifySchema, stripModelTitles } from "@/lib/schema";

interface Props {
	open: boolean;
	agentId: string;
	initialValue: Record<string, unknown>;
	onClose: () => void;
	onConfirm: (edits: Record<string, unknown>) => Promise<void>;
}

/** Edit form generated from the agent's own output schema, so it can only produce valid output. */
export default function HITLEditModal({ open, agentId, initialValue, onClose, onConfirm }: Props) {
	const [data, setData] = useState<Record<string, unknown>>(initialValue);
	const [error, setError] = useState<string | null>(null);
	const [saving, setSaving] = useState(false);

	const schemaQuery = useQuery({
		queryKey: ["agent-schema", agentId],
		queryFn: async () => stripModelTitles(simplifySchema(await getAgentSchema(agentId))) as RJSFSchema,
		enabled: open,
		staleTime: Infinity,
	});

	useEffect(() => {
		setData(initialValue);
	}, [initialValue]);

	useEffect(() => {
		if (!open) {
			return undefined;
		}
		const onKey = (event: KeyboardEvent) => {
			if (event.key === "Escape") {
				onClose();
			}
		};
		window.addEventListener("keydown", onKey);
		return () => window.removeEventListener("keydown", onKey);
	}, [open, onClose]);

	if (!open) {
		return null;
	}

	async function submit(formData: Record<string, unknown>): Promise<void> {
		setError(null);
		setSaving(true);
		try {
			await onConfirm(pruneEmpty(formData));
			onClose();
		} catch (submitError) {
			setError(submitError instanceof Error ? submitError.message : "Could not save your edits");
		} finally {
			setSaving(false);
		}
	}

	return (
		<div
			aria-labelledby="edit-title"
			aria-modal="true"
			role="dialog"
			style={{ position: "fixed", inset: 0, background: "rgba(20,33,24,0.5)", display: "grid", placeItems: "center", zIndex: 70, padding: "1rem" }}
		>
			<div className="panel" style={{ width: "min(900px, 96vw)", maxHeight: "90vh", overflow: "auto" }}>
				<h3 id="edit-title" style={{ marginTop: 0 }}>Edit the agent&apos;s output</h3>
				<p style={{ color: "var(--muted)", marginTop: 0 }}>
					Your changes are checked against the same rules the agent follows. Later agents will use your edited version.
				</p>
				{schemaQuery.isLoading ? <p aria-busy="true">Loading form…</p> : null}
				{schemaQuery.error ? (
					<p className="field-error" role="alert">Could not load the edit form. Close this and try again.</p>
				) : null}
				{schemaQuery.data ? (
					<div className="rjsf" data-testid="edit-form">
						<Form
							formData={data}
							noHtml5Validate
							onChange={(event) => setData((event.formData ?? {}) as Record<string, unknown>)}
							onSubmit={({ formData }) => void submit((formData ?? {}) as Record<string, unknown>)}
							schema={schemaQuery.data}
							showErrorList={false}
							uiSchema={{ "ui:submitButtonOptions": { norender: true } }}
							validator={validator}
						>
							{error ? <p className="field-error" role="alert">{error}</p> : null}
							<div style={{ display: "flex", gap: "0.5rem", justifyContent: "flex-end", marginTop: "0.8rem" }}>
								<button className="btn btn-secondary" onClick={onClose} type="button">Cancel</button>
								<button className="btn btn-primary" disabled={saving} type="submit">
									{saving ? "Submitting..." : "Submit edits"}
								</button>
							</div>
						</Form>
					</div>
				) : null}
			</div>
		</div>
	);
}
