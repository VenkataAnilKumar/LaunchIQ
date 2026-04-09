import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

const hasClerkConfig = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);

const isProtectedRoute = createRouteMatcher([
	"/dashboard(.*)",
	"/launch(.*)",
	"/settings(.*)",
	"/api/v1(.*)",
]);

export default clerkMiddleware(async (auth, req) => {
	if (!hasClerkConfig) {
		return;
	}

	if (isProtectedRoute(req)) {
		await auth.protect();
	}
});

export const config = {
	matcher: [
		"/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
		"/(api|trpc)(.*)",
	],
};
