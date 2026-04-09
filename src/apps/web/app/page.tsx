import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";

export default async function HomePage() {
	if (!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY) {
		redirect("/sign-in");
	}

	const { userId } = await auth();
	redirect(userId ? "/dashboard" : "/sign-in");
}