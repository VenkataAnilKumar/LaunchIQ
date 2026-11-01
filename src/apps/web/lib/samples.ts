export interface SampleBrief {
	label: string;
	product_name: string;
	description: string;
	target_market: string;
	competitors: string[];
}

/** One-click example briefs so a first-time visitor gets value without writing anything. */
export const SAMPLE_BRIEFS: SampleBrief[] = [
	{
		label: "B2B SaaS",
		product_name: "Zephyr",
		description: "An AI assistant that plans product launches for small B2B teams: market research, personas, strategy and content in one workflow.",
		target_market: "B2B SaaS startups",
		competitors: ["Acme Launch", "LaunchLite"],
	},
	{
		label: "Consumer app",
		product_name: "Tempo",
		description: "Consumer fitness app with adaptive training plans that adjust to sleep, soreness and schedule.",
		target_market: "Health-conscious mobile users",
		competitors: ["Nike Run Club", "Strava", "Centr"],
	},
	{
		label: "Developer tool",
		product_name: "ShipMate CLI",
		description: "Developer tool for release automation and changelog generation straight from your commit history.",
		target_market: "Engineering teams and DevOps leads",
		competitors: ["semantic-release", "release-please", "Changesets"],
	},
	{
		label: "Hardware",
		product_name: "Lumo",
		description: "A smart desk lamp that adapts colour temperature to the time of day and your calendar.",
		target_market: "Remote workers and home-office enthusiasts",
		competitors: ["Philips Hue", "BenQ ScreenBar"],
	},
	{
		label: "Fintech",
		product_name: "Ledgerly",
		description: "Automated bookkeeping for freelancers with tax-ready exports.",
		target_market: "Freelancers and solo consultants in the US",
		competitors: ["QuickBooks", "Wave", "FreshBooks"],
	},
];
