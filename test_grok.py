# test_groq.py
from dotenv import load_dotenv
from litellm import completion
import os

load_dotenv()

response = completion(
    model="groq/llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    messages=[{"role": "user", "content": "Say hello in one sentence."}]
)

print(response.choices[0].message.content)