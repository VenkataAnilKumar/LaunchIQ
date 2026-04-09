"""Base abstractions for LaunchIQ MCP tool executors."""
from __future__ import annotations

import abc
from typing import Any

from pydantic import BaseModel, ValidationError


class BaseMCPServer(abc.ABC):
	"""Abstract base class for tool executors with schema validation."""

	@abc.abstractmethod
	async def execute(self, tool_name: str, inputs: dict[str, Any]) -> dict[str, Any]:
		...

	def validate(self, schema: type[BaseModel], inputs: dict[str, Any]) -> BaseModel:
		"""Validate tool inputs against a Pydantic schema class."""
		try:
			return schema(**inputs)
		except ValidationError as exc:
			raise ValueError(f"Invalid tool input: {exc}") from exc

