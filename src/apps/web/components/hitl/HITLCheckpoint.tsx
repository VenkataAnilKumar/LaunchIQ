"use client";

import dynamic from "next/dynamic";
import { useState } from "react";

import { resolveHITL } from "@/lib/api";
import { AGENT_LABEL } from "@/lib/format";
import type { HITLState } from "@/packages/types";

import HITLDecisionBar from "./HITLDecisionBar";
import ReviewPreview from "./ReviewPreview";

// The JSON-Schema form library is large; load it only when someone clicks Edit.
const HITLEditModal = dynamic(() => import("./HITLEditModal"), { ssr: false });

const CHECKPOINT_TITLE: Record<string, string> = {
	brief_review: "Review the market research",
	strategy_review: "Review the launch strategy",
	persona_review: "Review the personas",
	content_review: "Review the content",
};

interface Props {
	hitl: HITLState;
	onResolved: () => void;
}

export default function HITLCheckpoint({ hitl, onResolved }: Props) {
	const [busy, setBusy] = useState(false);
	const [showEdit, setShowEdit] = useState(false);
	const [comment, setComment] = useState("");
	const [error, setError] = useState<string | null>(null);

	async function decide(decision: "approve" | "reject", edits?: Record<string, unknown>): Promise<void> {
		setError(null);
		if (decision === "reject" && !window.confirm("Reject this launch? The pipeline will stop and cannot be resumed.")) {
			return;
		}
		setBusy(true);
		try {
			await resolveHITL(hitl.launch_id, decision, edits, hitl.checkpoint, comment.trim() || undefined);
			onResolved();
		} catch (decisionError) {
			setError(decisionError instanceof Error ? decisionError.message : "Decision failed");
			onResolved(); // refresh: the checkpoint may already have been decided elsewhere
		} finally {
			setBusy(false);
		}
	}

	async function submitEdits(edits: Record<string, unknown>): Promise<void> {
		await resolveHITL(hitl.launch_id, "edit", edits, hitl.checkpoint, comment.trim() || undefined);
		onResolved();
	}

	return (
		<>
			<section className="panel" data-testid="hitl-panel" style={{ display: "grid", gap: "0.9rem", borderColor: "#5b8de0" }}>
				<div>
					<h2 style={{ margin: 0 }}>{CHECKPOINT_TITLE[hitl.checkpoint] ?? "Human review required"}</h2>
					<p style={{ color: "var(--muted)", margin: "0.3rem 0 0" }}>
						Checkpoint <strong>{hitl.checkpoint}</strong> · output of <strong>{AGENT_LABEL[hitl.agent_id] ?? hitl.agent_id}</strong>.
						The pipeline is paused until you approve, edit or reject.
					</p>
				</div>

				<ReviewPreview agentId={hitl.agent_id} output={hitl.output_preview} />

				<div>
					<label htmlFor="review-comment">Comment (optional)</label>
					<textarea
						id="review-comment"
						onChange={(event) => setComment(event.target.value)}
						placeholder="Why you approved, changed or rejected this"
						rows={2}
						style={{ marginTop: "0.35rem" }}
						value={comment}
					/>
				</div>

				{error ? <p className="field-error" role="alert">{error}</p> : null}

				<HITLDecisionBar
					busy={busy}
					onApprove={() => decide("approve")}
					onEdit={() => setShowEdit(true)}
					onReject={() => decide("reject")}
				/>
			</section>

			<HITLEditModal
				agentId={hitl.agent_id}
				initialValue={hitl.output_preview}
				onClose={() => setShowEdit(false)}
				onConfirm={submitEdits}
				open={showEdit}
			/>
		</>
	);
}
