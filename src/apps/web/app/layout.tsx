import type { Metadata } from "next";
import { Space_Grotesk, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";

import { Providers } from "./providers";

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

const ibmPlexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-mono",
  display: "swap",
});

const BASE_URL = process.env.NEXT_PUBLIC_APP_URL ?? "https://launchiq.io";

export const metadata: Metadata = {
  metadataBase: new URL(BASE_URL),
  title: {
    default: "LaunchIQ — AI-Powered Product Launch Intelligence",
    template: "%s · LaunchIQ",
  },
  description:
    "Turn one product prompt into market intelligence, audience strategy, GTM planning, and channel-ready content — with a human-controlled multi-agent AI pipeline.",
  keywords: [
    "AI product launch",
    "go-to-market strategy",
    "multi-agent AI",
    "launch intelligence",
    "GTM automation",
    "Claude agents",
  ],
  authors: [{ name: "Venkata Anil Kumar" }],
  openGraph: {
    type: "website",
    siteName: "LaunchIQ",
    title: "LaunchIQ — AI-Powered Product Launch Intelligence",
    description:
      "6 AI agents. One product prompt. Complete launch playbook in under 10 minutes.",
    url: BASE_URL,
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "LaunchIQ — AI-Powered Product Launch Intelligence",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "LaunchIQ — AI-Powered Product Launch Intelligence",
    description:
      "6 AI agents. One product prompt. Complete launch playbook in under 10 minutes.",
    images: ["/og-image.png"],
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${spaceGrotesk.variable} ${ibmPlexMono.variable}`}>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
