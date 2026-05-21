import openai
from app.core.database import SessionLocal
from app.models.note import Note
from app.core.config import settings

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_summary(text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes text."},
            {"role": "user", "content": f"Summarize the following markdown note in 1-2 sentences:\n\n{text}"}
        ],
        max_tokens=100
    )
    return response.choices[0].message.content.strip()

def generate_tags(text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that extracts up to 5 relevant tags from text. Return only the tags separated by commas, no other text."},
            {"role": "user", "content": f"Generate tags for this note:\n\n{text}"}
        ],
        max_tokens=50
    )
    return response.choices[0].message.content.strip()

