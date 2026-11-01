"use client";

export default function GlobalError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
	return (
		<div className="page-shell">
			<section className="panel" role="alert" style={{ display: "grid", gap: "0.6rem" }}>
				<h1 style={{ margin: 0 }}>Something went wrong</h1>
				<p style={{ margin: 0, color: "var(--muted)" }}>{error.message || "An unexpected error occurred."}</p>
				<div>
					<button className="btn btn-primary" onClick={reset} type="button">Try again</button>
				</div>
			</section>
		</div>
	);
}
