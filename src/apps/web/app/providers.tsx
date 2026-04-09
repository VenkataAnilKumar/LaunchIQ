"use client";

import { ClerkProvider } from "@clerk/nextjs";
import { QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { Toaster } from "sonner";

import { SessionProvider } from "@/components/auth/SessionProvider";
import { getQueryClient } from "@/lib/query-client";

export function Providers({ children }: { children: React.ReactNode }) {
	const queryClient = getQueryClient();
	const publishableKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;

	const content = (
		<SessionProvider>
			<QueryClientProvider client={queryClient}>
				{children}
				<Toaster position="top-right" richColors />
				{process.env.NODE_ENV === "development" ? <ReactQueryDevtools initialIsOpen={false} /> : null}
			</QueryClientProvider>
		</SessionProvider>
	);

	if (!publishableKey) {
		return content;
	}

	return (
		<ClerkProvider publishableKey={publishableKey}>
			{content}
		</ClerkProvider>
	);
}
