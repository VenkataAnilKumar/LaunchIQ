"use client";

import { RedirectToSignIn, UserButton } from "@clerk/nextjs";
import Link from "next/link";
import type { Route } from "next";
import { usePathname } from "next/navigation";

import { useSession } from "@/components/auth/SessionProvider";

const NAV: Array<{ href: string; label: string }> = [
	{ href: "/dashboard", label: "Dashboard" },
	{ href: "/launch/new", label: "New launch" },
	{ href: "/settings", label: "Settings" },
];

export default function AppShell({ children }: Readonly<{ children: React.ReactNode }>) {
	const { isLoaded, session } = useSession();
	const pathname = usePathname();
	const hasClerkConfig = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);

	if (!isLoaded) {
		return (
			<div className="page-shell">
				<section className="panel" aria-busy="true">
					<h1 style={{ margin: 0 }}>Preparing LaunchIQ</h1>
					<p style={{ margin: "0.4rem 0 0", color: "var(--muted)" }}>Checking your session.</p>
				</section>
			</div>
		);
	}

	if (!session) {
		if (!hasClerkConfig) {
			return (
				<div className="page-shell">
					<section className="panel">
						<h1 style={{ margin: 0 }}>Sign-in is not configured</h1>
						<p style={{ margin: "0.4rem 0 0", color: "var(--muted)" }}>
							Set NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY and CLERK_SECRET_KEY to enable sign-in, or set
							NEXT_PUBLIC_DEV_BEARER_TOKEN for keyless local development.
						</p>
					</section>
				</div>
			);
		}
		return <RedirectToSignIn redirectUrl="/sign-in" />;
	}

	return (
		<div className="page-shell" style={{ display: "grid", gap: "1rem" }}>
			<header
				className="panel"
				style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "0.8rem 1.5rem", flexWrap: "wrap" }}
			>
				<Link href="/dashboard" style={{ display: "grid", gap: "0.1rem" }}>
					<strong style={{ fontSize: "1.15rem" }}>LaunchIQ</strong>
					<span style={{ color: "var(--muted)", fontSize: "0.82rem" }}>
						{session.label} {session.source === "dev" ? <span className="status-pill status-running">dev</span> : null}
					</span>
				</Link>
				<nav aria-label="Main" style={{ display: "flex", gap: "0.25rem", alignItems: "center", flexWrap: "wrap" }}>
					{NAV.map((item) => {
						const active = pathname === item.href || (item.href === "/dashboard" && pathname.startsWith("/launch/") && pathname !== "/launch/new");
						return (
							<Link aria-current={active ? "page" : undefined} className="tab" href={item.href as Route} key={item.href}>
								{item.label}
							</Link>
						);
					})}
					{hasClerkConfig ? <UserButton afterSignOutUrl="/sign-in" /> : null}
				</nav>
			</header>
			<div id="main">{children}</div>
		</div>
	);
}
