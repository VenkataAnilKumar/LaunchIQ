from __future__ import annotations

from aws_cdk import Duration, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_secretsmanager as secretsmanager
from constructs import Construct


class ApiStack(Stack):
	def __init__(
		self,
		scope: Construct,
		construct_id: str,
		*,
		vpc: ec2.IVpc,
		database_url_secret: secretsmanager.ISecret,
		anthropic_secret: secretsmanager.ISecret,
		redis_endpoint: str,
		environment: str = "staging",
		**kwargs: object,
	) -> None:
		super().__init__(scope, construct_id, **kwargs)

		cluster = ecs.Cluster(self, "LaunchIQCluster", vpc=vpc, cluster_name=f"launchiq-{environment}")

		task_image_options = ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
			image=ecs.ContainerImage.from_asset(".", file="src/infra/docker/api.Dockerfile"),
			container_port=8000,
			environment={
				"APP_ENV": environment,
				"REDIS_URL": f"redis://{redis_endpoint}:6379/0",
			},
			secrets={
				"DATABASE_URL": ecs.Secret.from_secrets_manager(database_url_secret),
				"ANTHROPIC_API_KEY": ecs.Secret.from_secrets_manager(anthropic_secret),
			},
		)

		self.service = ecs_patterns.ApplicationLoadBalancedFargateService(
			self,
			"LaunchIQApiService",
			cluster=cluster,
			service_name=f"launchiq-api-{environment}",
			task_image_options=task_image_options,
			cpu=512,
			memory_limit_mib=1024,
			desired_count=1,
			public_load_balancer=True,
			redirect_http=True,
		)

		scaling = self.service.service.auto_scale_task_count(min_capacity=1, max_capacity=4)
		scaling.scale_on_cpu_utilization(
			"CpuAutoScaling",
			target_utilization_percent=70,
			scale_in_cooldown=Duration.seconds(120),
			scale_out_cooldown=Duration.seconds(60),
		)

