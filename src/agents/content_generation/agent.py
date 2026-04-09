"""Content Generation worker agent."""
from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path
from typing import Any, AsyncIterator

from pydantic import BaseModel

from src.agents._base.base_agent import AgentConfig, AgentResult, BaseAgent

from .brand_voice import BrandVoiceExtractor
from .schemas import ContentBundle


def _load_prompt(name: str) -> str:
	path = Path(__file__).parent / "prompts" / name
	return path.read_text(encoding="utf-8") if path.exists() else ""


class ContentGenerationAgent(BaseAgent):
	def __init__(self) -> None:
		super().__init__(
			AgentConfig(
				agent_id="content_generation",
				model="claude-sonnet-4-6",
				system_prompt=_load_prompt("system.md"),
			)
		)
		self._brand_voice = BrandVoiceExtractor()

	def get_output_schema(self) -> type[BaseModel]:
		return ContentBundle

	async def run(self, payload: dict[str, Any]) -> AgentResult:
		prior = payload.get("prior_outputs", {}) or {}
		strategy = prior.get("launch_strategy", {})
		personas = prior.get("audience_insight", {})
		brand_voice = self._brand_voice.extract(strategy)

		email_sequence, social_posts, ad_copy = await asyncio.gather(
			self._generate_email_sequence(strategy, personas),
			self._generate_social_posts(strategy, personas),
			self._generate_ad_copy(strategy, personas),
		)

		bundle = {
			"email_sequence": email_sequence,
			"social_posts": social_posts,
			"ad_copy": ad_copy,
			"brand_voice_notes": json.dumps(brand_voice),
		}
		validated = self._validate_output(bundle)
		return AgentResult(agent_id=self.config.agent_id, output=validated)

	async def stream(self, payload: dict[str, Any]) -> AsyncIterator[str]:
		result = await self.run(payload)
		yield json.dumps(result.output)

	async def _generate_email_sequence(
		self,
		strategy: dict[str, Any],
		personas: dict[str, Any],
	) -> list[dict[str, Any]]:
		return await self._generate_items(
			prompt_name="email.md",
			instruction="Generate 3-5 email items with format='email'.",
			strategy=strategy,
			personas=personas,
			max_tokens=2048,
		)

	async def _generate_social_posts(
		self,
		strategy: dict[str, Any],
		personas: dict[str, Any],
	) -> list[dict[str, Any]]:
		return await self._generate_items(
			prompt_name="social.md",
			instruction="Generate 3-10 social posts with format linkedin/twitter.",
			strategy=strategy,
			personas=personas,
			max_tokens=2048,
		)

	async def _generate_ad_copy(
		self,
		strategy: dict[str, Any],
		personas: dict[str, Any],
	) -> list[dict[str, Any]]:
		return await self._generate_items(
			prompt_name="ads.md",
			instruction="Generate 2-4 ad copy items with format='ad_copy'.",
			strategy=strategy,
			personas=personas,
			max_tokens=2048,
		)

	async def _generate_items(
		self,
		prompt_name: str,
		instruction: str,
		strategy: dict[str, Any],
		personas: dict[str, Any],
		max_tokens: int,
	) -> list[dict[str, Any]]:
		user_msg = (
			f"{instruction}\n"
			f"strategy: {json.dumps(strategy)}\n"
			f"personas: {json.dumps(personas)}\n"
			f"guide:\n{_load_prompt(prompt_name)}\n"
			"Return JSON object with key 'items' containing a list."
		)
		messages = self._build_messages(user_msg)
		params = self._make_api_params(messages)
		params["max_tokens"] = max_tokens
		response = self.client.messages.create(**params)
		text_parts = [b.text for b in response.content if getattr(b, "type", "") == "text"]
		payload = self._extract_json("".join(text_parts))
		items = payload.get("items", []) if isinstance(payload, dict) else []
		if not isinstance(items, list):
			raise ValueError("Content generation expected list in 'items'")
		return items

	def _extract_json(self, text: str) -> dict[str, Any]:
		fenced = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
		raw = fenced.group(1) if fenced else text.strip()
		if not raw.startswith("{"):
			match = re.search(r"(\{.*\})", raw, re.DOTALL)
			if match:
				raw = match.group(1)
		return json.loads(raw)

