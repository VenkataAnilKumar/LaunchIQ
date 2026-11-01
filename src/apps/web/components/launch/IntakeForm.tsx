"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { createLaunch, rememberLaunchId } from "@/lib/api";
import { SAMPLE_BRIEFS } from "@/lib/samples";

// Mirrors the API's validation so errors show before a round trip.
const LIMITS = { name: 255, description: 5000, market: 255, competitors: 10, minDescription: 10 };

export default function IntakeForm() {
	const router = useRouter();
	const searchParams = useSearchParams();
	const [productName, setProductName] = useState("");
	const [description, setDescription] = useState("");
	const [targetMarket, setTargetMarket] = useState("");
	const [competitorInput, setCompetitorInput] = useState("");
	const [competitors, setCompetitors] = useState<string[]>([]);
	const [sample, setSample] = useState<number | null>(null);
	const [touched, setTouched] = useState(false);
	const [isSaving, setIsSaving] = useState(false);
	const [error, setError] = useState<string | null>(null);

	function applySample(index: number): void {
		const brief = SAMPLE_BRIEFS[index];
		setProductName(brief.product_name);
		setDescription(brief.description);
		setTargetMarket(brief.target_market);
		setCompetitors(brief.competitors);
		setSample(index);
		setTouched(false);
	}

	useEffect(() => {
		const fromUrl = searchParams.get("sample");
		if (fromUrl !== null && SAMPLE_BRIEFS[Number(fromUrl)]) {
			applySample(Number(fromUrl));
		}
	}, [searchParams]);

	const problems = useMemo(() => {
		const list: Record<string, string> = {};
		if (!productName.trim()) list.name = "Enter a product name.";
		if (description.trim().length < LIMITS.minDescription) list.description = `Describe it in at least ${LIMITS.minDescription} characters.`;
		if (!targetMarket.trim()) list.market = "Who is it for?";
		return list;
	}, [description, productName, targetMarket]);

	const valid = Object.keys(problems).length === 0;

	function addCompetitor(): void {
		const normalized = competitorInput.trim();
		setCompetitorInput("");
		if (!normalized || competitors.includes(normalized) || competitors.length >= LIMITS.competitors) {
			return;
		}
		setCompetitors((prev) => [...prev, normalized]);
	}

	async function onSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
		event.preventDefault();
		setTouched(true);
		if (!valid || isSaving) {
			return;
		}
		setError(null);
		setIsSaving(true);
		try {
			const launch = await createLaunch({
				product_name: productName.trim(),
				description: description.trim(),
				target_market: targetMarket.trim(),
				competitors,
			});
			rememberLaunchId(launch.launch_id);
			router.push(`/launch/${launch.launch_id}/tracker`);
		} catch (submitError) {
			setError(submitError instanceof Error ? submitError.message : "Failed to create launch");
			setIsSaving(false);
		}
	}

	return (
		<form className="panel" noValidate onSubmit={onSubmit} style={{ display: "grid", gap: "1rem" }}>
			<div>
				<strong>Try an example</strong>
				<div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap", marginTop: "0.4rem" }}>
					{SAMPLE_BRIEFS.map((brief, index) => (
						<button aria-pressed={sample === index} className="chip" key={brief.label} onClick={() => applySample(index)} type="button">
							{brief.label}
						</button>
					))}
				</div>
			</div>

			<div>
				<label htmlFor="product-name">Product name</label>
				<input
					aria-describedby={touched && problems.name ? "name-error" : undefined}
					aria-invalid={touched && Boolean(problems.name)}
					id="product-name"
					maxLength={LIMITS.name}
					onChange={(event) => setProductName(event.target.value)}
					placeholder="LaunchIQ Copilot"
					style={{ marginTop: "0.35rem" }}
					value={productName}
				/>
				{touched && problems.name ? <p className="field-error" id="name-error">{problems.name}</p> : null}
			</div>

			<div>
				<label htmlFor="description">Description</label>
				<textarea
					aria-describedby={touched && problems.description ? "description-error" : "description-hint"}
					aria-invalid={touched && Boolean(problems.description)}
					id="description"
					maxLength={LIMITS.description}
					onChange={(event) => setDescription(event.target.value)}
					placeholder="What are you launching and why now?"
					rows={4}
					style={{ marginTop: "0.35rem" }}
					value={description}
				/>
				{touched && problems.description ? (
					<p className="field-error" id="description-error">{problems.description}</p>
				) : (
					<p className="field-hint" id="description-hint">
						{description.length}/{LIMITS.description}. The more specific, the better the research.
					</p>
				)}
			</div>

			<div>
				<label htmlFor="target-market">Target market</label>
				<input
					aria-describedby={touched && problems.market ? "market-error" : undefined}
					aria-invalid={touched && Boolean(problems.market)}
					id="target-market"
					maxLength={LIMITS.market}
					onChange={(event) => setTargetMarket(event.target.value)}
					placeholder="B2B SaaS founders in North America"
					style={{ marginTop: "0.35rem" }}
					value={targetMarket}
				/>
				{touched && problems.market ? <p className="field-error" id="market-error">{problems.market}</p> : null}
			</div>

			<div>
				<label htmlFor="competitor-input">Competitors <span style={{ color: "var(--muted)", fontWeight: 400 }}>(optional, up to {LIMITS.competitors})</span></label>
				<div style={{ display: "flex", gap: "0.5rem", marginTop: "0.35rem" }}>
					<input
						id="competitor-input"
						onChange={(event) => setCompetitorInput(event.target.value)}
						onKeyDown={(event) => {
							if (event.key === "Enter") {
								event.preventDefault();
								addCompetitor();
							}
						}}
						placeholder="Add competitor"
						style={{ flex: 1 }}
						value={competitorInput}
					/>
					<button className="btn btn-secondary" onClick={addCompetitor} type="button">
						Add
					</button>
				</div>
				<div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", marginTop: "0.5rem" }}>
					{competitors.map((name) => (
						<button
							aria-label={`Remove ${name}`}
							className="chip"
							key={name}
							onClick={() => setCompetitors((prev) => prev.filter((item) => item !== name))}
							type="button"
						>
							{name} ×
						</button>
					))}
				</div>
			</div>

			{error ? <p className="field-error" role="alert">{error}</p> : null}

			<div style={{ display: "flex", gap: "0.8rem", alignItems: "center", flexWrap: "wrap" }}>
				<button className="btn btn-primary" disabled={isSaving} type="submit">
					{isSaving ? "Creating launch..." : "Create launch"}
				</button>
				<span className="field-hint">You will review the results at two checkpoints before content is written.</span>
			</div>
		</form>
	);
}
