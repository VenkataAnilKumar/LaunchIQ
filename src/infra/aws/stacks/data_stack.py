from __future__ import annotations

from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticache as elasticache
from aws_cdk import aws_rds as rds
from constructs import Construct


class DataStack(Stack):
	def __init__(self, scope: Construct, construct_id: str, **kwargs: object) -> None:
		super().__init__(scope, construct_id, **kwargs)

		self.vpc = ec2.Vpc(
			self,
			"LaunchIQVpc",
			max_azs=2,
			nat_gateways=1,
			subnet_configuration=[
				ec2.SubnetConfiguration(name="public", subnet_type=ec2.SubnetType.PUBLIC),
				ec2.SubnetConfiguration(name="private", subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
			],
		)

		self.db_sg = ec2.SecurityGroup(self, "DbSecurityGroup", vpc=self.vpc)
		self.redis_sg = ec2.SecurityGroup(self, "RedisSecurityGroup", vpc=self.vpc)

		self.database = rds.DatabaseInstance(
			self,
			"LaunchIQPostgres",
			engine=rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_16_2),
			vpc=self.vpc,
			vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
			instance_type=ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MICRO),
			security_groups=[self.db_sg],
			credentials=rds.Credentials.from_generated_secret("postgres"),
			allocated_storage=20,
			multi_az=False,
			publicly_accessible=False,
			database_name="launchiq",
		)

		private_subnets = self.vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)
		redis_subnet_group = elasticache.CfnSubnetGroup(
			self,
			"RedisSubnetGroup",
			description="Subnet group for LaunchIQ Redis",
			subnet_ids=private_subnets.subnet_ids,
		)

		self.redis = elasticache.CfnCacheCluster(
			self,
			"LaunchIQRedis",
			cache_node_type="cache.t3.micro",
			num_cache_nodes=1,
			engine="redis",
			vpc_security_group_ids=[self.redis_sg.security_group_id],
			cache_subnet_group_name=redis_subnet_group.ref,
		)

		CfnOutput(self, "VpcId", value=self.vpc.vpc_id)
		CfnOutput(self, "DbEndpoint", value=self.database.db_instance_endpoint_address)
		CfnOutput(self, "RedisEndpoint", value=self.redis.attr_redis_endpoint_address)

