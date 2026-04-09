import { SignIn } from "@clerk/nextjs";

export default async function SignInPage({
	searchParams,
}: {
	searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
	const params = await searchParams;
	const nextPath = typeof params.next === "string" ? params.next : "/dashboard";
	const hasClerkConfig = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);

	if (!hasClerkConfig) {
		return (
			<main className="page-shell" style={{ display: "grid", gap: "1rem", minHeight: "80vh", alignContent: "center" }}>
				<section className="panel">
					<h1 style={{ margin: 0 }}>Clerk Configuration Required</h1>
					<p style={{ margin: "0.5rem 0 0", color: "var(--muted)" }}>
						Set NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY and CLERK_SECRET_KEY to enable sign-in.
					</p>
				</section>
			</main>
		);
	}

	return (
		<main className="page-shell" style={{ display: "grid", placeItems: "center", minHeight: "80vh" }}>
			<SignIn fallbackRedirectUrl={nextPath} signUpUrl="/sign-up" />
		</main>
	);
}
