"""Main python file_key for adding resources to the application stack."""
from typing import Dict, Any
import aws_cdk
# import aws_cdk.aws_kms as kms
import aws_cdk.aws_lambda as _lambda
import aws_cdk.aws_dynamodb as dynamodb
from constructs import Construct

from .iam_construct import IAMConstruct
from .kms_construct import KMSConstruct
from .lambda_construct import LambdaConstruct


class MainProjectStack(aws_cdk.Stack):
    """Build the app stacks and its resources."""
    def __init__(self, env_var: str, scope: Construct, 
                 app_id: str, config: dict, **kwargs: Dict[str, Any]) -> None:
        """Creates the cloudformation templates for the projects."""
        super().__init__(scope, app_id, **kwargs)
        self.env_var = env_var
        self.config = config
        MainProjectStack.create_stack(self, self.env_var, config=config)

    @staticmethod
    def create_stack(stack: aws_cdk.Stack, env: str, config: dict) -> None:
        """Create and add the resources to the application stack"""

        print(env)
        # DynamoDB infra setup ------------------------------------------------------
        dynamodb.Table(
            stack,
            id='apigateway-crud',
            table_name='product-inventory',
            partition_key=dynamodb.Attribute(
                name='productid',
                type=dynamodb.AttributeType.STRING
            )
        )

        # KMS infra setup ------------------------------------------------------
        kms_pol_doc = IAMConstruct.get_kms_policy_document()

        kms_key = KMSConstruct.create_kms_key(
            stack=stack,
            config=config,
            policy_doc=kms_pol_doc
        )
        print(kms_key)

        # Infra for Lambda function creation -------------------------------------
        MainProjectStack.create_lambda_functions(
            stack=stack,
            config=config,
            # env=env,
            # kms_key=kms_key,
            # layers=layer
        )

    @staticmethod
    def create_lambda_functions(
            stack: aws_cdk.Stack,
            config: dict) -> Dict[str, _lambda.Function]:
        """Create placeholder lambda function and roles."""

        lambdas = {}

        # Placeholder Lambda. ----------------------------------------------------
        placeholder_policy = IAMConstruct.create_managed_policy(
            stack=stack,
            config=config,
            policy_name="placeholder",
            statements=[
                LambdaConstruct.get_cloudwatch_policy(
                    config['global']['placeholder_lambdaLogsArn']
                ),
                LambdaConstruct.get_dynamodb_policy()
            ]
        )

        placeholder_role = IAMConstruct.create_role(
            stack=stack,
            config=config,
            role_name="placeholder",
            assumed_by=["lambda"]   
        )

        placeholder_role.add_managed_policy(placeholder_policy)

        lambdas["placeholder_lambda"] = LambdaConstruct.create_lambda(
            stack=stack,
            config=config,
            lambda_name="placeholder_lambda",
            role=placeholder_role,
            # layer=[layers["pandas"]],
            memory_size=3008,
        )