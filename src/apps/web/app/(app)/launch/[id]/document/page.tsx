"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { PageSkeleton } from "@/components/ui/Skeleton";
import { downloadLaunchBrief, getLaunchDocument } from "@/lib/api";
import { useLaunch } from "@/lib/useLaunch";

export default function LaunchDocumentPage() {
	const { id } = useParams<{ id: string }>();
	const launch = useLaunch(id);
	const ready = Boolean(launch.data?.export_ready);
	const doc = useQuery({ queryKey: ["document", id], queryFn: () => getLaunchDocument(id), enabled: ready });
	const [note, setNote] = useState<string | null>(null);

	if (launch.isLoading || (ready && doc.isLoading)) {
		return <PageSkeleton />;
	}
	if (!ready || !doc.data) {
		return (
			<section className="panel" style={{ textAlign: "center", padding: "2rem 1rem" }}>
				<h2 style={{ marginTop: 0 }}>The launch document is not ready yet</h2>
				<p style={{ color: "var(--muted)", marginBottom: 0 }}>
					It combines market research, personas, strategy and content into one document once the launch is completed.
				</p>
			</section>
		);
	}

	async function copy(): Promise<void> {
		await navigator.clipboard.writeText(doc.data?.markdown ?? "");
		setNote("Copied to clipboard");
		setTimeout(() => setNote(null), 1800);
	}

	return (
		<section style={{ display: "grid", gap: "1rem" }}>
			<div className="panel" style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap", alignItems: "center" }}>
				<button className="btn btn-primary" onClick={() => void downloadLaunchBrief(id, doc.data.product_name)} type="button">
					Download .md
				</button>
				<button className="btn btn-secondary" onClick={() => void copy()} type="button">
					Copy Markdown
				</button>
				{note ? <span role="status" style={{ color: "var(--muted)" }}>{note}</span> : null}
			</div>
			<article className="panel prose" data-testid="launch-document">
				<ReactMarkdown remarkPlugins={[remarkGfm]}>{doc.data.markdown}</ReactMarkdown>
			</article>
		</section>
	);
}
