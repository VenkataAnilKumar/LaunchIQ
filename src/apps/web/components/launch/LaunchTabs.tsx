"use client";

import Link from "next/link";
import type { Route } from "next";
import { usePathname } from "next/navigation";

const TABS = [
	{ slug: "tracker", label: "Progress" },
	{ slug: "brief", label: "Market" },
	{ slug: "personas", label: "Personas" },
	{ slug: "strategy", label: "Strategy" },
	{ slug: "content", label: "Content" },
	{ slug: "document", label: "Document" },
	{ slug: "analytics", label: "Analytics" },
];

export default function LaunchTabs({ launchId }: { launchId: string }) {
	const pathname = usePathname();
	return (
		<nav aria-label="Launch sections" className="tabs panel">
			{TABS.map((tab) => {
				const href = `/launch/${launchId}/${tab.slug}`;
				const active = pathname === href;
				return (
					<Link aria-current={active ? "page" : undefined} className="tab" href={href as Route} key={tab.slug}>
						{tab.label}
					</Link>
				);
			})}
		</nav>
	);
}
