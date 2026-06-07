# llm.py  (at project root for now, we'll move it into src/ next)
import os
import time
from litellm import completion
from litellm.exceptions import RateLimitError
from dotenv import load_dotenv

load_dotenv()

MODELS = {
    "ranker":   "groq/llama-3.1-8b-instant",
    "curator":  "groq/llama-3.1-8b-instant",
    "fetcher":  "groq/llama-3.1-8b-instant",
    "notebook": "groq/llama-3.3-70b-versatile",
    "quiz":     "groq/llama-3.3-70b-versatile",
    "notifier": "groq/llama-3.1-8b-instant",
}


def call_llm(agent: str, prompt: str, system: str = "", max_retries: int = 5) -> str:
    model = MODELS[agent]
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    for attempt in range(max_retries):
        try:
            response = completion(
                model=model,
                api_key=os.getenv("GROQ_API_KEY"),
                messages=messages,
                max_tokens=500,
            )
            return response.choices[0].message.content
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt + 3)