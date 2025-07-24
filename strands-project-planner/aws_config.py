import os
from dotenv import load_dotenv, find_dotenv
from strands.models import BedrockModel

def load_env():
    """Load environment variables from .env file"""
    _ = load_dotenv(find_dotenv())

def get_aws_bedrock_model(model_name="claude-4-sonnet"):
    """Get configured AWS Bedrock model"""
    load_env()
    
    # Model mappings
    model_mapping = {
        "claude-3-sonnet": "anthropic.claude-3-sonnet-20240229-v1:0",
        "claude-3.5-sonnet": "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "claude-4-sonnet": "us.anthropic.claude-sonnet-4-20250514-v1:0",
        "nova-pro": "us.amazon.nova-pro-v1:0"
    }
    
    model_id = model_mapping.get(model_name, model_mapping["claude-4-sonnet"])
    
    return BedrockModel(
        model_id=model_id,
        region_name=os.getenv("AWS_REGION", "us-east-1")
    )

def get_aws_credentials():
    """Get AWS credentials from environment"""
    load_env()
    return {
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "aws_region": os.getenv("AWS_REGION", "us-east-1")
    } 