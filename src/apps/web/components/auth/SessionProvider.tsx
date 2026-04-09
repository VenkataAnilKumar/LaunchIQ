"use client";

import { useAuth, useUser } from "@clerk/nextjs";
import { createContext, useContext, useEffect, useMemo } from "react";

import { setAccessTokenProvider } from "@/lib/api";

export interface SessionUser {
	id: string;
	label: string;
	email: string | null;
	source: "clerk";
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

export function SessionProvider({ children }: { children: React.ReactNode }) {
	const hasClerkConfig = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);

	useEffect(() => {
		if (!hasClerkConfig) {
			setAccessTokenProvider(null);
		}
	}, [hasClerkConfig]);

	if (!hasClerkConfig) {
		return <SessionContext.Provider value={DEFAULT_CONTEXT}>{children}</SessionContext.Provider>;
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
