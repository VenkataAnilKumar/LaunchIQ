"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import PersonaCard from "@/components/launch/PersonaCard";
import AgentPending from "@/components/ui/AgentPending";
import { getLaunch } from "@/lib/api";
import type { Persona } from "@/packages/types";

export default function LaunchPersonasPage() {
	const params = useParams<{ id: string }>();
	const [personas, setPersonas] = useState<Persona[]>([]);

	useEffect(() => {
		void getLaunch(params.id).then((launch) => {
			setPersonas((launch.brief.personas as Persona[] | undefined) ?? []);
		});
	}, [params.id]);

	if (personas.length === 0) {
		return <AgentPending agentName="Audience Insight" />;
	}

	return (
		<section style={{ display: "grid", gap: "0.8rem", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))" }}>
			{personas.map((persona, index) => (
				<PersonaCard isPrimary={index === 0} key={`${persona.name}-${index}`} persona={persona} />
			))}
		</section>
	);
}
