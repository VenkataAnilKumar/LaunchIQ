"use client";

import { useState } from "react";

import { resolveHITL } from "@/lib/api";
import type { HITLState } from "@/packages/types";

import HITLDecisionBar from "./HITLDecisionBar";
import HITLEditModal from "./HITLEditModal";

interface Props {
	hitl: HITLState;
	onResolved: () => void;
}

export default function HITLCheckpoint({ hitl, onResolved }: Props) {
	const [busy, setBusy] = useState(false);
	const [showEdit, setShowEdit] = useState(false);
	const [error, setError] = useState<string | null>(null);

	async function decide(decision: "approve" | "reject", edits?: Record<string, unknown>): Promise<void> {
		setError(null);
		setBusy(true);
		try {
			await resolveHITL(hitl.launch_id, decision, edits);
			onResolved();
		} catch (decisionError) {
			setError(decisionError instanceof Error ? decisionError.message : "Decision failed");
		} finally {
			setBusy(false);
		}
	}

	async function submitEdits(edits: Record<string, unknown>): Promise<void> {
		setError(null);
		setBusy(true);
		try {
			await resolveHITL(hitl.launch_id, "edit", edits);
			onResolved();
		} catch (decisionError) {
			setError(decisionError instanceof Error ? decisionError.message : "Edit submission failed");
		} finally {
			setBusy(false);
		}
	}

	return (
		<>
			<div
				style={{
					position: "fixed",
					inset: 0,
					zIndex: 60,
					background: "rgba(20, 33, 24, 0.45)",
					backdropFilter: "blur(2px)",
					display: "grid",
					placeItems: "center",
					padding: "1rem",
				}}
			>
				<section className="panel" style={{ width: "min(960px, 96vw)" }}>
					<h2 style={{ marginTop: 0 }}>Human Review Required</h2>
					<p style={{ color: "var(--muted)" }}>
						Checkpoint: <strong>{hitl.checkpoint}</strong> | Agent: <strong>{hitl.agent_id}</strong>
					</p>

					<pre
						style={{
							maxHeight: "40vh",
							overflow: "auto",
							background: "#f2f6f1",
							border: "1px solid var(--line)",
							padding: "0.8rem",
							borderRadius: "0.7rem",
						}}
					>
						{JSON.stringify(hitl.output_preview, null, 2)}
					</pre>

					{error ? <p style={{ color: "var(--danger)" }}>{error}</p> : null}

					<HITLDecisionBar
						busy={busy}
						onApprove={() => decide("approve")}
						onEdit={() => setShowEdit(true)}
						onReject={() => decide("reject")}
					/>
				</section>
			</div>

			<HITLEditModal
				initialValue={hitl.output_preview}
				onClose={() => setShowEdit(false)}
				onConfirm={submitEdits}
				open={showEdit}
			/>
		</>
	);
}
