"""Minimal Amazon Bedrock connectivity/model-access test."""

from bedrock_models import embed_text, generate_text

vector = embed_text("bank card verification policy")
print("Embedding dimensions:", len(vector))

text = generate_text(
    "Reply with exactly this sentence: Amazon Bedrock connectivity is working."
)
print("Generation response:", text)

print("SUCCESS: Amazon Bedrock calls completed.")
