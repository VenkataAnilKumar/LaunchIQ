import { Suspense } from "react";

import IntakeForm from "@/components/launch/IntakeForm";
import { PageSkeleton } from "@/components/ui/Skeleton";

export default function NewLaunchPage() {
	return (
		<main style={{ display: "grid", gap: "1rem" }}>
			<section>
				<h1 style={{ marginBottom: "0.2rem" }}>Start a new launch</h1>
				<p style={{ marginTop: 0, color: "var(--muted)" }}>
					Describe your product. Four agents research the market, build personas, plan the launch and draft the content,
					and you review the work at two checkpoints.
				</p>
			</section>
			<Suspense fallback={<PageSkeleton />}>
				<IntakeForm />
			</Suspense>
		</main>
	);
}
