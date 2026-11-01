import Link from "next/link";

export default function NotFound() {
	return (
		<div className="page-shell">
			<section className="panel" style={{ display: "grid", gap: "0.6rem" }}>
				<h1 style={{ margin: 0 }}>Page not found</h1>
				<p style={{ margin: 0, color: "var(--muted)" }}>That page does not exist, or it belongs to another account.</p>
				<div>
					<Link className="btn btn-primary" href="/dashboard">Back to dashboard</Link>
				</div>
			</section>
		</div>
	);
}
