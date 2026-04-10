import { ImageResponse } from "next/og";

export const runtime = "edge";
export const alt = "LaunchIQ — AI-Powered Product Launch Intelligence";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OGImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          background: "linear-gradient(135deg, #0e1f14 0%, #142118 50%, #0a1a10 100%)",
          fontFamily: "system-ui, sans-serif",
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* Background glow orbs */}
        <div
          style={{
            position: "absolute",
            top: -120,
            right: -80,
            width: 480,
            height: 480,
            borderRadius: "50%",
            background: "radial-gradient(circle, rgba(31,143,78,0.22) 0%, transparent 70%)",
          }}
        />
        <div
          style={{
            position: "absolute",
            bottom: -100,
            left: -60,
            width: 380,
            height: 380,
            borderRadius: "50%",
            background: "radial-gradient(circle, rgba(188,138,10,0.18) 0%, transparent 70%)",
          }}
        />

        {/* Badge */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            border: "1px solid rgba(31,143,78,0.4)",
            borderRadius: 999,
            background: "rgba(31,143,78,0.12)",
            padding: "8px 20px",
            marginBottom: 32,
            fontSize: 16,
            fontWeight: 700,
            color: "#62e799",
            letterSpacing: "0.04em",
          }}
        >
          2026 Agentic Launch Platform
        </div>

        {/* Wordmark */}
        <div
          style={{
            fontSize: 96,
            fontWeight: 800,
            color: "#f0faf2",
            letterSpacing: "-0.03em",
            lineHeight: 1,
            marginBottom: 20,
          }}
        >
          LaunchIQ
        </div>

        {/* Tagline */}
        <div
          style={{
            fontSize: 28,
            color: "rgba(228,242,231,0.7)",
            fontWeight: 400,
            maxWidth: 680,
            textAlign: "center",
            lineHeight: 1.4,
            marginBottom: 48,
          }}
        >
          6 AI agents. One product prompt.
          Complete launch playbook in under 10 minutes.
        </div>

        {/* Agent pills row */}
        <div style={{ display: "flex", gap: 12 }}>
          {[
            "Orchestrator",
            "Market Intel",
            "Audience",
            "Strategy",
            "Content",
            "Analytics",
          ].map((name) => (
            <div
              key={name}
              style={{
                background: "rgba(31,143,78,0.14)",
                border: "1px solid rgba(31,143,78,0.3)",
                borderRadius: 8,
                padding: "8px 16px",
                fontSize: 15,
                fontWeight: 600,
                color: "#a3f0be",
              }}
            >
              {name}
            </div>
          ))}
        </div>

        {/* URL watermark */}
        <div
          style={{
            position: "absolute",
            bottom: 28,
            right: 40,
            fontSize: 16,
            color: "rgba(228,242,231,0.3)",
            letterSpacing: "0.02em",
          }}
        >
          launchiq.io
        </div>
      </div>
    ),
    { ...size }
  );
}
