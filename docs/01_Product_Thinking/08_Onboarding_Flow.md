# Onboarding Flow & User Journey Map
## LaunchIQ — AI-Powered Product Launch Intelligence Platform

**Version:** 1.0
**Author:** Venkata Anil Kumar
**Date:** 2026-04-09

---

## 1. Onboarding Philosophy

LaunchIQ's onboarding is designed around one goal: **deliver the first "wow" moment in under 10 minutes.**

The "wow" moment is the first completed Launch Intelligence Brief — when the user sees AI-generated competitive research and audience personas tailored to their product, and realizes this would have taken them weeks to build manually.

**Design principles:**
- Minimize friction to first value — every extra step loses a user
- Agent activity should be visible and exciting — not a black box spinner
- HITL checkpoints are the onboarding, not obstacles to it
- First session should end with something actionable, not just impressive

---

## 2. Full User Journey Map

### Stage 1 — Awareness
**Touchpoints:** Product Hunt, LinkedIn, HN, Twitter, Indie Hackers
**User state:** Frustrated with manual launch prep, curious about AI automation
**Goal:** Land on waitlist / sign up page

```
Discovery → Landing Page → Email Signup (waitlist) OR Direct Trial
```

---

### Stage 2 — Signup & Activation (0–10 minutes)

```
Step 1: SIGN UP
────────────────
User arrives at launchiq.io
→ Sees headline: "Your AI launch team. First strategy in 10 minutes."
→ Clicks "Try Free" or "Start Your Launch"
→ OAuth signup (Google / GitHub) via Clerk
→ Redirected to onboarding flow

                    ↓

Step 2: PRODUCT INTAKE FORM
────────────────────────────
Screen: "Tell us about your product" (4 fields)
→ Product name: [text input]
→ What does it do? (plain English, 1–3 sentences): [textarea]
→ Who is it for? (target customer): [text input]
→ Any known competitors? (optional): [text input]
→ What's your launch goal? [dropdown: awareness / signups / sales / waitlist]

"This is all the agents need. You can add more detail later."
→ [Start Launch Intelligence] button

                    ↓

Step 3: AGENT PIPELINE ACTIVATES
──────────────────────────────────
Screen: Live agent activity view
→ "Orchestrator is planning your launch..."
→ Progress bar activates
→ "Market Intelligence Agent is researching your market..."
→ Live streaming: competitor cards appearing one by one
→ "Found 5 competitors. Analyzing positioning gaps..."
→ Estimated time remaining shown (< 90 seconds)

                    ↓

Step 4: HITL CHECKPOINT 1 — Market Brief Review
─────────────────────────────────────────────────
Screen: "Here's what we found about your market"
→ 4–6 competitor cards with: name, positioning, strengths, weakness vs. your product
→ 5–8 trend signals with source links
→ Market opportunity summary paragraph

User actions:
  [✓ Looks good, continue] → proceeds
  [Edit] → user can modify competitor list or add new ones
  [Regenerate] → re-runs Market Intelligence Agent

                    ↓

Step 5: AUDIENCE INSIGHT AGENT
────────────────────────────────
Screen: "Building your buyer personas..."
→ Agent streams 3 persona cards in real-time
→ Each card: Persona name, role, company size, pain points, JTBD, messaging angle

HITL Checkpoint 2:
→ User can rename personas, edit pain points
→ [Approve Personas] to continue

                    ↓

Step 6: LAUNCH STRATEGY AGENT
───────────────────────────────
Screen: "Generating your launch strategy..."
→ 3-phase GTM plan streaming in
→ Pre-launch (weeks + actions) → Launch Day → Post-launch

HITL Checkpoint 3:
→ User adjusts timeline if needed
→ [Approve Strategy] to continue

                    ↓

Step 7: CONTENT GENERATION (optional at end of onboarding)
────────────────────────────────────────────────────────────
Screen: "Want launch copy too? We'll write it now."
→ [Yes, generate content] → Content Agent runs (120 seconds)
→ [Skip for now] → Goes to dashboard

                    ↓

Step 8: LAUNCH DASHBOARD
──────────────────────────
Screen: Full launch dashboard
→ Brief | Strategy | Personas | Content (if generated) | Execution Tracker
→ "Your first launch is ready. Here's what to do next."
→ Top 3 recommended next actions highlighted

Celebration moment: "You just did in 10 minutes what takes most teams 2 weeks."
→ Share button: "Built with LaunchIQ" (optional viral loop)
```

---

### Stage 3 — Activation (Days 1–7)

**Goal:** User completes full launch workflow and starts execution tracker

```
Day 1: First brief complete → Email: "Your launch brief is ready"
Day 2: Content generation nudge (if skipped)
Day 3: "Add your launch date to unlock the execution tracker"
Day 5: "Connect Slack to get launch alerts on your team"
Day 7: NPS survey (in-app) + "How was your first launch brief?"
```

**Activation metric:** User completes full flow (brief → strategy → content) within 7 days

---

### Stage 4 — Engagement (Weeks 2–4)

**Goal:** Second launch created, integrations connected, habit formed

```
Week 2: "Ready for your next launch? Start a new one."
Week 3: HubSpot integration prompt (if PMM persona detected)
Week 4: "Your Market Intelligence is 30 days old — refresh it for free"
```

---

### Stage 5 — Retention & Expansion

**Goal:** Convert to paid, invite team members, become power user

```
Trial limit approaching: "You've used 4 of 5 free launch briefs"
→ Upgrade prompt with value reminder: "You've saved ~15 hours of research"

Team invite: "Working with a team? Invite them to collaborate on launches"
→ Triggers Team plan upgrade conversation
```

---

## 3. Onboarding Screen Flow (Wireframe Description)

```
[Signup] → [Intake Form] → [Agent Pipeline View] → [HITL: Brief] → [HITL: Personas]
    → [HITL: Strategy] → [Optional: Content Gen] → [Dashboard]
```

**Screen count:** 7–8 screens (lean — each screen has one clear action)
**Time to first value:** < 10 minutes
**Drop-off optimization:** Progress bar always visible; skip options at every HITL step

---

## 4. Empty State Design

Each section has a helpful empty state that explains what the agent will generate:

| Section | Empty State Message |
|---------|-------------------|
| Market Brief | "Your Market Intelligence Agent will research competitors and trends tailored to your product." |
| Personas | "Your Audience Insight Agent will build buyer personas based on your market brief." |
| Strategy | "Your Launch Strategy Agent will create a phased GTM plan based on your personas." |
| Content | "Your Content Agent will write launch copy aligned to your strategy and personas." |
| Tracker | "Your execution checklist will appear here once your strategy is approved." |

---

## 5. Key Onboarding Metrics

| Metric | Target |
|--------|--------|
| Signup to first brief completion | > 60% |
| Time to first brief | < 10 minutes |
| HITL checkpoint approval rate | > 85% (users not abandoning at checkpoints) |
| Day 7 retention | > 50% |
| Trial-to-paid conversion (Day 14) | > 15% |
| NPS (end of onboarding) | > 40 |
