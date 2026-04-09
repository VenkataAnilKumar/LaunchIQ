import IntakeForm from "@/components/launch/IntakeForm";

export default function NewLaunchPage() {
	return (
		<main style={{ display: "grid", gap: "1rem" }}>
			<section>
				<h1 style={{ marginBottom: "0.2rem" }}>Start a New Launch</h1>
				<p style={{ marginTop: 0, color: "var(--muted)" }}>
					Submit your brief to trigger the multi-agent pipeline.
				</p>
			</section>
			<IntakeForm />
		</main>
	);
}
