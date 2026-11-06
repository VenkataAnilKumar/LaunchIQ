# Hiring managers and investors

Background material for people evaluating the project. It is kept out of the main README on purpose.

## For Hiring Managers

This project demonstrates end-to-end production proficiency across:

**AI Engineering**
Multi-agent orchestration · Resumable human-in-the-loop workflows · Tool-use loops (ReAct) with validate-and-repair retries · Prompt-injection defences · Source grounding · Offline eval gate with adversarial cases · Cost budgets · Deterministic fake-model testing

**Backend Engineering**
FastAPI async architecture · SQLAlchemy 2.x async · Celery distributed tasks · Redis pub/sub · JWT auth middleware · Rate limiting · PII scrubbing pipeline · SSE streaming · Pydantic v2 validation

**Frontend Engineering**
Next.js 15 App Router · React 19 · TanStack Query v5 + Zustand · Authenticated live streaming with `fetch` · Forms generated from JSON Schema · Accessible, responsive custom design system · Playwright browser tests

**DevOps & Cloud**
GitHub Actions CI with lint, type-check, tests and an eval gate · Alembic migrations (verified on SQLite) · Keyless local stack · AWS CDK stacks and Dockerfiles (designed, not deployed) · Sentry

**Product Thinking**
Full PRD · Competitive analysis · GTM strategy · User research · Business model canvas — demonstrating product judgment alongside engineering skill

> Portfolio documentation: [`docs/portfolio/`](../portfolio/) | [`docs/`]()


## For Investors

> The figures below are planning estimates from the business docs, not measurements. No live run with a real model has been recorded yet.

**Market** — product management and launch tooling; sizing and growth figures are in the business docs and have not been independently verified. The gap LaunchIQ targets: no tool connects research → strategy → content in one reviewed pipeline.

**Moat (planned)** — eval baselines and, later, brand-voice memory from past launches. Neither a live baseline nor brand-voice learning exists yet.

**Unit economics (estimate)** — a cheaper model for analytics, a mid-tier model for research and content, and the top tier only for strategy. A cost-per-launch estimate of ~$0.40 and a target price of $49–199/month are assumptions to validate; the app already records tokens and estimated cost per launch to measure it.

**Architecture** — designed to deploy one function per agent on AWS so that compute scales with usage; today everything runs in one API and worker process.

> Full business model: [Business Model Canvas](../01_Product_Thinking/06_Business_Model_Canvas.md)

---

<div align="center">

---

**Built with the Anthropic Claude SDK · Designed for AWS · 2026**

<br/>

If LaunchIQ solves a problem you care about —<br/>as a customer, investor, co-founder, or hiring manager:

<br/>

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/venkataanilkumar)
[![Email](https://img.shields.io/badge/Email-Get%20In%20Touch-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:vanilkumarch@gmail.com)
[![Portfolio](https://img.shields.io/badge/Portfolio-View%20Case%20Study-6366f1?style=for-the-badge)](../portfolio/03_Case_Study.md)

<br/>

<sub>Made with care by **Venkata Anil Kumar** · © 2026 LaunchIQ · MIT License</sub>

</div>
