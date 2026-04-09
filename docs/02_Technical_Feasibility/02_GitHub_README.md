# LaunchIQ

**AI-Powered Product Launch Intelligence Platform**

> From product idea to full launch strategy in under 10 minutes — powered by autonomous AI agents.

---

## The Problem

Marketing teams and founders spend weeks manually researching competitors, defining audiences, planning launch campaigns, and writing content — only to miss the optimal launch window or misalign messaging with market reality.

## The Solution

LaunchIQ is a multi-agent AI platform that autonomously:
- Researches your market and competitors
- Generates audience personas with messaging angles
- Creates a phased go-to-market strategy
- Writes launch copy (email, social, ads)
- Tracks execution and optimizes based on performance

---

## Key Features

| Feature | Description |
|---------|-------------|
| Market Intelligence Agent | Real-time competitor and trend research |
| Audience Insight Agent | AI-generated buyer personas with messaging |
| Launch Strategy Generator | Phased GTM plan with milestones |
| Content Generation Agent | Email, social, ad copy — strategy-aware |
| Analytics & Feedback Agent | Performance tracking + optimization |
| Human-in-the-Loop | Approve and edit at every major step |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, React 19, Tailwind CSS, shadcn/ui |
| Backend | FastAPI (Python 3.12), Celery, Redis |
| AI / Agents | Claude Opus 4.6, Sonnet 4.6, Haiku 4.5 |
| Agent SDK | Claude Agent SDK |
| Database | PostgreSQL (Supabase), Qdrant (vectors) |
| Auth | Clerk |
| Observability | LangSmith, Langfuse, Sentry, PostHog |
| Infrastructure | Vercel (frontend), AWS Lambda (agents) |

---

## Architecture

```
User Input → Orchestrator Agent → [Market | Audience | Strategy | Content | Analytics] Agents
                    ↓                              ↓
             Memory Layer                    Tool Registry (MCP)
          (Redis + Qdrant + PG)        (Search, HubSpot, Slack, GA4)
                    ↓
             Observability (LangSmith + Langfuse)
```

---

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js 20+
- Docker (for local services)
- Anthropic API key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/launchiq.git
cd launchiq

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Add your API keys

# Frontend setup
cd ../frontend
npm install
cp .env.example .env.local

# Start local services
docker-compose up -d  # PostgreSQL + Redis + Qdrant

# Run backend
uvicorn main:app --reload

# Run frontend
npm run dev
```

### Environment Variables

```env
ANTHROPIC_API_KEY=your_key_here
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
QDRANT_URL=http://localhost:6333
REDIS_URL=redis://localhost:6379
CLERK_SECRET_KEY=your_clerk_key
TAVILY_API_KEY=your_tavily_key
LANGSMITH_API_KEY=your_langsmith_key
```

---

## Project Structure

```
launchiq/
├── backend/
│   ├── agents/           # Agent definitions
│   │   ├── orchestrator.py
│   │   ├── market_intelligence.py
│   │   ├── audience_insight.py
│   │   ├── launch_strategy.py
│   │   ├── content_generation.py
│   │   └── analytics_feedback.py
│   ├── api/              # FastAPI routes
│   ├── memory/           # Memory layer (Redis, Qdrant, PG)
│   ├── tools/            # MCP tool definitions
│   └── main.py
├── frontend/
│   ├── app/              # Next.js App Router pages
│   ├── components/       # React components
│   └── lib/              # Utilities
├── docs/                 # Product documentation
├── docker-compose.yml
└── README.md
```

---

## Roadmap

- [x] Core agent architecture
- [x] Market Intelligence Agent
- [x] Audience Insight Agent
- [ ] Content Generation Agent
- [ ] Analytics & Feedback Agent
- [ ] Slack Integration
- [ ] HubSpot Integration
- [ ] GA4 Integration
- [ ] Public Beta

---

## Contributing

Contributions are welcome. Please open an issue first to discuss what you'd like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Author

**Venkata Anil Kumar**
AI Engineer | Building LaunchIQ
