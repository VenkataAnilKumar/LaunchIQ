"""Global registry for MCP tools and their executors."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ToolEntry:
	name: str
	executor: Any
	schema: dict[str, Any]


class ToolRegistry:
	def __init__(self) -> None:
		self._tools: dict[str, ToolEntry] = {}

	def register(self, name: str, executor: Any, schema: dict[str, Any]) -> None:
		self._tools[name] = ToolEntry(name=name, executor=executor, schema=schema)

	def get(self, name: str) -> ToolEntry | None:
		return self._tools.get(name)

	def list_all(self) -> list[str]:
		return sorted(self._tools.keys())


REGISTRY = ToolRegistry()

