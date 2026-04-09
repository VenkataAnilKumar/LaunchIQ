from __future__ import annotations

from aws_cdk import Duration, RemovalPolicy
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_logs as logs
from constructs import Construct


class MCPServerConstruct(Construct):
	def __init__(
		self,
		scope: Construct,
		construct_id: str,
		*,
		server_id: str,
		handler_path: str,
		environment_vars: dict[str, str],
		timeout_seconds: int = 60,
	) -> None:
		super().__init__(scope, construct_id)

		role = iam.Role(
			self,
			f"{server_id}-role",
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
			f"{server_id}-fn",
			function_name=f"launchiq-mcp-{server_id}",
			runtime=lambda_.Runtime.PYTHON_3_12,
			handler=handler_path,
			code=lambda_.Code.from_asset("src"),
			timeout=Duration.seconds(timeout_seconds),
			memory_size=512,
			role=role,
			environment=environment_vars,
		)

		self.log_group = logs.LogGroup(
			self,
			f"{server_id}-logs",
			log_group_name=f"/aws/lambda/launchiq-mcp-{server_id}",
			retention=logs.RetentionDays.ONE_MONTH,
			removal_policy=RemovalPolicy.DESTROY,
		)

