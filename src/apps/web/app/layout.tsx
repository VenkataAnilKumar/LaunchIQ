import type { Metadata } from "next";
import "./globals.css";

import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "LaunchIQ",
  description: "AI-assisted launch operations dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
			<Providers>{children}</Providers>
		</body>
    </html>
  );
}
