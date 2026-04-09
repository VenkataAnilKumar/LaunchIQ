export default function AgentPending({ agentName }: { agentName: string }) {
	return (
		<section className="panel" style={{ textAlign: "center", padding: "2rem 1rem" }}>
			<h2 style={{ marginTop: 0 }}>Waiting For {agentName}</h2>
			<p style={{ color: "var(--muted)", marginBottom: 0 }}>
				This section will populate once the corresponding agent completes and its output is approved.
			</p>
		</section>
	);
}