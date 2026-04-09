from __future__ import annotations

from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_secretsmanager as secretsmanager
from constructs import Construct


class SecretsStack(Stack):
	def __init__(self, scope: Construct, construct_id: str, **kwargs: object) -> None:
		super().__init__(scope, construct_id, **kwargs)

		self.anthropic_secret = secretsmanager.Secret(
			self,
			"AnthropicApiKey",
			secret_name="launchiq/anthropic-api-key",
		)
		self.tavily_secret = secretsmanager.Secret(
			self,
			"TavilyApiKey",
			secret_name="launchiq/tavily-api-key",
		)
		self.clerk_secret = secretsmanager.Secret(
			self,
			"ClerkSecretKey",
			secret_name="launchiq/clerk-secret-key",
		)
		self.database_url_secret = secretsmanager.Secret(
			self,
			"DatabaseUrl",
			secret_name="launchiq/database-url",
		)

		CfnOutput(self, "AnthropicSecretArn", value=self.anthropic_secret.secret_arn)
		CfnOutput(self, "TavilySecretArn", value=self.tavily_secret.secret_arn)
		CfnOutput(self, "ClerkSecretArn", value=self.clerk_secret.secret_arn)
		CfnOutput(self, "DatabaseUrlSecretArn", value=self.database_url_secret.secret_arn)

