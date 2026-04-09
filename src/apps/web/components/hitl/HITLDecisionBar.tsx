"use client";

interface Props {
	busy: boolean;
	onApprove: () => Promise<void>;
	onEdit: () => void;
	onReject: () => Promise<void>;
}

export default function HITLDecisionBar({ busy, onApprove, onEdit, onReject }: Props) {
	return (
		<div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
			<button className="btn btn-primary" disabled={busy} onClick={onApprove} type="button">
				Approve
			</button>
			<button className="btn btn-secondary" disabled={busy} onClick={onEdit} type="button">
				Edit
			</button>
			<button
				className="btn"
				disabled={busy}
				onClick={onReject}
				style={{ background: "var(--danger)", color: "white" }}
				type="button"
			>
				Reject
			</button>
		</div>
	);
}
