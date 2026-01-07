# for testing purposes

import openai
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL

openai.api_key = OPENROUTER_API_KEY
openai.api_base = OPENROUTER_BASE_URL

try:
    print("Testing OpenRouter connection...")
    response = openai.ChatCompletion.create(
        model="xiaomi/mimo-v2-flash:free",
        messages=[{"role": "user", "content": "explain what is a react hook ?"}],
        max_tokens=10
    )
    print("✅ Connection successful!")
    print(f"Response: {response.choices[0].message.content}") # type: ignore
except Exception as e:
    print(f"❌ Connection failed: {e}")