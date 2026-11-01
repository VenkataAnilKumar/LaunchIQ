"use client";

import { useAuth, useUser } from "@clerk/nextjs";
import { createContext, useContext, useEffect, useMemo } from "react";

import { setAccessTokenProvider } from "@/lib/api";

export interface SessionUser {
	id: string;
	label: string;
	email: string | null;
	source: "clerk" | "dev";
}

interface SessionContextValue {
	session: SessionUser | null;
	isLoaded: boolean;
	signOut: () => Promise<void>;
}

const SessionContext = createContext<SessionContextValue | null>(null);

const DEFAULT_CONTEXT: SessionContextValue = {
	session: null,
	isLoaded: true,
	signOut: async () => undefined,
};

function ClerkBackedSessionProvider({ children }: { children: React.ReactNode }) {
	const { getToken, isLoaded, signOut: clerkSignOut, userId } = useAuth();
	const { user } = useUser();
	const tokenTemplate = process.env.NEXT_PUBLIC_CLERK_JWT_TEMPLATE;

	useEffect(() => {
		setAccessTokenProvider(async () => {
			const token = await getToken(
				tokenTemplate ? { template: tokenTemplate } : undefined,
			);
			return token ?? null;
		});

		return () => {
			setAccessTokenProvider(null);
		};
	}, [getToken, tokenTemplate]);

	const session = useMemo<SessionUser | null>(() => {
		if (!userId) {
			return null;
		}
		const displayName =
			user?.fullName || user?.primaryEmailAddress?.emailAddress || user?.username || userId;
		return {
			id: userId,
			label: displayName,
			email: user?.primaryEmailAddress?.emailAddress ?? null,
			source: "clerk",
		};
	}, [user, userId]);

	const value = useMemo<SessionContextValue>(
		() => ({
			session,
			isLoaded,
			signOut: () => clerkSignOut({ redirectUrl: "/sign-in" }),
		}),
		[clerkSignOut, isLoaded, session],
	);

	return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

// Keyless local development: a dev bearer token stands in for a Clerk session. The API only
// accepts unsigned tokens outside production, so this has no effect on deployed environments.
function devSessionFromToken(token: string | undefined): SessionUser | null {
	if (!token) {
		return null;
	}
	try {
		const payload = JSON.parse(atob(token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/")));
		const id = typeof payload.sub === "string" && payload.sub ? payload.sub : "local-dev-user";
		return { id, label: `Local dev (${id})`, email: null, source: "dev" };
	} catch {
		return null;
	}
}

export function SessionProvider({ children }: { children: React.ReactNode }) {
	const hasClerkConfig = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);
	const devSession = useMemo(() => devSessionFromToken(process.env.NEXT_PUBLIC_DEV_BEARER_TOKEN), []);
	const devValue = useMemo<SessionContextValue>(
		() => ({ session: devSession, isLoaded: true, signOut: async () => undefined }),
		[devSession],
	);

	useEffect(() => {
		if (!hasClerkConfig) {
			setAccessTokenProvider(null);
		}
	}, [hasClerkConfig]);

	if (!hasClerkConfig) {
		return (
			<SessionContext.Provider value={devSession ? devValue : DEFAULT_CONTEXT}>
				{children}
			</SessionContext.Provider>
		);
	}

	return <ClerkBackedSessionProvider>{children}</ClerkBackedSessionProvider>;
}

export function useSession(): SessionContextValue {
	const context = useContext(SessionContext);
	if (!context) {
		throw new Error("useSession must be used within SessionProvider");
	}
	return context;
}
