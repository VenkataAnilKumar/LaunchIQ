import LaunchTabs from "@/components/launch/LaunchTabs";

export default async function LaunchLayout({
	children,
	params,
}: Readonly<{ children: React.ReactNode; params: Promise<{ id: string }> }>) {
	const { id } = await params;

	return (
		<div style={{ display: "grid", gap: "1rem" }}>
			<LaunchTabs launchId={id} />
			{children}
		</div>
	);
}
