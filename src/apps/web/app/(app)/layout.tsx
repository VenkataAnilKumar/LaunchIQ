import AppShell from "@/components/auth/AppShell";

export default function AppLayout({ children }: Readonly<{ children: React.ReactNode }>) {
	return <AppShell>{children}</AppShell>;
}
