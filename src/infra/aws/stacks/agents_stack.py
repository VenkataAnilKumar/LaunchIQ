from __future__ import annotations

from aws_cdk import Stack
from constructs import Construct

from src.infra.aws.constructs.agent_lambda import AgentLambdaConstruct


class AgentsStack(Stack):
	AGENTS = [
		"orchestrator",
		"market_intelligence",
		"audience_insight",
		"launch_strategy",
		"content_generation",
		"analytics_feedback",
	]

	def __init__(
		self,
		scope: Construct,
		construct_id: str,
		*,
		database_url: str,
		redis_url: str,
		environment: str = "staging",
		**kwargs: object,
	) -> None:
		super().__init__(scope, construct_id, **kwargs)

		for agent_id in self.AGENTS:
			AgentLambdaConstruct(
				self,
				f"{agent_id}-lambda",
				agent_id=agent_id,
				env_name=environment,
				environment_vars={
					"DATABASE_URL": database_url,
					"REDIS_URL": redis_url,
					"ANTHROPIC_API_KEY": "{{resolve:secretsmanager:launchiq/anthropic-api-key}}",
				},
			)

