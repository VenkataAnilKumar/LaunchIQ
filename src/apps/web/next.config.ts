import type { NextConfig } from "next";

const config: NextConfig = {
	experimental: {
		ppr: process.env.NEXT_ENABLE_PPR === "1",
		reactCompiler: process.env.NEXT_ENABLE_REACT_COMPILER === "1",
		typedRoutes: true,
	} as NonNullable<NextConfig["experimental"]>,
	async rewrites() {
		const apiUrl = process.env.API_URL ?? "http://localhost:8000";
		return [
			{
				source: "/api/v1/:path*",
				destination: `${apiUrl}/api/v1/:path*`,
			},
		];
	},
};

export default config;
