import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise SystemExit("GEMINI_API_KEY is missing. Add it to .env.")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    contents="Reply as Radha in one short sentence: Hello, are you free to talk?",
)

print(response.text)
