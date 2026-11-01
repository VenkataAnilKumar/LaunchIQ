"use client";

import { useParams } from "next/navigation";

import LaunchSection from "@/components/launch/LaunchSection";
import { PersonasView } from "@/components/launch/Views";
import type { Persona } from "@/packages/types";

export default function LaunchPersonasPage() {
	const { id } = useParams<{ id: string }>();
	return (
		<LaunchSection launchId={id} waitingFor="Audience Insight">
			{(launch) => {
				const personas = launch.brief.personas as Persona[] | undefined;
				return personas?.length ? <PersonasView personas={personas} /> : null;
			}}
		</LaunchSection>
	);
}
