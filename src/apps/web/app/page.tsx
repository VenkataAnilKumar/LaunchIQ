import { auth } from "@clerk/nextjs/server";
import Link from "next/link";
import { ArrowRight, Bot, Gauge, Rocket, ShieldCheck, Sparkles, Target, WandSparkles } from "lucide-react";
import { redirect } from "next/navigation";

const proofPoints = [
	{ label: "Time To First Brief", value: "< 10 min", tone: "green" },
	{ label: "Specialized Agents", value: "6", tone: "amber" },
	{ label: "Eval-Gated CI", value: "Enabled", tone: "green" },
	{ label: "External Tool Servers", value: "5", tone: "amber" },
];

const features = [
	{
		title: "Market Signal Engine",
		description: "Transform raw product ideas into competitive context, positioning threats, and opportunity windows.",
		icon: Target,
	},
	{
		title: "Sequential Strategy Intelligence",
		description: "Agent-to-agent handoffs preserve context so persona logic, GTM planning, and content stay coherent.",
		icon: Bot,
	},
	{
		title: "Structural Human Review",
		description: "Hard workflow gates force review at pivotal decisions before downstream generation proceeds.",
		icon: ShieldCheck,
	},
	{
		title: "Parallel Launch Velocity",
		description: "Generate campaign artifacts across channels simultaneously without losing strategic thread.",
		icon: Rocket,
	},
	{
		title: "Live Pipeline Telemetry",
		description: "Monitor state transitions, token spend, and decision checkpoints in one streaming surface.",
		icon: Gauge,
	},
	{
		title: "Quality Locked In CI",
		description: "Automated eval baselines catch regressions before prompt or workflow changes hit production.",
		icon: Sparkles,
	},
];

const flowSteps = [
	"Product intake + category context",
	"Market intelligence + competitor map",
	"Audience narratives + message hooks",
	"Phased GTM + milestone strategy",
	"Channel-ready content + variants",
];

export default async function HomePage() {
	const hasClerk = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);

	if (hasClerk) {
		const { userId } = await auth();
		if (userId) {
			redirect("/dashboard");
		}
	}

	return (
		<main className="page-shell lq-landing" style={{ paddingTop: "1rem" }}>
			<section className="panel lq-hero-panel">
				<div className="lq-hero-grid">
					<div className="lq-reveal-up">
						<div className="lq-badge">
							<WandSparkles size={14} />
							2026 Agentic Launch Platform
						</div>
						<h1 className="lq-hero-title">Build launch strategy, not launch chaos.</h1>
						<p className="lq-hero-subtitle">
							LaunchIQ turns one product prompt into market intelligence, audience strategy, GTM planning, and channel-ready
							content with a human-controlled multi-agent pipeline.
						</p>
						<div className="lq-hero-cta-row">
							<Link className="btn btn-primary" href={hasClerk ? "/sign-up" : "/dashboard"}>
								Launch New Brief <ArrowRight size={16} style={{ marginLeft: "0.35rem", verticalAlign: "text-top" }} />
							</Link>
							{hasClerk ? (
								<Link className="btn btn-secondary" href="/sign-in">
									Sign In
								</Link>
							) : (
								<Link className="btn btn-secondary" href="/dashboard">
									Open Dashboard
								</Link>
							)}
						</div>
					</div>

					<div className="lq-terminal lq-reveal-up lq-delay-1">
						<div className="lq-terminal-head">
							<div className="lq-dots">
								<span />
								<span />
								<span />
							</div>
							<span>launchiq-runtime</span>
						</div>
						<div className="lq-terminal-body">
							<p>$ orchestration start --pipeline launch</p>
							<p>✓ market_intelligence ............... complete</p>
							<p>✓ audience_insight ................... complete</p>
							<p>⚡ hitl_checkpoint.strategy ........... approved</p>
							<p>✓ content_generation ................. complete</p>
							<p>✓ analytics_feedback ................. complete</p>
							<p className="lq-terminal-highlight">→ launch package ready in 03:47</p>
						</div>
					</div>
				</div>

				<div className="lq-proof-grid lq-reveal-up lq-delay-2">
					{proofPoints.map((point) => (
						<div key={point.label} className="lq-proof-card" data-tone={point.tone}>
							<div className="lq-proof-value">{point.value}</div>
							<div className="lq-proof-label">{point.label}</div>
						</div>
					))}
				</div>
			</section>

			<section className="lq-section-gap">
				<div className="lq-section-head">
					<p>Capabilities</p>
					<h2>Purpose-built agents for each launch decision layer</h2>
				</div>
				<div className="lq-feature-grid">
					{features.map((feature, index) => {
						const Icon = feature.icon;
						return (
							<article key={feature.title} className="panel lq-feature-card lq-reveal-up" style={{ animationDelay: `${0.08 * index}s` }}>
								<div className="lq-feature-icon">
									<Icon size={16} />
								</div>
								<h3>{feature.title}</h3>
								<p>{feature.description}</p>
							</article>
						);
					})}
				</div>
			</section>

			<section className="panel lq-flow-panel lq-section-gap">
				<div className="lq-section-head" style={{ marginBottom: "0.7rem" }}>
					<p>Pipeline</p>
					<h2>One input. Five strategic layers. One coherent launch package.</h2>
				</div>
				<div className="lq-flow-grid">
					{flowSteps.map((step, index) => (
						<div key={step} className="lq-flow-step">
							<div className="lq-flow-index">0{index + 1}</div>
							<div>{step}</div>
						</div>
					))}
				</div>
			</section>
		</main>
	);
}