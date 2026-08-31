"""Shared AWS clients and helpers.

Authentication is intentionally delegated to the standard AWS credential chain:
EC2/ECS/Lambda role -> environment -> shared AWS config. Do not hard-code keys.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache

import boto3
from dotenv import load_dotenv

load_dotenv()


@lru_cache(maxsize=1)
def region() -> str:
    return os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-east-1"


@lru_cache(maxsize=1)
def bedrock_runtime():
    return boto3.client("bedrock-runtime", region_name=region())


@lru_cache(maxsize=1)
def secrets_manager():
    return boto3.client("secretsmanager", region_name=region())


@lru_cache(maxsize=1)
def load_db_secret() -> dict:
    """Return database connection settings from Secrets Manager when configured."""
    arn = os.getenv("DB_SECRET_ARN")
    if not arn:
        return {}
    response = secrets_manager().get_secret_value(SecretId=arn)
    return json.loads(response["SecretString"])
