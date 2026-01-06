from openai import OpenAI
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL
)

try:
    models = client.models.list()

    mimo_models = [
        model.id for model in models.data
        if "mimo" in model.id.lower()
    ]

    print("Available MiMo models:")
    for m in mimo_models:
        print(f"  {m}")

except Exception as e:
    print(f"Error: {e}")
