"""Minimal local Ollama generation + embedding check."""

import os
import requests
from dotenv import load_dotenv

load_dotenv()
base = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")

r = requests.post(
    f"{base}/api/generate",
    json={"model": os.getenv("GEN_MODEL", "qwen2.5:3b"), "prompt": "Reply with: model ready", "stream": False},
    timeout=120,
)
r.raise_for_status()
print("Generation:", r.json()["response"].strip())

r = requests.post(
    f"{base}/api/embed",
    json={"model": os.getenv("EMBED_MODEL", "nomic-embed-text"), "input": "bank policy"},
    timeout=120,
)
r.raise_for_status()
print("Embedding dimensions:", len(r.json()["embeddings"][0]))
