import type { Config } from "tailwindcss";

const config: Config = {
	content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
	theme: {
		extend: {
			colors: {
				brand: {
					primary: "oklch(0.55 0.22 264)",
					secondary: "oklch(0.66 0.16 210)",
					accent: "oklch(0.72 0.16 145)",
				},
			},
		},
	},
};

export default config;
