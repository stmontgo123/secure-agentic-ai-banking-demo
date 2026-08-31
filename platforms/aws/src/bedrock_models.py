"""Amazon Bedrock generation and embedding helpers."""

from __future__ import annotations

import json
import os

from botocore.exceptions import ClientError
from dotenv import load_dotenv

from aws_clients import bedrock_runtime

load_dotenv()


def generate_text(prompt: str) -> str:
    """Generate grounded text with Amazon Bedrock Converse API."""
    model_id = os.getenv("BEDROCK_GEN_MODEL", "amazon.nova-lite-v1:0")
    try:
        response = bedrock_runtime().converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={
                "maxTokens": 900,
                "temperature": 0.1,
                "topP": 0.9,
            },
        )
    except ClientError as exc:
        raise RuntimeError(
            f"Bedrock generation failed for model {model_id}: {exc}"
        ) from exc

    blocks = response["output"]["message"]["content"]
    return "".join(block.get("text", "") for block in blocks).strip()


def embed_text(text: str) -> list[float]:
    """Create an embedding with Amazon Titan Text Embeddings V2."""
    model_id = os.getenv("BEDROCK_EMBED_MODEL", "amazon.titan-embed-text-v2:0")
    dimensions = int(os.getenv("EMBED_DIMENSIONS", "1024"))

    body = json.dumps(
        {
            "inputText": text,
            "dimensions": dimensions,
            "normalize": True,
        }
    )

    try:
        response = bedrock_runtime().invoke_model(
            modelId=model_id,
            body=body,
            accept="application/json",
            contentType="application/json",
        )
    except ClientError as exc:
        raise RuntimeError(
            f"Bedrock embedding failed for model {model_id}: {exc}"
        ) from exc

    payload = json.loads(response["body"].read())
    vector = payload["embedding"]
    if len(vector) != dimensions:
        raise RuntimeError(
            f"Expected {dimensions} embedding dimensions, got {len(vector)}"
        )
    return vector
