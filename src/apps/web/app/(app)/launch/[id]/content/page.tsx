"use client";

import { useParams } from "next/navigation";

import LaunchSection from "@/components/launch/LaunchSection";
import { ContentView } from "@/components/launch/Views";
import type { ContentBundle } from "@/packages/types";

export default function LaunchContentPage() {
	const { id } = useParams<{ id: string }>();
	return (
		<LaunchSection launchId={id} waitingFor="Content Generation">
			{(launch) => {
				const content = launch.brief.content as ContentBundle | undefined;
				return content ? <ContentView content={content} /> : null;
			}}
		</LaunchSection>
	);
}
