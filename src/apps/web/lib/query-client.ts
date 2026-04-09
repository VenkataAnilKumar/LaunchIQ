import { QueryClient } from "@tanstack/react-query";

function createQueryClient(): QueryClient {
	return new QueryClient({
		defaultOptions: {
			queries: {
				staleTime: 30_000,
				retry: 1,
				refetchOnWindowFocus: false,
			},
		},
	});
}

let browserClient: QueryClient | undefined;

export function getQueryClient(): QueryClient {
	if (typeof window === "undefined") {
		return createQueryClient();
	}

	if (!browserClient) {
		browserClient = createQueryClient();
	}

	return browserClient;
}