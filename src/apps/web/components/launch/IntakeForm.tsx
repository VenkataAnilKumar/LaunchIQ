"use client";

import { FormEvent, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { createLaunch, rememberLaunchId } from "@/lib/api";

export default function IntakeForm() {
	const router = useRouter();
	const [productName, setProductName] = useState("");
	const [description, setDescription] = useState("");
	const [targetMarket, setTargetMarket] = useState("");
	const [competitorInput, setCompetitorInput] = useState("");
	const [competitors, setCompetitors] = useState<string[]>([]);
	const [isSaving, setIsSaving] = useState(false);
	const [error, setError] = useState<string | null>(null);

	const canSubmit = useMemo(
		() => productName.trim() && description.trim() && targetMarket.trim() && !isSaving,
		[description, isSaving, productName, targetMarket],
	);

	function addCompetitor(): void {
		const normalized = competitorInput.trim();
		if (!normalized || competitors.includes(normalized)) {
			setCompetitorInput("");
			return;
		}
		setCompetitors((prev) => [...prev, normalized]);
		setCompetitorInput("");
	}

	function removeCompetitor(name: string): void {
		setCompetitors((prev) => prev.filter((item) => item !== name));
	}

	async function onSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
		event.preventDefault();
		if (!canSubmit) {
			return;
		}

		setError(null);
		setIsSaving(true);
		try {
			const launch = await createLaunch({
				product_name: productName,
				description,
				target_market: targetMarket,
				competitors,
			});
			rememberLaunchId(launch.launch_id);
			router.push(`/launch/${launch.launch_id}/tracker`);
		} catch (submitError) {
			setError(submitError instanceof Error ? submitError.message : "Failed to create launch");
		} finally {
			setIsSaving(false);
		}
	}

	return (
		<form className="panel" onSubmit={onSubmit} style={{ display: "grid", gap: "0.9rem" }}>
			<h2 style={{ margin: 0, fontSize: "1.25rem" }}>New Launch Brief</h2>

			<label>
				Product name
				<input
					value={productName}
					onChange={(event) => setProductName(event.target.value)}
					placeholder="LaunchIQ Copilot"
					style={{ width: "100%", marginTop: "0.35rem" }}
				/>
			</label>

			<label>
				Description
				<textarea
					value={description}
					onChange={(event) => setDescription(event.target.value)}
					placeholder="What are you launching and why now?"
					rows={4}
					style={{ width: "100%", marginTop: "0.35rem" }}
				/>
			</label>

			<label>
				Target market
				<input
					value={targetMarket}
					onChange={(event) => setTargetMarket(event.target.value)}
					placeholder="B2B SaaS founders in North America"
					style={{ width: "100%", marginTop: "0.35rem" }}
				/>
			</label>

			<div>
				<label>
					Competitors
					<div style={{ display: "flex", gap: "0.5rem", marginTop: "0.35rem" }}>
						<input
							value={competitorInput}
							onChange={(event) => setCompetitorInput(event.target.value)}
							placeholder="Add competitor"
							style={{ flex: 1 }}
						/>
						<button className="btn btn-secondary" onClick={addCompetitor} type="button">
							Add
						</button>
					</div>
				</label>
				<div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", marginTop: "0.5rem" }}>
					{competitors.map((name) => (
						<button className="btn btn-secondary" key={name} onClick={() => removeCompetitor(name)} type="button">
							{name} x
						</button>
					))}
				</div>
			</div>

			{error ? <p style={{ color: "var(--danger)", margin: 0 }}>{error}</p> : null}

			<button className="btn btn-primary" disabled={!canSubmit} type="submit">
				{isSaving ? "Creating launch..." : "Create launch"}
			</button>
		</form>
	);
}
