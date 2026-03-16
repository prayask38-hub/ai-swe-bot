from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROK_API_KEY"))

def test_connection():
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": "Say: AI SWE Bot is online and ready."}
        ]
    )
    print(response.choices[0].message.content)

test_connection()