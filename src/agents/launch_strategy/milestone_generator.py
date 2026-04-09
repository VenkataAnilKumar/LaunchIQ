"""Milestone generation helper."""
from __future__ import annotations


class MilestoneGenerator:
	def generate_milestones(self, phases: list[dict]) -> list[dict]:
		milestones: list[dict] = []
		for phase in phases:
			milestones.append(
				{
					"phase": phase.get("phase"),
					"milestone": f"Complete {phase.get('phase')} goals",
				}
			)
		return milestones

