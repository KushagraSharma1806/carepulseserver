import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.api_base = "https://openrouter.ai/api/v1"

try:
    response = openai.ChatCompletion.create(
        model="mistralai/mistral-7b-instruct",
        messages=[
            {"role": "system", "content": "You're a helpful assistant."},
            {"role": "user", "content": "I have a fever and sore throat."}
        ],
    )
    print("✅ Response:")
    print(response["choices"][0]["message"]["content"])

except Exception as e:
    import traceback
    print("❌ Error:")
    traceback.print_exc()
