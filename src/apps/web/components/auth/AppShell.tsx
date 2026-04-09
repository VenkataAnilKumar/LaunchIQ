"use client";

import { RedirectToSignIn, UserButton } from "@clerk/nextjs";
import Link from "next/link";

import { useSession } from "@/components/auth/SessionProvider";

export default function AppShell({ children }: Readonly<{ children: React.ReactNode }>) {
	const { isLoaded, session } = useSession();
	const hasClerkConfig = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);

	if (!isLoaded) {
		return (
			<div className="page-shell" style={{ display: "grid", gap: "1rem" }}>
				<section className="panel">
					<h1 style={{ margin: 0 }}>Preparing LaunchIQ</h1>
					<p style={{ margin: "0.4rem 0 0", color: "var(--muted)" }}>Checking your Clerk session.</p>
				</section>
			</div>
		);
	}

	if (!session) {
		if (!hasClerkConfig) {
			return (
				<div className="page-shell" style={{ display: "grid", gap: "1rem" }}>
					<section className="panel">
						<h1 style={{ margin: 0 }}>Clerk Configuration Required</h1>
						<p style={{ margin: "0.4rem 0 0", color: "var(--muted)" }}>
							Set NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY and CLERK_SECRET_KEY to access protected routes.
						</p>
					</section>
				</div>
			);
		}
		return <RedirectToSignIn redirectUrl="/sign-in" />;
	}

	return (
		<div className="page-shell" style={{ display: "grid", gap: "1rem" }}>
			<header className="panel" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "1rem", flexWrap: "wrap" }}>
				<div style={{ display: "grid", gap: "0.2rem" }}>
					<strong>LaunchIQ</strong>
					<div style={{ display: "flex", gap: "0.5rem", alignItems: "center", flexWrap: "wrap", color: "var(--muted)" }}>
						<span>{session.label}</span>
						<span className="status-pill status-running">
							{session.source}
						</span>
					</div>
				</div>
				<nav style={{ display: "flex", gap: "0.7rem", alignItems: "center", flexWrap: "wrap" }}>
					<Link href="/dashboard">Dashboard</Link>
					<Link href="/launch/new">New Launch</Link>
					<Link href="/settings">Settings</Link>
					<UserButton afterSignOutUrl="/sign-in" />
				</nav>
			</header>
			{children}
		</div>
	);
}
