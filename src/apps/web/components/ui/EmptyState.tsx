import Link from "next/link";
import type { Route } from "next";

export default function EmptyState({
	title,
	description,
	action,
}: {
	title: string;
	description: string;
	action?: { label: string; href: Route };
}) {
	return (
		<section className="panel" style={{ textAlign: "center", padding: "2rem 1rem" }}>
			<h2 style={{ marginTop: 0 }}>{title}</h2>
			<p style={{ color: "var(--muted)", maxWidth: "40rem", margin: "0 auto" }}>{description}</p>
			{action ? (
				<div style={{ marginTop: "1rem" }}>
					<Link className="btn btn-primary" href={action.href}>
						{action.label}
					</Link>
				</div>
			) : null}
		</section>
	);
}