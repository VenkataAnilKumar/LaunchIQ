"use client";

import { useEffect, useState } from "react";

interface Props {
	open: boolean;
	initialValue: Record<string, unknown>;
	onClose: () => void;
	onConfirm: (edits: Record<string, unknown>) => Promise<void>;
}

export default function HITLEditModal({ open, initialValue, onClose, onConfirm }: Props) {
	const [raw, setRaw] = useState("{}");
	const [error, setError] = useState<string | null>(null);
	const [isSubmitting, setIsSubmitting] = useState(false);

	useEffect(() => {
		setRaw(JSON.stringify(initialValue, null, 2));
	}, [initialValue]);

	if (!open) {
		return null;
	}

	async function submit(): Promise<void> {
		setError(null);
		try {
			const parsed = JSON.parse(raw) as Record<string, unknown>;
			setIsSubmitting(true);
			await onConfirm(parsed);
			onClose();
		} catch (parseError) {
			setError(parseError instanceof Error ? parseError.message : "Invalid JSON");
		} finally {
			setIsSubmitting(false);
		}
	}

	return (
		<div
			style={{
				position: "fixed",
				inset: 0,
				background: "rgba(0,0,0,0.5)",
				display: "grid",
				placeItems: "center",
				zIndex: 70,
			}}
		>
			<div className="panel" style={{ width: "min(860px, 92vw)" }}>
				<h3 style={{ marginTop: 0 }}>Edit Agent Output</h3>
				<label htmlFor="hitl-edit-json" style={{ display: "block", marginBottom: "0.4rem", color: "var(--muted)" }}>
					Agent output JSON
				</label>
				<textarea
					id="hitl-edit-json"
					rows={14}
					value={raw}
					onChange={(event) => setRaw(event.target.value)}
					style={{ width: "100%", fontFamily: "ui-monospace, Menlo, monospace" }}
				/>
				{error ? <p style={{ color: "var(--danger)", marginBottom: 0 }}>{error}</p> : null}
				<div style={{ marginTop: "0.8rem", display: "flex", gap: "0.5rem", justifyContent: "flex-end" }}>
					<button className="btn btn-secondary" onClick={onClose} type="button">
						Cancel
					</button>
					<button className="btn btn-primary" disabled={isSubmitting} onClick={submit} type="button">
						{isSubmitting ? "Submitting..." : "Submit edits"}
					</button>
				</div>
			</div>
		</div>
	);
}
