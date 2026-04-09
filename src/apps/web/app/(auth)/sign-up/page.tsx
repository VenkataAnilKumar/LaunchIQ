import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
	const hasClerkConfig = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);

	if (!hasClerkConfig) {
		return (
			<main className="page-shell" style={{ display: "grid", gap: "1rem", minHeight: "80vh", alignContent: "center" }}>
				<section className="panel">
					<h1 style={{ margin: 0 }}>Clerk Configuration Required</h1>
					<p style={{ margin: "0.5rem 0 0", color: "var(--muted)" }}>
						Set NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY and CLERK_SECRET_KEY to enable account signup.
					</p>
				</section>
			</main>
		);
	}

	return (
		<main className="page-shell" style={{ display: "grid", placeItems: "center", minHeight: "80vh" }}>
			<SignUp fallbackRedirectUrl="/dashboard" signInUrl="/sign-in" />
		</main>
	);
}
