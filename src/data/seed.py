from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEMO_DIR = ROOT / "src" / "data" / "demo"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.apps.api.models.launch import LaunchStatus
from src.memory.structured.database import AsyncSessionLocal
from src.memory.structured.repositories.agent_repo import AgentRepository
from src.memory.structured.repositories.launch_repo import LaunchRepository
from src.packages.config.models import PIPELINE_SEQUENCE


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _demo_strategy(product_name: str) -> dict[str, Any]:
    return {
        "positioning_statement": f"{product_name} helps teams launch with speed and confidence.",
        "launch_date_recommendation": "Target Tuesday launch with two-week prelaunch runway",
        "phases": [
            {
                "phase": "Pre-Launch",
                "duration": "2 weeks",
                "goals": ["Build audience", "Validate message"],
                "tactics": ["Waitlist campaign", "Founder narrative", "Teaser email"],
                "kpis": ["Waitlist signups", "CTR", "Email replies"],
            },
            {
                "phase": "Launch Week",
                "duration": "1 week",
                "goals": ["Drive qualified traffic", "Convert trials"],
                "tactics": ["Launch announcement", "Demo webinar", "Partner amplification"],
                "kpis": ["Sessions", "Trials", "Demo bookings"],
            },
            {
                "phase": "Post-Launch",
                "duration": "2 weeks",
                "goals": ["Improve activation", "Collect insight"],
                "tactics": ["Customer stories", "Retargeting", "Feedback loop"],
                "kpis": ["Activation", "CAC", "Pipeline influenced"],
            },
        ],
        "channels": ["LinkedIn", "Email", "Webinars", "Communities"],
        "budget_allocation": {"paid": "35%", "content": "25%", "events": "20%", "experiments": "20%"},
        "success_metrics": ["Qualified pipeline", "Activation rate", "Cost per activated account"],
        "risks": ["Message dilution", "Insufficient follow-up sequencing"],
    }


def _demo_content(product_name: str) -> dict[str, Any]:
    return {
        "email_sequence": [
            {
                "format": "email",
                "variant": "a",
                "headline": f"Launch faster with {product_name}",
                "body": "Turn launch planning from weeks into days with guided AI workflows.",
                "cta": "Book a demo",
                "target_persona": "Product marketer",
            },
            {
                "format": "email",
                "variant": "b",
                "headline": "Your AI launch team is ready",
                "body": "Research, strategy, and content in one connected system.",
                "cta": "Start trial",
                "target_persona": "Founder",
            },
            {
                "format": "email",
                "variant": "a",
                "headline": "Ship launches with confidence",
                "body": "Keep quality high with human approvals at every critical checkpoint.",
                "cta": "See workflow",
                "target_persona": "Growth lead",
            },
        ],
        "social_posts": [
            {
                "format": "linkedin",
                "variant": "a",
                "headline": "Launch planning is too fragmented",
                "body": "Use one workflow to move from research to launch content.",
                "cta": "Learn more",
                "target_persona": "Product marketer",
            },
            {
                "format": "twitter",
                "variant": "b",
                "headline": "Launch smarter",
                "body": "Connect insight, strategy, and content with AI + HITL controls.",
                "cta": "Try it",
                "target_persona": "Founder",
            },
            {
                "format": "linkedin",
                "variant": "a",
                "headline": "Faster GTM execution",
                "body": "From product brief to execution-ready campaign outputs in minutes.",
                "cta": "Book demo",
                "target_persona": "Growth lead",
            },
        ],
        "ad_copy": [
            {
                "format": "ad_copy",
                "variant": "a",
                "headline": "Launch in days, not weeks",
                "body": "AI-assisted launch strategy and content for modern teams.",
                "cta": "Start free",
                "target_persona": "Product marketer",
            },
            {
                "format": "ad_copy",
                "variant": "b",
                "headline": "Better GTM outcomes",
                "body": "Plan and execute launches faster with integrated intelligence.",
                "cta": "Request demo",
                "target_persona": "Founder",
            },
        ],
        "brand_voice_notes": "Confident, practical, and outcomes-focused.",
    }


async def seed_demo(user_id: str) -> str:
    launch_input = _load_json(DEMO_DIR / "demo_launch.json")
    market_output = _load_json(DEMO_DIR / "demo_market_output.json")
    persona_output = _load_json(DEMO_DIR / "demo_personas.json")

    strategy_output = _demo_strategy(launch_input["product_name"])
    content_output = _demo_content(launch_input["product_name"])

    brief_output: dict[str, Any] = {
        "market_intelligence": market_output,
        "audience_insight": persona_output,
        "launch_strategy": strategy_output,
        "content_generation": content_output,
    }

    async with AsyncSessionLocal() as db:
        launch_repo = LaunchRepository(db)
        agent_repo = AgentRepository(db)

        launch = await launch_repo.create(user_id=user_id, data=launch_input)

        for agent_id in PIPELINE_SEQUENCE:
            await agent_repo.create(launch_id=launch.launch_id, agent_id=agent_id)

        await launch_repo.save_brief_output(launch.launch_id, brief_output)
        await launch_repo.update_status(launch.launch_id, LaunchStatus.COMPLETED)

        for agent_id in PIPELINE_SEQUENCE:
            output = brief_output.get(agent_id, {})
            await agent_repo.set_completed(
                launch_id=launch.launch_id,
                agent_id=agent_id,
                output=output,
                tokens_used=1024,
            )

        return launch.launch_id


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed LaunchIQ data")
    parser.add_argument("--demo", action="store_true", help="Seed demo launch and precomputed outputs")
    parser.add_argument("--user-id", default="demo-user", help="User id to own seeded data")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.demo:
        print("Only --demo is currently implemented.")
        raise SystemExit(1)

    import asyncio

    launch_id = asyncio.run(seed_demo(args.user_id))
    print(f"Demo launch seeded successfully: {launch_id}")


if __name__ == "__main__":
    main()
