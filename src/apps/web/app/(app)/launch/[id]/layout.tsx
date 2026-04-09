import Link from "next/link";
import type { Route } from "next";

export default async function LaunchLayout({
	children,
	params,
}: Readonly<{ children: React.ReactNode; params: Promise<{ id: string }> }>) {
	const { id } = await params;
	const base = `/launch/${id}`;

	return (
		<div style={{ display: "grid", gap: "1rem" }}>
			<nav className="panel" style={{ display: "flex", gap: "0.7rem", flexWrap: "wrap" }}>
				<Link href={`${base}/tracker` as Route}>Tracker</Link>
				<Link href={`${base}/brief` as Route}>Brief</Link>
				<Link href={`${base}/personas` as Route}>Personas</Link>
				<Link href={`${base}/strategy` as Route}>Strategy</Link>
				<Link href={`${base}/content` as Route}>Content</Link>
			</nav>
			{children}
		</div>
	);
}
