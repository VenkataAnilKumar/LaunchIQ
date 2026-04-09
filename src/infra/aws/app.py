from __future__ import annotations

import aws_cdk as cdk

from src.infra.aws.stacks.agents_stack import AgentsStack
from src.infra.aws.stacks.api_stack import ApiStack
from src.infra.aws.stacks.data_stack import DataStack
from src.infra.aws.stacks.secrets_stack import SecretsStack


app = cdk.App()

env_name = app.node.try_get_context("env") or "staging"

secrets_stack = SecretsStack(app, f"LaunchIQ-Secrets-{env_name}")
data_stack = DataStack(app, f"LaunchIQ-Data-{env_name}")

api_stack = ApiStack(
	app,
	f"LaunchIQ-Api-{env_name}",
	vpc=data_stack.vpc,
	database_url_secret=secrets_stack.database_url_secret,
	anthropic_secret=secrets_stack.anthropic_secret,
	redis_endpoint=data_stack.redis.attr_redis_endpoint_address,
	environment=env_name,
)

agents_stack = AgentsStack(
	app,
	f"LaunchIQ-Agents-{env_name}",
	database_url="{{resolve:secretsmanager:launchiq/database-url}}",
	redis_url=f"redis://{data_stack.redis.attr_redis_endpoint_address}:6379/0",
	environment=env_name,
)

api_stack.add_dependency(secrets_stack)
api_stack.add_dependency(data_stack)
agents_stack.add_dependency(secrets_stack)
agents_stack.add_dependency(data_stack)

app.synth()

