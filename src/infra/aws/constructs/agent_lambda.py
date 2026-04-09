from __future__ import annotations

from typing import Any

from aws_cdk import Duration, RemovalPolicy
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_logs as logs
from constructs import Construct


class AgentLambdaConstruct(Construct):
	def __init__(
		self,
		scope: Construct,
		construct_id: str,
		*,
		agent_id: str,
		environment_vars: dict[str, str],
		env_name: str = "dev",
		memory_size: int = 1024,
		timeout_seconds: int = 300,
	) -> None:
		super().__init__(scope, construct_id)

		role = iam.Role(
			self,
			f"{agent_id}-role",
			assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
			managed_policies=[
				iam.ManagedPolicy.from_aws_managed_policy_name(
					"service-role/AWSLambdaBasicExecutionRole"
				)
			],
		)
		role.add_to_policy(
			iam.PolicyStatement(
				actions=["secretsmanager:GetSecretValue"],
				resources=["*"],
			)
		)

		self.function = lambda_.Function(
			self,
			f"{agent_id}-fn",
			function_name=f"launchiq-{agent_id}",
			runtime=lambda_.Runtime.PYTHON_3_12,
			handler=f"src.agents.{agent_id}.handler.handler",
			code=lambda_.Code.from_asset("src/agents"),
			timeout=Duration.seconds(timeout_seconds),
			memory_size=memory_size,
			role=role,
			environment={**environment_vars, "APP_ENV": env_name},
		)

		self.log_group = logs.LogGroup(
			self,
			f"{agent_id}-logs",
			log_group_name=f"/aws/lambda/launchiq-{agent_id}",
			retention=logs.RetentionDays.ONE_MONTH,
			removal_policy=RemovalPolicy.DESTROY,
		)

